# ADR 004: Model Routing Strategy

## Status

Accepted

---

## Context

Different Large Language Models vary in cost, latency, context window size, reasoning ability and domain expertise.

Using a single model for every request is inefficient and unnecessarily expensive.

---

## Decision

NeuroFlow will implement a rule-based model routing layer that selects the most appropriate model based on query characteristics.

Future versions may replace this with a learned routing policy.

---

## Routing Matrix

| Query Type | Model Tier | Reason |
|------------|------------|--------|
| FAQ | Small LLM | Lowest latency and cost |
| Document Q&A | Medium LLM | Balanced quality and efficiency |
| Long Summaries | Large Context LLM | Handles large context windows |
| Complex Reasoning | Premium LLM | Strong reasoning capability |
| Code Generation | Code-specialized LLM | Optimized for programming tasks |
| Legal / Medical | Fine-tuned Domain Model | Higher domain accuracy |
| High-priority Enterprise Queries | Best Available Model | Prioritize quality over cost |

---

## Routing Criteria

Routing decisions consider:

- Query complexity
- Context length
- Domain classification
- Historical model performance
- Latency requirements
- Cost constraints
- User service level objectives (SLOs)

---

## Consequences

### Positive

- Reduced inference costs
- Improved response latency
- Better answer quality
- Efficient use of specialized models

### Negative

- Incorrect routing may reduce answer quality
- Routing policies require ongoing monitoring and refinement

---

## Future Improvements

- Machine learning–based routing
- Adaptive routing using evaluation metrics
- Dynamic A/B testing of routing strategies
- Continuous optimization based on production performance