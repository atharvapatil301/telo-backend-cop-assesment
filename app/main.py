"""
Main FastAPI Application.

TeloHive Venue Knowledge Assistant API - RAG-powered venue information retrieval system.
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import logging

from app.config import settings
from app.db.session import init_db, get_db
from app.views import ingestion_routes, query_routes, inspection_routes, evaluation_routes
from app.schemas.schemas import HealthResponse
from app.controllers.document_processor import DocumentProcessorController

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TeloHive Venue Knowledge Assistant",
    description="RAG-powered API for venue knowledge retrieval and question answering",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database tables and connections on application startup."""
    logger.info("Starting TeloHive Venue Knowledge Assistant API")
    logger.info(f"Environment: {settings.ENVIRONMENT}")

    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on application shutdown."""
    logger.info("Shutting down TeloHive Venue Knowledge Assistant API")


app.include_router(ingestion_routes.router)
app.include_router(query_routes.router)
app.include_router(inspection_routes.router)
app.include_router(evaluation_routes.router)


@app.get("/")
async def root():
    """
    Root endpoint providing API information and navigation links.

    Returns:
        dict: API metadata and available endpoints
    """
    return {
        "message": "TeloHive Venue Knowledge Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """
    Comprehensive health check for all system components.

    Args:
        db: Database session dependency

    Returns:
        HealthResponse: Status of database, cache, and embeddings services
    """
    health_status = {
        "status": "healthy",
        "database": "unknown",
        "cache": "unknown",
        "embeddings": "unknown"
    }

    try:
        db.execute("SELECT 1")
        health_status["database"] = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        health_status["database"] = "unhealthy"
        health_status["status"] = "degraded"

    health_status["cache"] = "healthy" if health_status["database"] == "healthy" else "unhealthy"

    try:
        processor = DocumentProcessorController()
        test_embedding = processor.generate_embedding("test")
        if len(test_embedding) == settings.EMBEDDING_DIMENSION:
            health_status["embeddings"] = "healthy"
        else:
            health_status["embeddings"] = "unhealthy"
            health_status["status"] = "degraded"
    except Exception as e:
        logger.error(f"Embeddings health check failed: {str(e)}")
        health_status["embeddings"] = "unhealthy"
        health_status["status"] = "degraded"

    return HealthResponse(**health_status)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
