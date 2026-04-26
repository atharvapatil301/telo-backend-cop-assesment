"""
Database Models (Model Layer in MVC)
SQLAlchemy ORM models for venue knowledge system
"""
from sqlalchemy import Column, String, Integer, Float, JSON, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.db.session import Base
from app.config import settings


class Venue(Base):
    """Venue model - stores structured venue data"""
    __tablename__ = "venues"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    city = Column(String)
    neighborhood = Column(String)
    capacity = Column(Integer)
    price_per_head_usd = Column(Float)
    venue_type = Column(String)
    amenities = Column(JSON)  # List of amenities
    tags = Column(JSON)  # List of tags
    description = Column(Text)
    policies = Column(JSON)  # Dictionary of policies
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    documents = relationship("Document", back_populates="venue", cascade="all, delete-orphan")


class Document(Base):
    """Document model - stores unstructured venue documents"""
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)
    venue_id = Column(String, ForeignKey("venues.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    doc_type = Column(String, default="text")  # text, faq, policy, notes
    metadata_ = Column("metadata", JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    venue = relationship("Venue", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    """Document Chunk model - stores chunked text with embeddings for RAG"""
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False, index=True)
    venue_id = Column(String, ForeignKey("venues.id"), nullable=False, index=True)
    chunk_text = Column(Text, nullable=False)
    chunk_index = Column(Integer)  # Position in original document
    embedding = Column(Vector(settings.EMBEDDING_DIMENSION))  # Vector embedding
    metadata_ = Column("metadata", JSON)  # Additional metadata for filtering
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    document = relationship("Document", back_populates="chunks")


class QueryCache(Base):
    """Query Cache model - caches query results for performance"""
    __tablename__ = "query_cache"

    id = Column(Integer, primary_key=True, autoincrement=True)
    query_hash = Column(String, unique=True, index=True, nullable=False)
    query_text = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    sources = Column(JSON)  # List of source references
    metadata_ = Column("metadata", JSON)  # Additional information
    hit_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_accessed = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True))


class EvaluationResult(Base):
    """Evaluation Result model - stores LLM-as-Judge evaluations"""
    __tablename__ = "evaluation_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    query_text = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    retrieved_chunks = Column(JSON)  # List of retrieved chunks
    relevance_score = Column(Float)  # 0-1 score
    faithfulness_score = Column(Float)  # 0-1 score
    overall_score = Column(Float)  # 0-1 score
    judge_reasoning = Column(Text)  # LLM's explanation
    passed = Column(Boolean)  # Whether it meets quality threshold
    metadata_ = Column("metadata", JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
