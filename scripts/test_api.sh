#!/bin/bash

# TeloHive Venue Knowledge Assistant - API Test Script
# This script demonstrates all API endpoints with sample requests

BASE_URL="http://localhost:8000"

echo "======================================"
echo "TeloHive Venue Knowledge Assistant"
echo "API Testing Script"
echo "======================================"
echo ""

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. Health Check
echo -e "${BLUE}1. Health Check${NC}"
curl -X GET "$BASE_URL/health" | jq .
echo -e "\n"

# 2. Bulk Ingestion
echo -e "${BLUE}2. Bulk Ingestion (Venues + Documents)${NC}"
curl -X POST "$BASE_URL/ingest/bulk" \
  -H "Content-Type: application/json" \
  -d @scripts/sample_ingestion.json | jq .
echo -e "\n"

# 3. Create Embeddings (Indexing)
echo -e "${BLUE}3. Create Embeddings${NC}"
curl -X POST "$BASE_URL/ingest/index" \
  -H "Content-Type: application/json" \
  -d '{"reindex_all": true}' | jq .
echo -e "\n"

# 4. System Stats
echo -e "${BLUE}4. System Stats${NC}"
curl -X GET "$BASE_URL/inspect/stats" | jq .
echo -e "\n"

# 5. Query: Outside Catering
echo -e "${BLUE}5. Query: Which venues allow outside catering?${NC}"
curl -X POST "$BASE_URL/query/" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Which venues allow outside catering?",
    "top_k": 5,
    "use_cache": true
  }' | jq .
echo -e "\n"

# 6. Query: AV Capabilities
echo -e "${BLUE}6. Query: Which venues have built-in AV support?${NC}"
curl -X POST "$BASE_URL/query/" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Which venues have built-in AV support?",
    "top_k": 5,
    "use_cache": true
  }' | jq .
echo -e "\n"

# 7. Query: Cancellation Policies
echo -e "${BLUE}7. Query: What are the cancellation policies?${NC}"
curl -X POST "$BASE_URL/query/" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the cancellation policies for venues?",
    "top_k": 5,
    "use_cache": true
  }' | jq .
echo -e "\n"

# 8. Cache Stats
echo -e "${BLUE}8. Cache Statistics${NC}"
curl -X GET "$BASE_URL/query/cache/stats" | jq .
echo -e "\n"

# 9. Inspect Chunks
echo -e "${BLUE}9. Inspect Chunks (venue_001)${NC}"
curl -X GET "$BASE_URL/inspect/chunks?venue_id=venue_001&limit=5" | jq .
echo -e "\n"

# 10. Inspect Documents
echo -e "${BLUE}10. Inspect Documents${NC}"
curl -X GET "$BASE_URL/inspect/documents?limit=5" | jq .
echo -e "\n"

# 11. Query and Evaluate
echo -e "${BLUE}11. Query with Automatic Evaluation${NC}"
curl -X POST "$BASE_URL/evaluate/query-and-evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Which venues allow outside catering?",
    "top_k": 5,
    "use_cache": false
  }' | jq .
echo -e "\n"

# 12. Evaluation Stats
echo -e "${BLUE}12. Evaluation Statistics${NC}"
curl -X GET "$BASE_URL/evaluate/stats" | jq .
echo -e "\n"

# 13. Test cache hit (repeat query from #5)
echo -e "${BLUE}13. Test Cache Hit (repeat previous query)${NC}"
curl -X POST "$BASE_URL/query/" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Which venues allow outside catering?",
    "top_k": 5,
    "use_cache": true
  }' | jq '.cached'
echo -e "\n"

echo -e "${GREEN}======================================"
echo "Testing Complete!"
echo -e "======================================${NC}"
