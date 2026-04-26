#!/usr/bin/env python3
"""
Python test script for TeloHive Venue Knowledge Assistant API
Alternative to test_api.sh for systems without curl/jq
"""
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"


def print_section(title):
    """Print formatted section header"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}\n")


def print_response(response):
    """Print formatted JSON response"""
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    print()


def test_health():
    """Test health check endpoint"""
    print_section("1. Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print_response(response)


def test_bulk_ingest():
    """Test bulk ingestion"""
    print_section("2. Bulk Ingestion")

    # Load sample data
    data_file = Path(__file__).parent / "sample_ingestion.json"
    with open(data_file, 'r') as f:
        data = json.load(f)

    response = requests.post(f"{BASE_URL}/ingest/bulk", json=data)
    print_response(response)


def test_indexing():
    """Test indexing/embedding creation"""
    print_section("3. Create Embeddings")

    payload = {"reindex_all": True}
    response = requests.post(f"{BASE_URL}/ingest/index", json=payload)
    print_response(response)


def test_stats():
    """Test system stats"""
    print_section("4. System Stats")

    response = requests.get(f"{BASE_URL}/inspect/stats")
    print_response(response)


def test_query_catering():
    """Test query about outside catering"""
    print_section("5. Query: Outside Catering")

    payload = {
        "question": "Which venues allow outside catering?",
        "top_k": 5,
        "use_cache": True
    }
    response = requests.post(f"{BASE_URL}/query/", json=payload)
    print_response(response)


def test_query_av():
    """Test query about AV capabilities"""
    print_section("6. Query: AV Support")

    payload = {
        "question": "Which venues have built-in AV support?",
        "top_k": 5,
        "use_cache": True
    }
    response = requests.post(f"{BASE_URL}/query/", json=payload)
    print_response(response)


def test_query_cancellation():
    """Test query about cancellation policies"""
    print_section("7. Query: Cancellation Policies")

    payload = {
        "question": "What are the cancellation policies for venues?",
        "top_k": 5,
        "use_cache": True
    }
    response = requests.post(f"{BASE_URL}/query/", json=payload)
    print_response(response)


def test_cache_stats():
    """Test cache statistics"""
    print_section("8. Cache Statistics")

    response = requests.get(f"{BASE_URL}/query/cache/stats")
    print_response(response)


def test_inspect_chunks():
    """Test chunk inspection"""
    print_section("9. Inspect Chunks")

    response = requests.get(f"{BASE_URL}/inspect/chunks?venue_id=venue_001&limit=5")
    print_response(response)


def test_inspect_documents():
    """Test document inspection"""
    print_section("10. Inspect Documents")

    response = requests.get(f"{BASE_URL}/inspect/documents?limit=5")
    print_response(response)


def test_query_and_evaluate():
    """Test query with automatic evaluation"""
    print_section("11. Query with Automatic Evaluation")

    payload = {
        "question": "Which venues allow outside catering?",
        "top_k": 5,
        "use_cache": False
    }
    response = requests.post(f"{BASE_URL}/evaluate/query-and-evaluate", json=payload)
    print_response(response)


def test_evaluation_stats():
    """Test evaluation statistics"""
    print_section("12. Evaluation Statistics")

    response = requests.get(f"{BASE_URL}/evaluate/stats")
    print_response(response)


def test_cache_hit():
    """Test cache hit (repeat previous query)"""
    print_section("13. Test Cache Hit")

    payload = {
        "question": "Which venues allow outside catering?",
        "top_k": 5,
        "use_cache": True
    }
    response = requests.post(f"{BASE_URL}/query/", json=payload)

    data = response.json()
    print(f"Cache hit: {data.get('cached', False)}")
    print()


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("TeloHive Venue Knowledge Assistant")
    print("Python API Test Script")
    print("="*60)

    try:
        # Check if API is running
        requests.get(BASE_URL, timeout=2)
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Error: Cannot connect to API at {BASE_URL}")
        print("Make sure the API is running: docker-compose up")
        return

    # Run tests
    test_health()
    test_bulk_ingest()
    test_indexing()
    test_stats()
    test_query_catering()
    test_query_av()
    test_query_cancellation()
    test_cache_stats()
    test_inspect_chunks()
    test_inspect_documents()
    test_query_and_evaluate()
    test_evaluation_stats()
    test_cache_hit()

    print_section("✅ Testing Complete!")


if __name__ == "__main__":
    main()
