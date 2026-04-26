# TeloHive Venue Knowledge Assistant API

Production-ready RAG system for intelligent venue knowledge retrieval using local embeddings and Gemini LLM.

## Quick Start

```bash
docker-compose up --build
curl http://localhost:8000/health
```

API Documentation: http://localhost:8000/docs

## Architecture

```
User Query → Embedding (sentence-transformers) → Vector Search (pgvector)
    → Retrieved Chunks → LLM Generation (Gemini) → Answer + Sources
```

### Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL + pgvector
- **Embeddings**: Sentence Transformers (local, all-MiniLM-L6-v2)
- **LLM**: Google Gemini 2.5-flash
- **Orchestration**: LangChain

### Project Structure

```
app/
├── models/          # Database models (SQLAlchemy)
├── views/           # API routes (FastAPI)
├── controllers/     # Business logic
├── schemas/         # Pydantic validation
└── db/              # Database session
```

## Core Features

### Data Ingestion
- Structured venue data + unstructured documents
- Intelligent chunking (500 tokens, 50 overlap)
- Batch embedding generation
- Metadata enrichment

### RAG Query
- Semantic vector search
- LLM-powered answer generation
- Source citations with relevance scores
- Query caching (hash-based deduplication)

### LLM-as-a-Judge Evaluation
- **Relevance**: Query ↔ Retrieved chunks
- **Faithfulness**: Answer ↔ Context grounding
- **Overall Score**: Weighted average (threshold: 0.7)
- Statistics tracking

## API Endpoints

### Ingestion
- `POST /ingest/bulk` - Ingest venues and documents
- `POST /ingest/index` - Create embeddings

### Query
- `POST /query/` - RAG query execution
- `GET /query/cache/stats` - Cache statistics

### Inspection
- `GET /inspect/chunks` - View document chunks
- `GET /inspect/stats` - System statistics

### Evaluation
- `POST /evaluate/query-and-evaluate` - Query + automatic evaluation
- `GET /evaluate/stats` - Evaluation metrics

## Example Usage

**Query:**
```bash
curl -X POST http://localhost:8000/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Which venues allow outside catering?",
    "top_k": 3
  }'
```

**Response:**
```json
{
  "answer": "Harbor Loft allows outside catering with prior approval.",
  "sources": [
    {
      "venue_name": "Harbor Loft",
      "document_title": "Harbor Loft Policies",
      "chunk_text": "Harbor Loft allows outside catering...",
      "relevance_score": 0.89
    }
  ],
  "metadata": {
    "chunks_retrieved": 3,
    "llm_used": true
  }
}
```

## Key Design Decisions

### Chunking
- 500 token chunks with 50 token overlap
- Balances context preservation vs retrieval precision
- Recursive splitting respects document structure

### Embeddings
- Sentence Transformers (local deployment)
- Fast inference, no API costs
- 384 dimensions for optimal storage/performance

### LLM
- Gemini 2.5-flash for generation and evaluation
- Fast inference, cost-effective
- Excellent instruction following

### Caching
- Database-backed (persistent across restarts)
- Hash-based query normalization
- Configurable TTL (1 hour default)

## Production Considerations

### Scaling
- Stateless API (horizontal scaling ready)
- Connection pooling configured
- Add HNSW index for large datasets

### Observability
- Structured logging
- Health checks for all components
- Evaluation metrics tracking

### Security
- Input validation (Pydantic)
- CORS configuration
- Ready for JWT authentication

## Environment Setup

Required variables in `.env`:
```bash
DATABASE_URL=postgresql://...
GEMINI_API_KEY=your_key_here
```

See `.env.example` for complete configuration.

## Development

Run tests (when implemented):
```bash
pytest tests/
```

View logs:
```bash
docker-compose logs -f app
```

## Documentation

- **QUICKSTART.md**: Step-by-step tutorial with examples
- **ARCHITECTURE.md**: Detailed system design and data flow

---

