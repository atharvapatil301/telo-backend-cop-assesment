# Evaluation Criteria

We use a practical engineering rubric. The goal is not to reward the largest project. The goal is to identify candidates with strong backend engineering fundamentals and good product judgment.

Total: 100 points

## 1. Problem Understanding: 10

We assess whether you understood the real product problem and translated it into an appropriate backend design.

We look for:

- the right entities and workflows
- sensible assumptions
- clear scope choices
- alignment between implementation and product goals

## 2. Backend Architecture And API Design: 20

We look for:

- clean service structure
- clear endpoint design
- good separation of concerns
- request / response validation
- thoughtful error handling
- maintainable organization

## 3. Code Quality: 15

We look for:

- readability
- consistency
- good naming
- maintainability
- modular design
- engineering hygiene

## 4. Database And Data Modeling: 15

We look for:

- schema quality
- appropriate use of PostgreSQL
- sensible indexing decisions
- structured vs flexible modeling tradeoffs
- appropriate use of JSONB or pgvector if chosen

## 5. Scalability And Production Thinking: 15

We look for:

- pagination
- performance awareness
- observability
- failure handling
- configuration discipline
- deployment awareness
- basic security and access considerations

## 6. AI / Retrieval Design: 10

Relevant especially for Task 2, but also useful in Task 1 if you build semantic or intent-based ranking.

We look for:

- retrieval design quality
- explainability
- grounding / citation quality
- thoughtful use of LLMs
- realistic handling of failure modes

## 7. Testing And Validation: 10

We look for:

- unit or integration tests
- edge-case handling
- realistic verification of core behavior
- confidence that the system works as described

## 8. Documentation And Communication: 5

We look for:

- good README
- setup clarity
- architecture notes
- tradeoff explanations
- submission completeness

## High-Signal Behaviors

Strong submissions usually show:

- correct and scoped implementation
- clear backend judgment
- a schema that matches the product
- practical performance and reliability thinking
- evidence that the author understands the system end to end

## Low-Signal Behaviors

Weak submissions often show:

- too much generated code without clear architecture
- shallow AI integration with weak backend design
- no testing
- poor setup instructions
- overengineered structure without correctness
- inability to explain tradeoffs

## Important Note On AI Tools

Candidates may use AI-assisted coding tools, but they must be able to explain and defend the submission in detail during follow-up interviews.
