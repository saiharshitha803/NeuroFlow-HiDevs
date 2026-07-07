# ADR 001: Vector Store Selection

## Status

Accepted

---

## Context

NeuroFlow requires a vector database to store document embeddings and perform efficient similarity searches for Retrieval-Augmented Generation (RAG). The chosen solution should support semantic search, integrate with relational data, scale for enterprise workloads and minimize operational complexity.

Several options were considered:

- pgvector
- Pinecone
- Weaviate
- Qdrant

Each provides vector search capabilities but differs in deployment, cost and ecosystem integration.

---

## Decision

NeuroFlow will use **PostgreSQL with the pgvector extension** as the primary vector store.

The system will store structured metadata and vector embeddings within the same PostgreSQL database.

---

## Rationale

The decision is based on the following advantages:

- Seamless integration with PostgreSQL
- ACID-compliant transactions
- Ability to combine SQL filtering with vector search
- Simplified infrastructure management
- Open-source and self-hosted
- Lower operational cost
- Mature PostgreSQL ecosystem

Using a single database avoids the complexity of synchronizing data between a relational database and an external vector database.

---

## Alternatives Considered

### Pinecone

Advantages

- Fully managed
- Excellent scalability
- Optimized for vector search

Disadvantages

- Vendor lock-in
- Additional operational cost
- Metadata joins require separate storage

---

### Weaviate

Advantages

- Native vector database
- Rich search capabilities

Disadvantages

- Additional infrastructure
- Higher operational complexity

---

### Qdrant

Advantages

- High-performance vector search
- Lightweight deployment

Disadvantages

- Requires maintaining a separate database
- Metadata integration is less seamless than PostgreSQL

---

## Consequences

### Positive

- Simpler architecture
- Lower maintenance cost
- Unified storage layer
- Easier backups and migrations
- Strong SQL capabilities

### Negative

- Slightly lower vector search performance than specialized vector databases for extremely large datasets
- Future scaling may require dedicated vector infrastructure

---

## Review

The decision will be revisited if dataset size or query volume exceeds the practical limits of PostgreSQL with pgvector.

