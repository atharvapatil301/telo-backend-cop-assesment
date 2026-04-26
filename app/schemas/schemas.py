"""
Pydantic Schemas for Request/Response Validation
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


# ============= Venue Schemas =============

class VenueBase(BaseModel):
    """Base venue schema"""
    id: str
    name: str
    city: Optional[str] = None
    neighborhood: Optional[str] = None
    capacity: Optional[int] = None
    price_per_head_usd: Optional[float] = None
    venue_type: Optional[str] = None
    amenities: Optional[List[str]] = []
    tags: Optional[List[str]] = []
    description: Optional[str] = None
    policies: Optional[Dict[str, Any]] = {}


class VenueCreate(VenueBase):
    """Schema for creating a venue"""
    pass


class VenueResponse(VenueBase):
    """Schema for venue response"""
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============= Document Schemas =============

class DocumentBase(BaseModel):
    """Base document schema"""
    id: str = Field(..., alias="doc_id")
    venue_id: str
    title: str
    content: str
    doc_type: str = "text"
    metadata_: Optional[Dict[str, Any]] = Field(default={}, alias="metadata")


class DocumentCreate(DocumentBase):
    """Schema for creating a document"""
    pass


class DocumentResponse(DocumentBase):
    """Schema for document response"""
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        populate_by_name = True


# ============= Ingestion Schemas =============

class BulkIngestRequest(BaseModel):
    """Schema for bulk ingestion request"""
    venues: List[VenueCreate] = []
    documents: List[DocumentCreate] = []


class IngestResponse(BaseModel):
    """Schema for ingestion response"""
    success: bool
    message: str
    venues_ingested: int = 0
    documents_ingested: int = 0
    chunks_created: int = 0


class IndexingRequest(BaseModel):
    """Schema for triggering indexing"""
    reindex_all: bool = False
    venue_ids: Optional[List[str]] = None


class IndexingResponse(BaseModel):
    """Schema for indexing response"""
    success: bool
    message: str
    chunks_indexed: int = 0


# ============= Query Schemas =============

class QueryRequest(BaseModel):
    """Schema for query request"""
    question: str = Field(..., min_length=1, description="Question to ask about venues")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of chunks to retrieve")
    use_cache: bool = Field(default=True, description="Whether to use cached results")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata filters")


class SourceReference(BaseModel):
    """Schema for source reference"""
    chunk_id: int
    document_id: str
    document_title: str
    venue_id: str
    venue_name: str
    chunk_text: str
    relevance_score: float


class QueryResponse(BaseModel):
    """Schema for query response"""
    question: str
    answer: str
    sources: List[SourceReference]
    cached: bool = False
    metadata: Dict[str, Any] = {}


# ============= Inspection Schemas =============

class ChunkInspectionResponse(BaseModel):
    """Schema for inspecting retrieved chunks"""
    chunk_id: int
    document_id: str
    venue_id: str
    chunk_text: str
    chunk_index: int
    metadata: Dict[str, Any]


class DocumentInspectionResponse(BaseModel):
    """Schema for inspecting documents"""
    document_id: str
    venue_id: str
    title: str
    content: str
    chunk_count: int
    created_at: datetime


# ============= Evaluation Schemas =============

class EvaluationRequest(BaseModel):
    """Schema for evaluation request"""
    query: str
    answer: str
    retrieved_chunks: List[Dict[str, Any]]
    ground_truth: Optional[str] = None


class EvaluationResponse(BaseModel):
    """Schema for evaluation response"""
    relevance_score: float
    faithfulness_score: float
    overall_score: float
    passed: bool
    judge_reasoning: str
    metadata: Dict[str, Any] = {}


# ============= Health Check Schema =============

class HealthResponse(BaseModel):
    """Schema for health check response"""
    status: str
    database: str
    cache: str
    embeddings: str
