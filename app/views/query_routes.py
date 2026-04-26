"""
Query Routes (View Layer in MVC)
Handles RAG query endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.db.session import get_db
from app.schemas.schemas import QueryRequest, QueryResponse, SourceReference
from app.controllers.rag_controller import RAGController
from app.controllers.cache_controller import CacheController
from app.controllers.document_processor import DocumentProcessorController

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/query", tags=["Query"])


@router.post("/", response_model=QueryResponse)
async def query_venues(
    request: QueryRequest,
    db: Session = Depends(get_db)
):
    """
    Execute a RAG query against the venue knowledge base.

    Processes a user query by retrieving relevant document chunks and generating
    an answer. Results can be cached based on the request parameter.

    Args:
        request: Query request containing question, optional filters, and cache preference.
        db: Database session for data access.

    Returns:
        QueryResponse with generated answer, source references, cache status, and metadata.
    """
    try:
        rag_controller = RAGController(db)
        cache_controller = CacheController(db)
        doc_processor = DocumentProcessorController()

        query_hash = doc_processor.create_query_hash(
            request.question,
            request.filters
        )

        cached_result = None
        if request.use_cache:
            cached_result = cache_controller.get_cached_result(query_hash)

        if cached_result:
            logger.info(f"Returning cached result for query: {request.question[:50]}...")
            return QueryResponse(
                question=request.question,
                answer=cached_result["answer"],
                sources=[
                    SourceReference(**source) for source in cached_result["sources"]
                ],
                cached=True,
                metadata=cached_result.get("metadata", {})
            )

        result = rag_controller.query(
            question=request.question,
            top_k=request.top_k,
            filters=request.filters
        )

        if request.use_cache:
            cache_controller.cache_result(
                query_hash=query_hash,
                query_text=request.question,
                answer=result["answer"],
                sources=result["sources"],
                metadata=result.get("metadata", {})
            )

        return QueryResponse(
            question=request.question,
            answer=result["answer"],
            sources=[SourceReference(**source) for source in result["sources"]],
            cached=False,
            metadata=result.get("metadata", {})
        )

    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )


@router.get("/cache/stats")
async def get_cache_stats(db: Session = Depends(get_db)):
    """
    Retrieve current cache statistics.

    Returns performance and usage metrics for the query cache including
    entry counts and most frequently accessed queries.

    Args:
        db: Database session for data access.

    Returns:
        Dictionary with cache statistics.
    """
    try:
        cache_controller = CacheController(db)
        stats = cache_controller.get_cache_stats()
        return stats

    except Exception as e:
        logger.error(f"Error getting cache stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting cache stats: {str(e)}"
        )


@router.delete("/cache/clear")
async def clear_cache(
    clear_all: bool = False,
    db: Session = Depends(get_db)
):
    """
    Clear cache entries from the database.

    Removes either all cache entries or only expired ones based on the parameter.

    Args:
        clear_all: If True, clear all cache entries. If False, only expired ones.
        db: Database session for data access.

    Returns:
        Dictionary with success status, message, and count of cleared entries.
    """
    try:
        cache_controller = CacheController(db)

        if clear_all:
            count = cache_controller.clear_all_cache()
            message = f"Cleared all {count} cache entries"
        else:
            count = cache_controller.clear_expired_cache()
            message = f"Cleared {count} expired cache entries"

        return {
            "success": True,
            "message": message,
            "entries_cleared": count
        }

    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing cache: {str(e)}"
        )
