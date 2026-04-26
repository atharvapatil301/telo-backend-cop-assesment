"""
Document Processor Controller.

Handles document chunking and embedding generation using sentence transformers.
"""
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import hashlib
from app.config import settings


class DocumentProcessorController:
    """Controller for processing documents into chunks with embeddings."""

    def __init__(self):
        """Initialize document processor with embedding model and text splitter."""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)

    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks for processing.

        Args:
            text: Input text to chunk

        Returns:
            List of text chunks
        """
        chunks = self.text_splitter.split_text(text)
        return chunks

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate vector embedding for text using sentence transformers.

        Args:
            text: Input text

        Returns:
            Embedding vector as list of floats
        """
        embedding = self.embedding_model.encode(text)
        return embedding.tolist()

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts using batch processing.

        Args:
            texts: List of input texts

        Returns:
            List of embedding vectors
        """
        embeddings = self.embedding_model.encode(texts, batch_size=32, show_progress_bar=False)
        return [emb.tolist() for emb in embeddings]

    def process_document(
        self,
        document_id: str,
        venue_id: str,
        content: str,
        metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Process a document into chunks with embeddings.

        Args:
            document_id: Document identifier
            venue_id: Venue identifier
            content: Document content
            metadata: Additional metadata

        Returns:
            List of chunk dictionaries with embeddings
        """
        chunks = self.chunk_text(content)
        embeddings = self.generate_embeddings_batch(chunks)

        processed_chunks = []
        for idx, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_data = {
                "document_id": document_id,
                "venue_id": venue_id,
                "chunk_text": chunk_text,
                "chunk_index": idx,
                "embedding": embedding,
                "metadata": metadata or {}
            }
            processed_chunks.append(chunk_data)

        return processed_chunks

    def create_query_hash(self, query: str, filters: Dict[str, Any] = None) -> str:
        """
        Create SHA256 hash for query caching.

        Args:
            query: Query text
            filters: Optional filters

        Returns:
            Hash string
        """
        cache_key = f"{query.lower().strip()}"
        if filters:
            cache_key += f"_{str(sorted(filters.items()))}"

        return hashlib.sha256(cache_key.encode()).hexdigest()

    def enrich_chunk_metadata(
        self,
        chunk_data: Dict[str, Any],
        venue_data: Dict[str, Any],
        document_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enrich chunk metadata with venue and document information.

        Args:
            chunk_data: Chunk data
            venue_data: Venue data
            document_data: Document data

        Returns:
            Enriched chunk data
        """
        enriched_metadata = chunk_data.get("metadata", {})
        enriched_metadata.update({
            "venue_name": venue_data.get("name"),
            "venue_type": venue_data.get("venue_type"),
            "city": venue_data.get("city"),
            "neighborhood": venue_data.get("neighborhood"),
            "document_title": document_data.get("title"),
            "doc_type": document_data.get("doc_type", "text")
        })
        chunk_data["metadata"] = enriched_metadata
        return chunk_data
