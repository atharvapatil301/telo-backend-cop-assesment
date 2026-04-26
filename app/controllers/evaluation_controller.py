"""
Evaluation Controller (Business Logic)
Implements LLM-as-a-Judge for RAG quality evaluation
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from app.models.database import EvaluationResult
from app.config import settings
import logging
import json
from sqlalchemy import func

logger = logging.getLogger(__name__)


class EvaluationController:
    """Controller for evaluating RAG responses using LLM-as-a-Judge"""

    def __init__(self, db: Session):
        """
        Initialize evaluation controller.

        Args:
            db: Database session for storing evaluation results.
        """
        self.db = db

        self.judge_llm = None
        if settings.GEMINI_API_KEY:
            self.judge_llm = ChatGoogleGenerativeAI(
                model=settings.GEMINI_MODEL,
                temperature=settings.GEMINI_TEMPERATURE,
                google_api_key=settings.GEMINI_API_KEY,
                convert_system_message_to_human=True
            )

    def evaluate_relevance(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> float:
        """
        Evaluate relevance of retrieved chunks to the original query.

        Uses LLM-as-a-Judge to score how relevant the retrieved chunks are
        to answering the user's query.

        Args:
            query: Original user query.
            retrieved_chunks: Retrieved context chunks to evaluate.

        Returns:
            Relevance score as float between 0.0 and 1.0.
        """
        if not self.judge_llm or not retrieved_chunks:
            return 0.0

        try:
            chunks_text = "\n\n".join([
                f"Chunk {i+1}: {chunk.get('chunk_text', '')}"
                for i, chunk in enumerate(retrieved_chunks)
            ])

            prompt_template = ChatPromptTemplate.from_messages([
                ("system", """You are an evaluation judge. Your task is to evaluate the relevance of retrieved information to a query.

Score the relevance on a scale of 0-1 where:
- 1.0: Highly relevant, directly answers the query
- 0.7-0.9: Mostly relevant, contains useful information
- 0.4-0.6: Partially relevant, some related information
- 0.1-0.3: Minimally relevant, tangentially related
- 0.0: Not relevant at all

Respond with ONLY a JSON object in this format:
{{"score": 0.85, "reasoning": "explanation here"}}"""),
                ("user", """Query: {query}

Retrieved Chunks:
{chunks}

Evaluate the relevance:""")
            ])

            chain = prompt_template | self.judge_llm
            response = chain.invoke({
                "query": query,
                "chunks": chunks_text
            })

            content = response.content.strip()

            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            logger.info(f"Relevance response: {content[:200]}")
            result = json.loads(content)
            return float(result.get("score", 0.0))

        except Exception as e:
            logger.error(f"Error evaluating relevance: {str(e)}")
            return 0.5

    def evaluate_faithfulness(
        self,
        answer: str,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> float:
        """
        Evaluate faithfulness (groundedness) of answer to retrieved context.

        Uses LLM-as-a-Judge to score how well the generated answer is grounded
        in the provided context without hallucination.

        Args:
            answer: Generated answer to evaluate.
            retrieved_chunks: Retrieved context chunks that ground the answer.

        Returns:
            Faithfulness score as float between 0.0 and 1.0.
        """
        if not self.judge_llm or not retrieved_chunks:
            return 0.0

        try:
            context = "\n\n".join([
                chunk.get('chunk_text', '')
                for chunk in retrieved_chunks
            ])

            prompt_template = ChatPromptTemplate.from_messages([
                ("system", """You are an evaluation judge. Your task is to evaluate if an answer is faithful (grounded) in the provided context.

An answer is faithful if:
- All claims are supported by the context
- No hallucinated information
- No contradictions with the context

Score faithfulness on a scale of 0-1 where:
- 1.0: Completely faithful, all claims supported
- 0.7-0.9: Mostly faithful, minor unsupported details
- 0.4-0.6: Partially faithful, some unsupported claims
- 0.1-0.3: Minimally faithful, major unsupported claims
- 0.0: Not faithful, hallucinated or contradictory

Respond with ONLY a JSON object in this format:
{{"score": 0.90, "reasoning": "explanation here"}}"""),
                ("user", """Context:
{context}

Answer:
{answer}

