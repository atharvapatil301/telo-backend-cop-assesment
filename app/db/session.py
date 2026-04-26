"""
Database session management and initialization.

Provides SQLAlchemy database engine, session factory, and dependency injection
for FastAPI endpoints. Handles database initialization and cleanup.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Get database session for dependency injection in FastAPI endpoints.

    Creates a new database session and ensures it is properly closed after use.

    Yields:
        Database session for use in route handlers.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize all database tables.

    Creates tables for all models in the database if they don't already exist.
    Should be called once at application startup.
    """
    from app.models.database import Venue, Document, DocumentChunk, QueryCache, EvaluationResult
    Base.metadata.create_all(bind=engine)
