"""
RAG Controller (Business Logic)
Handles retrieval-augmented generation using LangChain and pgvector
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from app.models.database import DocumentChunk, Document, Venue
from app.controllers.document_processor import DocumentProcessorController
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class RAGController:
    """Controller for RAG pipeline"""

    def __init__(self, db: Session):
        """
        Initialize RAG controller.

        Args:
            db: Database session for performing database operations.
        """
        self.db = db
        self.doc_processor = DocumentProcessorController()

        self.llm = None
        if settings.GEMINI_API_KEY:
            self.llm = ChatGoogleGenerativeAI(
                model=settings.GEMINI_MODEL,
                temperature=settings.GEMINI_TEMPERATURE,
                google_api_key=settings.GEMINI_API_KEY,
                convert_system_message_to_human=True
            )

    def retrieve_relevant_chunks(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant document chunks using vector similarity search.

        Performs semantic search on document chunks using pgvector and cosine distance
        to find the most relevant chunks for a given query.

        Args:
            query: Query text to search for.
            top_k: Number of chunks to retrieve. Defaults to 5.
            filters: Optional metadata filters for constraining search results.

        Returns:
            List of relevant chunks with metadata including chunk text, document title,
            venue name, and relevance score.
        """
        try:
            query_embedding = self.doc_processor.generate_embedding(query)

            embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'

            sql_query = text(f"""
                SELECT
                    dc.id,
                    dc.document_id,
                    dc.venue_id,
                    dc.chunk_text,
                    dc.chunk_index,
                    dc.metadata,
                    d.title as document_title,
                    v.name as venue_name,
                    (1 - (dc.embedding <=> '{embedding_str}'::vector)) as similarity
                FROM document_chunks dc
                JOIN documents d ON dc.document_id = d.id
                JOIN venues v ON dc.venue_id = v.id
                ORDER BY dc.embedding <=> '{embedding_str}'::vector
                LIMIT :top_k
            """)

            result = self.db.execute(
                sql_query,
                {"top_k": top_k}
            )

            chunks = []
            for row in result:
                chunk_data = {
                    "chunk_id": row.id,
                    "document_id": row.document_id,
                    "venue_id": row.venue_id,
                    "chunk_text": row.chunk_text,
                    "chunk_index": row.chunk_index,
                    "metadata": row.metadata or {},
                    "document_title": row.document_title,
                    "venue_name": row.venue_name,
                    "relevance_score": float(row.similarity)
                }
                chunks.append(chunk_data)

            logger.info(f"Retrieved {len(chunks)} chunks for query")
            return chunks

        except Exception as e:
            logger.error(f"Error retrieving chunks: {str(e)}")
            return []

    def generate_answer(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> str:
        """
        Generate answer using LLM based on retrieved chunks.

        Creates a contextualized prompt from retrieved chunks and uses the configured
        LLM to generate a natural language answer. Falls back to concatenated chunks
        if no LLM is available.

        Args:
            query: User query to answer.
            retrieved_chunks: Retrieved context chunks with venue and document information.

        Returns:
            Generated answer as a string. Returns fallback answer if LLM is unavailable.
        """
        if not self.llm:
            logger.warning("No LLM API key configured, returning concatenated chunks")
            return self._fallback_answer(retrieved_chunks)

        try:
            context_parts = []
            for chunk in retrieved_chunks:
                venue_name = chunk.get("venue_name", "Unknown")
                doc_title = chunk.get("document_title", "Unknown")
                chunk_text = chunk.get("chunk_text", "")
                context_parts.append(
                    f"[Venue: {venue_name} | Document: {doc_title}]\n{chunk_text}"
                )

            context = "\n\n---\n\n".join(context_parts)

            prompt_template = ChatPromptTemplate.from_messages([
                ("system", """You are a helpful assistant for TeloHive, a venue matching platform.
Your job is to answer questions about venues based on the provided context.

Guidelines:
- Answer based ONLY on the provided context
- If the context doesn't contain enough information, say so
- Be specific and cite venue names when relevant
- Keep answers concise and actionable
- If multiple venues match, list them clearly"""),
                ("user", """Context:
{context}

Question: {question}

Answer:""")
            ])

            chain = prompt_template | self.llm
            response = chain.invoke({
                "context": context,
                "question": query
            })

            return response.content

        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return self._fallback_answer(retrieved_chunks)

    def _fallback_answer(self, retrieved_chunks: List[Dict[str, Any]]) -> str:
        """
        Generate fallback answer when LLM is not available.

        Concatenates the top 3 retrieved chunks with venue names to create a basic
        answer without requiring an LLM service.

        Args:
            retrieved_chunks: Retrieved chunks with venue and text information.

        Returns:
            Concatenated answer from chunks, or a message indicating no relevant information found.
        """
        if not retrieved_chunks:
            return "No relevant information found to answer your question."

        answer_parts = ["Based on the available information:\n"]
        for i, chunk in enumerate(retrieved_chunks[:3], 1):
            venue_name = chunk.get("venue_name", "Unknown")
            chunk_text = chunk.get("chunk_text", "")
            answer_parts.append(f"{i}. {venue_name}: {chunk_text}")

        return "\n\n".join(answer_parts)

    def query(
        self,
        question: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a complete RAG query pipeline.

        Orchestrates the retrieval of relevant chunks and generation of an answer,
        returning both the answer and source information for transparency.

        Args:
            question: User question to answer.
            top_k: Number of chunks to retrieve. Defaults to 5.
            filters: Optional metadata filters for constraining search results.

        Returns:
            Dictionary containing:
                - answer: Generated answer string
                - sources: List of source chunks with metadata
                - metadata: Query metadata including chunk count and LLM usage
        """
        chunks = self.retrieve_relevant_chunks(question, top_k, filters)

        if not chunks:
            return {
                "answer": "I couldn't find any relevant information to answer your question.",
                "sources": []
            }

        answer = self.generate_answer(question, chunks)

        sources = [
            {
                "chunk_id": chunk["chunk_id"],
                "document_id": chunk["document_id"],
                "document_title": chunk["document_title"],
                "venue_id": chunk["venue_id"],
                "venue_name": chunk["venue_name"],
                "chunk_text": chunk["chunk_text"],
                "relevance_score": chunk["relevance_score"]
            }
            for chunk in chunks
        ]

        return {
            "answer": answer,
            "sources": sources,
            "metadata": {
                "chunks_retrieved": len(chunks),
                "llm_used": self.llm is not None
            }
        }
