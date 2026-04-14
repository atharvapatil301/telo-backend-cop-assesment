# TeloHive Backend Co-op Assessment

Welcome to the TeloHive backend engineering take-home assessment.

This assessment is for candidates applying to backend or backend-leaning co-op roles at TeloHive. The goal is to evaluate backend engineering fundamentals, system design, product thinking, code quality, and production readiness in the context of AI-enabled software systems.

## About TeloHive

TeloHive is building an AI-native platform for venue matching, venue discovery, and venue operations workflows. We care about pragmatic engineering, clean backend design, reliable APIs, thoughtful data modeling, and the ability to work on AI-enabled user experiences without losing backend rigor.

## Assessment Format

- Choose `1 of 2` tasks
- Expected effort: `10-14 hours`
- Submission timeline: `7 days` from the time you receive the assignment
- Preferred stack:
  - Python
  - FastAPI
  - PostgreSQL
  - Docker / Docker Compose

You are free to use supporting libraries and tools when appropriate, but your design decisions should remain pragmatic and well-explained.

## Task Options

### Option 1: AI Venue Search Backend

Build a backend service for venue discovery and matching.

Details: [TASK_1.md](./TASK_1.md)

### Option 2: RAG-Powered Venue Knowledge Assistant API

Build a backend system for internal knowledge retrieval over venue documents and operational notes.

Details: [TASK_2.md](./TASK_2.md)

## What To Submit

Please read [SUBMISSION.md](./SUBMISSION.md) before starting.

At a minimum, your submission should include:

- a GitHub repository
- a working codebase
- setup instructions
- a README
- architecture notes
- tests
- sample requests or API documentation

## Evaluation Criteria

We will evaluate submissions across backend engineering fundamentals, design quality, scalability, production readiness, and implementation clarity.

Details: [EVALUATION.md](./EVALUATION.md)

## Sample Data

We have included a lightweight sample dataset to help you get started:

- [data/venues.json](./data/venues.json)
- [data/venue_docs.json](./data/venue_docs.json)

You may extend or transform this data as needed.

## FAQ

Common clarifications are documented in [FAQ.md](./FAQ.md).

## Use Of AI Tools

You may use AI coding tools such as ChatGPT, Claude, Cursor, or GitHub Copilot. However:

- you must understand every part of the submission
- you must be able to explain your design and implementation decisions
- you should clearly document tradeoffs and assumptions
- you should not submit code that you cannot defend in a technical discussion

We care more about engineering judgment than tool usage.

## What We Value

We value:

- correct and clear backend design
- strong API and schema decisions
- sensible production thinking
- pragmatic tradeoff decisions
- readable code
- good developer experience
- evidence that you can build backend systems for AI-enabled products

## Contact

If you need a short extension or have a clarification question, reply to the assignment email.
