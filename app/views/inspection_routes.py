"""
Inspection Routes (View Layer in MVC)
Handles endpoints for inspecting sources and retrieved documents
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.db.session import get_db
from app.schemas.schemas import ChunkInspectionResponse, DocumentInspectionResponse
from app.models.database import DocumentChunk, Document, Venue

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/inspect", tags=["Inspection"])


@router.get("/chunks", response_model=List[ChunkInspectionResponse])
async def get_chunks(
    venue_id: Optional[str] = None,
    document_id: Optional[str] = None,
    limit: int = Query(default=10, le=100),
    db: Session = Depends(get_db)
):
    """
    Retrieve and inspect document chunks with optional filtering.

    Returns chunks for inspection and debugging, optionally filtered
    by venue or document.

    Args:
        venue_id: Optional venue ID to filter chunks.
        document_id: Optional document ID to filter chunks.
        limit: Maximum number of chunks to return. Defaults to 10, max 100.
        db: Database session for data access.

    Returns:
        List of chunks with metadata including text, indices, and document references.
    """
    try:
        query = db.query(DocumentChunk)

        if venue_id:
            query = query.filter(DocumentChunk.venue_id == venue_id)

        if document_id:
            query = query.filter(DocumentChunk.document_id == document_id)

        chunks = query.order_by(
            DocumentChunk.document_id,
            DocumentChunk.chunk_index
        ).limit(limit).all()

        return [
            ChunkInspectionResponse(
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                venue_id=chunk.venue_id,
                chunk_text=chunk.chunk_text,
                chunk_index=chunk.chunk_index,
                metadata=chunk.metadata_ or {}
            )
            for chunk in chunks
        ]

    except Exception as e:
        logger.error(f"Error retrieving chunks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving chunks: {str(e)}"
        )


@router.get("/documents", response_model=List[DocumentInspectionResponse])
async def get_documents(
    venue_id: Optional[str] = None,
    limit: int = Query(default=10, le=100),
    db: Session = Depends(get_db)
):
    """
    Retrieve and inspect documents with optional venue filtering.

    Returns document metadata including content, chunk counts, and creation dates
    for inspection and debugging purposes.

    Args:
        venue_id: Optional venue ID to filter documents.
        limit: Maximum number of documents to return. Defaults to 10, max 100.
        db: Database session for data access.

    Returns:
        List of documents with metadata including chunk counts and creation timestamps.
    """
    try:
        query = db.query(Document)

        if venue_id:
            query = query.filter(Document.venue_id == venue_id)

        documents = query.order_by(Document.created_at.desc()).limit(limit).all()

        return [
            DocumentInspectionResponse(
                document_id=doc.id,
                venue_id=doc.venue_id,
                title=doc.title,
                content=doc.content,
                chunk_count=len(doc.chunks),
                created_at=doc.created_at
            )
            for doc in documents
        ]

    except Exception as e:
        logger.error(f"Error retrieving documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving documents: {str(e)}"
        )


@router.get("/chunks/{chunk_id}", response_model=ChunkInspectionResponse)
async def get_chunk_by_id(
    chunk_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific chunk by its ID.

    Returns detailed information about a single chunk for inspection.

    Args:
        chunk_id: ID of the chunk to retrieve.
        db: Database session for data access.

    Returns:
        ChunkInspectionResponse with full chunk details.

    Raises:
        HTTPException: 404 if chunk not found.
    """
    try:
        chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()

        if not chunk:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chunk {chunk_id} not found"
            )

        return ChunkInspectionResponse(
            chunk_id=chunk.id,
            document_id=chunk.document_id,
            venue_id=chunk.venue_id,
            chunk_text=chunk.chunk_text,
            chunk_index=chunk.chunk_index,
            metadata=chunk.metadata_ or {}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving chunk: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving chunk: {str(e)}"
        )


@router.get("/documents/{document_id}", response_model=DocumentInspectionResponse)
async def get_document_by_id(
    document_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific document by its ID.

    Returns detailed information about a single document including
    content and associated chunk counts.

    Args:
        document_id: ID of the document to retrieve.
        db: Database session for data access.

    Returns:
        DocumentInspectionResponse with full document details.

    Raises:
        HTTPException: 404 if document not found.
    """
    try:
        document = db.query(Document).filter(Document.id == document_id).first()

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found"
            )

        return DocumentInspectionResponse(
            document_id=document.id,
            venue_id=document.venue_id,
            title=document.title,
            content=document.content,
            chunk_count=len(document.chunks),
            created_at=document.created_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving document: {str(e)}"
        )


@router.get("/stats")
async def get_system_stats(db: Session = Depends(get_db)):
    """
    Retrieve overall system statistics.

    Returns counts of all entities and computed statistics including
    average chunks per document.

    Args:
        db: Database session for data access.

    Returns:
        Dictionary with venue count, document count, chunk count, and computed averages.
    """
    try:
        venue_count = db.query(Venue).count()
        document_count = db.query(Document).count()
        chunk_count = db.query(DocumentChunk).count()

        return {
            "venues": venue_count,
            "documents": document_count,
            "chunks": chunk_count,
            "avg_chunks_per_document": round(chunk_count / document_count, 2) if document_count > 0 else 0
        }

    except Exception as e:
        logger.error(f"Error getting system stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting system stats: {str(e)}"
        )
