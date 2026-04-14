# Task 2: RAG-Powered Venue Knowledge Assistant API

## Problem

Build a backend system that helps internal TeloHive users query venue knowledge.

Imagine that internal teams need to search across:

- venue descriptions
- venue policies
- operational notes
- FAQ content
- previous booking details

Users should be able to ask questions such as:

- "Which venues allow outside catering?"
- "Which venues are best for a 150-person launch event with built-in AV?"
- "What are the cancellation rules for venues in downtown Boston?"

## Objective

Design and implement a backend API that ingests venue-related documents and supports retrieval-backed question answering.

## Required Stack

Preferred:

- Python
- FastAPI
- PostgreSQL
- Docker Compose

## Functional Requirements

Your system should include:

1. Data ingestion
- ingest structured venue data and unstructured text documents
- store enough metadata to support filtering and traceability

2. Retrieval workflow
- support indexing or retrieval preparation
- support question answering over the ingested content
- return relevant supporting passages or citations

3. API endpoints
- ingest or register documents
- trigger indexing or retrieval preparation
- query the system with a question
- inspect sources / citations / retrieved passages

4. Response behavior
- return:
  - answer
  - source references or supporting excerpts
  - some confidence, ranking, or explanation signal

5. Local developer setup
- system should run locally using Docker Compose

## Strong Bonus Points

- pgvector integration
- chunking and embedding pipeline
- hybrid search that combines structured metadata with semantic retrieval
- Anthropic Claude or another LLM API
- evaluation cases and failure mode discussion
- ingestion pipeline quality
- background jobs or async processing
- observability, tracing, or structured logging

## What We Are Looking For

We care about practical engineering judgment, not hype.

A strong submission will show:

- sensible retrieval design
- clear tradeoffs
- thoughtful API boundaries
- explainability
- reliable data handling
- good backend discipline around a real AI-enabled use case

## Deliverables

See [SUBMISSION.md](./SUBMISSION.md), but for this task specifically include:

- explanation of your retrieval design
- why you chose your chunking / indexing / ranking strategy
- how you reduce hallucination or bad-answer risk
- how you would evaluate retrieval quality in a production setting

## Suggested Timebox

Prioritize a backend that is understandable, robust, and well-structured over building a flashy demo with weak engineering foundations.
