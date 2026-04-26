"""
Evaluation Routes (View Layer in MVC)
Handles LLM-as-a-Judge evaluation endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.db.session import get_db
from app.schemas.schemas import (
    EvaluationRequest,
    EvaluationResponse,
    QueryRequest
)
from app.controllers.evaluation_controller import EvaluationController
from app.controllers.rag_controller import RAGController

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/evaluate", tags=["Evaluation"])


@router.post("/", response_model=EvaluationResponse)
async def evaluate_response(
    request: EvaluationRequest,
    db: Session = Depends(get_db)
):
    """
    Evaluate a query-answer pair using LLM-as-a-Judge methodology.

    Scores relevance and faithfulness of a RAG response and persists the
    evaluation results for auditing and quality monitoring.

    Args:
        request: EvaluationRequest with query, answer, and retrieved chunks.
        db: Database session for persisting evaluation results.

    Returns:
        EvaluationResponse with relevance, faithfulness, and overall scores.
    """
    try:
        eval_controller = EvaluationController(db)

        result = eval_controller.evaluate_response(
            query=request.query,
            answer=request.answer,
            retrieved_chunks=request.retrieved_chunks,
            ground_truth=request.ground_truth
        )

        eval_controller.save_evaluation(
            query=request.query,
            answer=request.answer,
            retrieved_chunks=request.retrieved_chunks,
            evaluation_result=result
        )

        return EvaluationResponse(
            relevance_score=result["relevance_score"],
            faithfulness_score=result["faithfulness_score"],
            overall_score=result["overall_score"],
            passed=result["passed"],
            judge_reasoning=result["judge_reasoning"],
            metadata={}
        )

    except Exception as e:
        logger.error(f"Error evaluating response: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error evaluating response: {str(e)}"
        )


@router.post("/query-and-evaluate", response_model=dict)
async def query_and_evaluate(
    request: QueryRequest,
    db: Session = Depends(get_db)
):
    """
    Execute a RAG query and automatically evaluate the generated response.

    Performs both query execution and evaluation in a single request for
    end-to-end quality assessment of the RAG system.

    Args:
        request: QueryRequest containing question and search parameters.
        db: Database session for data access and evaluation persistence.

    Returns:
        Dictionary with query results and evaluation scores.
    """
    try:
        rag_controller = RAGController(db)
        result = rag_controller.query(
            question=request.question,
            top_k=request.top_k,
            filters=request.filters
        )

        eval_controller = EvaluationController(db)
        evaluation = eval_controller.evaluate_response(
            query=request.question,
            answer=result["answer"],
            retrieved_chunks=result["sources"]
        )

        eval_controller.save_evaluation(
            query=request.question,
            answer=result["answer"],
            retrieved_chunks=result["sources"],
            evaluation_result=evaluation
        )

        return {
            "query": request.question,
            "answer": result["answer"],
            "sources": result["sources"],
            "evaluation": {
                "relevance_score": evaluation["relevance_score"],
                "faithfulness_score": evaluation["faithfulness_score"],
                "overall_score": evaluation["overall_score"],
                "passed": evaluation["passed"],
                "reasoning": evaluation["judge_reasoning"]
            },
            "metadata": result.get("metadata", {})
        }

    except Exception as e:
        logger.error(f"Error in query and evaluate: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in query and evaluate: {str(e)}"
        )


@router.get("/stats")
async def get_evaluation_stats(db: Session = Depends(get_db)):
    """
    Retrieve aggregated evaluation statistics and metrics.

    Returns overall quality metrics across all evaluations including
    pass rates and average scores.

    Args:
        db: Database session for data access.

    Returns:
        Dictionary with evaluation statistics including pass rate and average scores.
    """
    try:
        eval_controller = EvaluationController(db)
        stats = eval_controller.get_evaluation_stats()
        return stats

    except Exception as e:
        logger.error(f"Error getting evaluation stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting evaluation stats: {str(e)}"
        )
