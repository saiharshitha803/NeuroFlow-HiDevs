# ADR 002: Chunking Strategy

## Status

Accepted

---

## Context

Large Language Models have context length limitations. Documents must therefore be divided into smaller chunks before generating embeddings.

Several chunking strategies were evaluated:

- Fixed-size chunking
- Sentence-boundary chunking
- Semantic chunking

---

## Decision

NeuroFlow will use **Semantic Chunking** as the default strategy.

Fallback strategies include:

- Sentence-boundary chunking
- Fixed-size chunking

---

## Rationale

Semantic chunking preserves logical meaning by grouping related sentences into coherent sections.

Compared to fixed-size chunking, it reduces context fragmentation and improves retrieval quality.

Sentence-boundary chunking is used when semantic parsing is unavailable or document structure is simple.

Fixed-size chunking is reserved for very large or poorly structured documents.

---

## Alternatives Considered

### Fixed-size Chunking

Advantages

- Fast
- Simple

Disadvantages

- Splits ideas across chunk boundaries
- Lower retrieval quality

---

### Sentence-boundary Chunking

Advantages

- Preserves sentence integrity
- Lightweight

Disadvantages

- May separate related concepts

---

### Semantic Chunking

Advantages

- Highest retrieval quality
- Better contextual coherence
- Improved LLM grounding

Disadvantages

- Computationally expensive
- Higher preprocessing time

---

## Consequences

### Positive

- Improved answer quality
- Better retrieval precision
- Reduced hallucinations

### Negative

- Longer ingestion time
- Increased preprocessing cost

---

## Switching Strategy

NeuroFlow will automatically switch to sentence-boundary or fixed-size chunking if semantic chunking becomes impractical due to document size, parser limitations or latency requirements.