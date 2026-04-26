# Quick Start Guide

## Prerequisites

- Docker Desktop installed and running
- `curl` and `jq` installed (for testing)

## Step 1: Start the Application

```bash
# Navigate to project directory
cd telo-backend-cop-assesment

# Start all services (PostgreSQL, Redis, API)
docker-compose up --build
```

Wait for all services to start. You should see:
```
telohive_api      | INFO:     Application startup complete.
telohive_postgres | database system is ready to accept connections
telohive_redis    | Ready to accept connections
```

## Step 2: Verify Health

In a new terminal:

```bash
curl http://localhost:8000/health | jq .
```

Expected output:
```json
{
  "status": "healthy",
  "database": "healthy",
  "cache": "healthy",
  "embeddings": "healthy"
}
```


## Step 3: Test Queries

### Query 1: Outside Catering

```bash
curl -X POST http://localhost:8000/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Which venues allow outside catering?",
    "top_k": 5,
    "use_cache": true
  }' | jq .
```
#### Response Screenshot
![Screenshot 2026-04-26 at 2.00.20 PM.png](screenshots/Screenshot%202026-04-26%20at%202.00.20%E2%80%AFPM.png)


### Query 2: AV Capabilities

```bash
curl -X POST http://localhost:8000/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Which venues have built-in AV support?",
    "top_k": 5,
    "use_cache": true
  }' | jq .
```
#### Response Screenshot
![Screenshot 2026-04-26 at 2.02.03 PM.png](screenshots/Screenshot%202026-04-26%20at%202.02.03%E2%80%AFPM.png)



### Query 3: With Evaluation

```bash
curl -X POST http://localhost:8000/evaluate/query-and-evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the cancellation policies?",
    "top_k": 5,
    "use_cache": false
  }' | jq .
```
#### Response Screenshot
![Screenshot 2026-04-26 at 2.04.59 PM.png](screenshots/Screenshot%202026-04-26%20at%202.04.59%E2%80%AFPM.png)


## Step 4: Explore the API

### Interactive Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Run Full Test Suite

```bash
./scripts/test_api.sh
```

## Common Commands

### View Logs
```bash
docker-compose logs -f app
```

### Stop Services
```bash
docker-compose down
```

### Reset Database
```bash
docker-compose down -v  # Removes volumes
docker-compose up --build
```

### Access PostgreSQL
```bash
docker exec -it telohive_postgres psql -U telohive -d venue_knowledge
```

### Check System Stats
```bash
curl http://localhost:8000/inspect/stats | jq .
```

### Check Cache Stats
```bash
curl http://localhost:8000/query/cache/stats | jq .
```

### Check Evaluation Stats
```bash
curl http://localhost:8000/evaluate/stats | jq .
```

## Troubleshooting

### Port Already in Use

If port 8000, 5432, or 6379 is already in use:

1. Edit `docker-compose.yml`
2. Change port mappings:
   ```yaml
   ports:
     - "8001:8000"  # For API
     - "5433:5432"  # For PostgreSQL
     - "6380:6379"  # For Redis
   ```
3. Update BASE_URL in scripts accordingly

### Database Connection Error

Wait 30 seconds after `docker-compose up` for PostgreSQL to fully initialize.

### Embeddings Model Download

First run will download the embedding model (~80MB). This is normal and only happens once.

## Next Steps

1. Read the full [PROJECT_README.md](PROJECT_README.md) for architecture details
2. Explore the API documentation at http://localhost:8000/docs
3. Try the sample test script: `./scripts/test_api.sh`
4. Review the code structure in the `app/` directory

## Optional: Add LLM API Keys

For full functionality (answer generation and evaluation):

1. Copy `.env.example` to `.env`
2. Add your API key:
   ```
   GEMINI_API_KEY=your_key_here
   ```
3. Restart: `docker-compose restart app`

**Note:** The system works without API keys using fallback mode (concatenated chunks instead of generated answers).