Evaluate faithfulness:""")
            ])

            chain = prompt_template | self.judge_llm
            response = chain.invoke({
                "context": context,
                "answer": answer
            })

            content = response.content.strip()

            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            logger.info(f"Faithfulness response: {content[:200]}")
            result = json.loads(content)
            return float(result.get("score", 0.0))

        except Exception as e:
            logger.error(f"Error evaluating faithfulness: {str(e)}")
            return 0.5

    def evaluate_response(
        self,
        query: str,
        answer: str,
        retrieved_chunks: List[Dict[str, Any]],
        ground_truth: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive evaluation of RAG response.

        Evaluates both the relevance of retrieved chunks and the faithfulness of the
        generated answer, returning combined scores and reasoning.

        Args:
            query: Original user query.
            answer: Generated answer to evaluate.
            retrieved_chunks: Retrieved context chunks used to generate the answer.
            ground_truth: Optional ground truth answer for comparison.

        Returns:
            Dictionary containing:
                - relevance_score: Score for chunk relevance (0-1)
                - faithfulness_score: Score for answer groundedness (0-1)
                - overall_score: Weighted average of both scores
                - passed: Boolean indicating if overall score meets threshold (0.7)
                - judge_reasoning: Detailed reasoning for the scores
        """
        if not self.judge_llm:
            logger.warning("No LLM API key configured for evaluation")
            return {
                "relevance_score": 0.0,
                "faithfulness_score": 0.0,
                "overall_score": 0.0,
                "passed": False,
                "judge_reasoning": "LLM not configured for evaluation"
            }

        relevance_score = self.evaluate_relevance(query, retrieved_chunks)

        faithfulness_score = self.evaluate_faithfulness(answer, retrieved_chunks)

        overall_score = (relevance_score * 0.5) + (faithfulness_score * 0.5)

        passed = overall_score >= 0.7

        reasoning = f"""
Relevance Score: {relevance_score:.2f} - The retrieved chunks {"are" if relevance_score > 0.7 else "may not be"} highly relevant to the query.
Faithfulness Score: {faithfulness_score:.2f} - The answer {"is" if faithfulness_score > 0.7 else "may not be"} well-grounded in the context.
Overall Score: {overall_score:.2f} - {"PASSED" if passed else "FAILED"} (threshold: 0.70)
        """.strip()

        evaluation_result = {
            "relevance_score": relevance_score,
            "faithfulness_score": faithfulness_score,
            "overall_score": overall_score,
            "passed": passed,
            "judge_reasoning": reasoning
        }

        return evaluation_result

    def save_evaluation(
        self,
        query: str,
        answer: str,
        retrieved_chunks: List[Dict[str, Any]],
        evaluation_result: Dict[str, Any]
    ) -> int:
        """
        Persist evaluation result to the database.

        Stores all evaluation metrics and metadata for audit trail and analysis.

        Args:
            query: Original user query.
            answer: Generated answer that was evaluated.
            retrieved_chunks: Retrieved chunks used for the answer.
            evaluation_result: Dictionary of evaluation scores and reasoning.

        Returns:
            ID of the saved evaluation record, or -1 if saving failed.
        """
        try:
            eval_record = EvaluationResult(
                query_text=query,
                answer=answer,
                retrieved_chunks=[
                    {
                        "chunk_id": chunk.get("chunk_id"),
                        "chunk_text": chunk.get("chunk_text"),
                        "relevance_score": chunk.get("relevance_score")
                    }
                    for chunk in retrieved_chunks
                ],
                relevance_score=evaluation_result["relevance_score"],
                faithfulness_score=evaluation_result["faithfulness_score"],
                overall_score=evaluation_result["overall_score"],
                judge_reasoning=evaluation_result["judge_reasoning"],
                passed=evaluation_result["passed"],
                metadata_={}
            )

            self.db.add(eval_record)
            self.db.commit()
            self.db.refresh(eval_record)

            logger.info(f"Saved evaluation result with ID: {eval_record.id}")
            return eval_record.id

        except Exception as e:
            logger.error(f"Error saving evaluation: {str(e)}")
            self.db.rollback()
            return -1

    def get_evaluation_stats(self) -> Dict[str, Any]:
        """
        Retrieve aggregated evaluation statistics.

        Computes overall performance metrics across all stored evaluations including
        pass rate, pass/fail counts, and average scores.

        Returns:
            Dictionary containing:
                - total_evaluations: Total number of evaluations performed
                - passed: Count of evaluations that passed
                - failed: Count of evaluations that failed
                - pass_rate: Percentage of evaluations that passed
                - avg_relevance: Average relevance score across all evaluations
                - avg_faithfulness: Average faithfulness score across all evaluations
                - avg_overall: Average overall score across all evaluations
        """
        try:
            total = self.db.query(EvaluationResult).count()
            passed = self.db.query(EvaluationResult).filter(
                EvaluationResult.passed == True
            ).count()

            if total == 0:
                return {
                    "total_evaluations": 0,
                    "passed": 0,
                    "failed": 0,
                    "pass_rate": 0.0,
                    "avg_relevance": 0.0,
                    "avg_faithfulness": 0.0,
                    "avg_overall": 0.0
                }

            failed = total - passed

            avg_scores = self.db.query(
                func.avg(EvaluationResult.relevance_score).label('avg_relevance'),
                func.avg(EvaluationResult.faithfulness_score).label('avg_faithfulness'),
                func.avg(EvaluationResult.overall_score).label('avg_overall')
            ).first()

            return {
                "total_evaluations": total,
                "passed": passed,
                "failed": failed,
                "pass_rate": (passed / total) * 100,
                "avg_relevance": float(avg_scores.avg_relevance or 0),
                "avg_faithfulness": float(avg_scores.avg_faithfulness or 0),
                "avg_overall": float(avg_scores.avg_overall or 0)
            }

        except Exception as e:
            logger.error(f"Error getting evaluation stats: {str(e)}")
            return {}
