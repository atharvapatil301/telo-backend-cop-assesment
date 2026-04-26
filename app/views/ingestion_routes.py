"""
Ingestion Routes (View Layer in MVC)
Handles document and venue ingestion endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from app.db.session import get_db
from app.schemas.schemas import (
    VenueCreate,
    DocumentCreate,
    BulkIngestRequest,
    IngestResponse,
    IndexingRequest,
    IndexingResponse
)
from app.models.database import Venue, Document, DocumentChunk
from app.controllers.document_processor import DocumentProcessorController

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ingest", tags=["Ingestion"])


@router.post("/venues", response_model=IngestResponse)
async def ingest_venues(
    venues: List[VenueCreate],
    db: Session = Depends(get_db)
):
    """
    Ingest or update venue data in the knowledge base.

    Creates new venue records or updates existing ones based on venue ID.

    Args:
        venues: List of venue objects to ingest.
        db: Database session for data persistence.

    Returns:
        IngestResponse with success status and count of venues ingested.
    """
    try:
        ingested_count = 0
        for venue_data in venues:
            existing = db.query(Venue).filter(Venue.id == venue_data.id).first()

            if existing:
                for key, value in venue_data.model_dump().items():
                    setattr(existing, key, value)
                logger.info(f"Updated venue: {venue_data.id}")
            else:
                venue = Venue(**venue_data.model_dump())
                db.add(venue)
                logger.info(f"Created venue: {venue_data.id}")

            ingested_count += 1

        db.commit()

        return IngestResponse(
            success=True,
            message=f"Successfully ingested {ingested_count} venues",
            venues_ingested=ingested_count
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Error ingesting venues: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting venues: {str(e)}"
        )


@router.post("/documents", response_model=IngestResponse)
async def ingest_documents(
    documents: List[DocumentCreate],
    db: Session = Depends(get_db)
):
    """
    Ingest or update document data in the knowledge base.

    Creates new document records or updates existing ones. Documents must reference
    an existing venue. Chunks are not created during ingestion; see /index endpoint.

    Args:
        documents: List of document objects to ingest.
        db: Database session for data persistence.

    Returns:
        IngestResponse with success status and count of documents ingested.
    """
    try:
        ingested_count = 0
        for doc_data in documents:
            venue = db.query(Venue).filter(Venue.id == doc_data.venue_id).first()
            if not venue:
                logger.warning(f"Venue {doc_data.venue_id} not found for document {doc_data.id}")
                continue

            existing = db.query(Document).filter(Document.id == doc_data.id).first()

            doc_dict = doc_data.model_dump(by_alias=False)

            if existing:
                for key, value in doc_dict.items():
                    setattr(existing, key, value)
                logger.info(f"Updated document: {doc_data.id}")
            else:
                document = Document(**doc_dict)
                db.add(document)
                logger.info(f"Created document: {doc_data.id}")

            ingested_count += 1

        db.commit()

        return IngestResponse(
            success=True,
            message=f"Successfully ingested {ingested_count} documents",
            documents_ingested=ingested_count
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Error ingesting documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting documents: {str(e)}"
        )


@router.post("/bulk", response_model=IngestResponse)
async def bulk_ingest(
    request: BulkIngestRequest,
    db: Session = Depends(get_db)
):
    """
    Bulk ingest venues and documents together in a single request.

    Ingests venues first, then documents that reference those venues.
    More efficient than separate ingest calls when loading related data.

    Args:
        request: BulkIngestRequest containing venues and documents lists.
        db: Database session for data persistence.

    Returns:
        IngestResponse with success status and counts for venues and documents.
    """
    try:
        venues_count = 0
        documents_count = 0

        for venue_data in request.venues:
            existing = db.query(Venue).filter(Venue.id == venue_data.id).first()

            if existing:
                for key, value in venue_data.model_dump().items():
                    setattr(existing, key, value)
            else:
                venue = Venue(**venue_data.model_dump())
                db.add(venue)

            venues_count += 1

        db.commit()

        for doc_data in request.documents:
            venue = db.query(Venue).filter(Venue.id == doc_data.venue_id).first()
            if not venue:
                logger.warning(f"Venue {doc_data.venue_id} not found")
                continue

            existing = db.query(Document).filter(Document.id == doc_data.id).first()
            doc_dict = doc_data.model_dump(by_alias=False)

            if existing:
                for key, value in doc_dict.items():
                    setattr(existing, key, value)
            else:
                document = Document(**doc_dict)
                db.add(document)

            documents_count += 1

        db.commit()

        return IngestResponse(
            success=True,
            message=f"Successfully ingested {venues_count} venues and {documents_count} documents",
            venues_ingested=venues_count,
            documents_ingested=documents_count
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Error in bulk ingestion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in bulk ingestion: {str(e)}"
        )


@router.post("/index", response_model=IndexingResponse)
async def index_documents(
    request: IndexingRequest,
    db: Session = Depends(get_db)
):
    """
    Create or update document embeddings through chunking and vectorization.

    Splits documents into semantic chunks, generates embeddings, enriches metadata
    with venue and document information, and stores chunks for vector search.

    Args:
        request: IndexingRequest with documents to index and reindexing options.
        db: Database session for data persistence.

    Returns:
        IndexingResponse with success status and count of chunks created.
    """
    try:
        doc_processor = DocumentProcessorController()
        chunks_created = 0

        query = db.query(Document)
        if not request.reindex_all and request.venue_ids:
            query = query.filter(Document.venue_id.in_(request.venue_ids))

        documents = query.all()

        for document in documents:
            if request.reindex_all:
                db.query(DocumentChunk).filter(
                    DocumentChunk.document_id == document.id
                ).delete()

            venue = db.query(Venue).filter(Venue.id == document.venue_id).first()

            processed_chunks = doc_processor.process_document(
                document_id=document.id,
                venue_id=document.venue_id,
                content=document.content,
                metadata={
                    "doc_type": document.doc_type,
                    "title": document.title
                }
            )

            for chunk_data in processed_chunks:
                enriched = doc_processor.enrich_chunk_metadata(
                    chunk_data,
                    venue_data={
                        "name": venue.name if venue else "Unknown",
                        "venue_type": venue.venue_type if venue else None,
                        "city": venue.city if venue else None,
                        "neighborhood": venue.neighborhood if venue else None
                    },
                    document_data={
                        "title": document.title,
                        "doc_type": document.doc_type
                    }
                )

                chunk = DocumentChunk(**enriched)
                db.add(chunk)
                chunks_created += 1

            logger.info(f"Indexed document {document.id}: {len(processed_chunks)} chunks")

        db.commit()

        return IndexingResponse(
            success=True,
            message=f"Successfully indexed {len(documents)} documents into {chunks_created} chunks",
            chunks_indexed=chunks_created
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Error indexing documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error indexing documents: {str(e)}"
        )
