# Task 1: AI Venue Search Backend

## Problem

Build a backend service for an AI-native venue matching platform.

Users should be able to search for venues using structured filters and natural-language intent, for example:

- "Rooftop venue in Boston for a startup mixer with 80 people"
- "Private dining space in Cambridge for a team dinner under $120 per head"
- "Industrial-style venue with AV support for a demo day"

The system should support both structured venue filtering and a more intelligent ranking layer that reflects user intent.

## Objective

Design and implement a backend that:

- stores venue information cleanly
- supports CRUD operations
- enables structured and text-based search
- returns ranked results with explainable matching
- demonstrates production-minded engineering choices

## Required Stack

Preferred:

- Python
- FastAPI
- PostgreSQL
- Docker Compose

You may use adjacent tools if needed, but the closer you stay to this stack, the easier it is for us to evaluate your work against the role.

## Functional Requirements

Your system should include:

1. Venue data model
- venue identity
- location
- capacity
- pricing or pricing hints
- amenities
- tags / categories
- short descriptive content
- optional operational attributes

2. Core API endpoints
- create venue
- update venue
- delete venue
- get venue by id
- list venues
- search venues

3. Search behavior
- support structured filters such as city, capacity, budget, and amenities
- support keyword or natural-language search
- return ranked results
- include a brief explanation of why a result matched

4. Lead / search capture
- add one endpoint to save a user inquiry, search request, or lead record

5. Local developer setup
- system should run locally using Docker Compose

## Strong Bonus Points

- pgvector-based semantic search
- JSONB for flexible venue attributes
- ranking logic that combines structured and semantic relevance
- pagination and filtering discipline
- authentication or admin access control
- database migrations
- request validation and robust error handling
- deployment notes for AWS EC2 / S3 / Route 53 / IAM
- clean API docs

## What We Are Looking For

We are not looking for a massive feature set. We are looking for:

- a clean backend design
- thoughtful data modeling
- a reliable search flow
- clear tradeoffs
- a system that another engineer could extend

## Deliverables

See [SUBMISSION.md](./SUBMISSION.md), but for this task specifically include:

- architecture notes for search and ranking
- explanation of how structured filters and text/semantic matching interact
- explanation of how you would scale the system if traffic or data volume increased

## Suggested Timebox

Target a polished, scoped implementation rather than trying to do everything.

If you choose to leave some ideas unimplemented, document:

- what you prioritized
- what you intentionally left out
- what you would build next
