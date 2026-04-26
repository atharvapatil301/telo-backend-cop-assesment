# System Architecture

## Project Structure

```
app/
├── models/          # SQLAlchemy ORM models
├── views/           # FastAPI routes (ingestion, query, inspection, evaluation)
├── controllers/     # Business logic (RAG, document processing, caching, evaluation)
├── schemas/         # Pydantic validation
└── db/              # Database session management

data/                # Sample venues and documents
scripts/             # API test scripts
```

## Database Schema

**Core Tables:**
- `venues`: Structured venue data (name, capacity, amenities, policies)
- `documents`: Unstructured venue documents
- `document_chunks`: Text chunks with 384-dim embeddings (pgvector)
- `query_cache`: Cached query results with TTL
- `evaluation_results`: LLM-as-a-Judge evaluation scores

**Relationships:** venues (1:N) → documents (1:N) → document_chunks

## MVC Architecture

**Models** (`app/models/`): SQLAlchemy ORM for venues, documents, chunks, cache, evaluations

**Views** (`app/views/`): FastAPI routes for ingestion, querying, inspection, evaluation

**Controllers** (`app/controllers/`):
- `document_processor`: Chunking (500 tokens) + embeddings (sentence-transformers)
- `rag_controller`: Vector search + LLM answer generation
- `cache_controller`: Hash-based query caching with TTL
- `evaluation_controller`: LLM-as-a-Judge (relevance + faithfulness scoring)

## Data Flow

**Ingestion:**
1. Client → Pydantic validation → Database persistence
2. Indexing trigger → Chunking → Embedding generation → Storage

**Query (RAG):**
1. Client question → Cache check (hash-based)
2. If miss: Query embedding → Vector search (pgvector) → Top-K chunks → LLM generation → Cache result
3. Return answer + sources with relevance scores

**Evaluation:**
1. Execute RAG query
2. LLM-as-a-Judge evaluates: relevance (query ↔ chunks) + faithfulness (answer ↔ context)
3. Overall score = 0.5×relevance + 0.5×faithfulness (threshold: 0.7)
4. Persist evaluation results

## Technology Stack

- **Framework**: FastAPI (async, automatic docs, Pydantic validation)
- **Database**: PostgreSQL + pgvector (vector similarity search)
- **ORM**: SQLAlchemy (connection pooling, query builder)
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2 (384 dims, local inference)
- **LLM**: Google Gemini 2.5-flash (answer generation + LLM-as-a-Judge)
- **RAG**: LangChain (text splitting, prompt templates, LLM integration)
- **Deployment**: Docker Compose (PostgreSQL, Redis, FastAPI app)

## Production Considerations

**Scaling:**
- Stateless API (horizontal scaling ready)
- Database connection pooling
- Hash-based query caching
- HNSW index support for large datasets

**Security:**
- Pydantic input validation
- Parameterized queries (SQLAlchemy)
- CORS configuration
- Ready for JWT authentication

**Observability:**
- Structured logging (INFO, DEBUG, ERROR)
- Health checks (database, cache, embeddings)
- Evaluation metrics tracking
- Error handling with fallback mode

**Implemented:** Docker deployment, health monitoring, query caching, LLM-as-a-Judge evaluation

**Ready to Add:** Rate limiting, Prometheus metrics, OpenTelemetry tracing, async task queue
