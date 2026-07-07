# NeuroFlow Data Models

## Overview

The NeuroFlow platform stores structured metadata, vector embeddings, query history, evaluation results, pipeline configurations and fine-tuning experiments.

The data model is designed to support:

- Multi-format document ingestion
- Hybrid retrieval
- Evaluation tracking
- Fine-tuning workflows
- Pipeline management
- Model versioning

---

# Entity Relationship Diagram

```text
                +----------------+
                |   Document     |
                +----------------+
                        |
                        | 1
                        |
                        | N
                +----------------+
                |     Chunk      |
                +----------------+
                        |
                        | 1
                        |
                        | 1
                +----------------+
                |   Embedding    |
                +----------------+

Document
     |
     | N
     |
Query -----------+
     |           |
     |           |
     ▼           ▼
Generation Log  Evaluation

Pipeline -------- Pipeline Run

FineTune Job ---- Model Registry
```

---

# 1. Document

Represents an uploaded document.

| Field | Type | Description |
|-------|------|-------------|
| document_id | UUID | Primary key |
| filename | String | Original file name |
| source_type | String | PDF, DOCX, Image, CSV, URL |
| author | String | Document author |
| language | String | Document language |
| upload_time | Timestamp | Upload timestamp |
| tags | JSON | User-defined tags |
| status | String | Processing status |

---

# 2. Chunk

Represents a section of a document.

| Field | Type | Description |
|-------|------|-------------|
| chunk_id | UUID | Primary key |
| document_id | UUID | Foreign key |
| chunk_index | Integer | Position within document |
| text | Text | Chunk content |
| token_count | Integer | Number of tokens |
| metadata | JSON | Chunk metadata |

Relationship

- One Document → Many Chunks

---

# 3. Embedding

Stores vector embeddings for chunks.

| Field | Type | Description |
|-------|------|-------------|
| embedding_id | UUID | Primary key |
| chunk_id | UUID | Foreign key |
| vector | Vector | pgvector embedding |
| embedding_model | String | Model used |
| created_at | Timestamp | Creation time |

Relationship

- One Chunk → One Embedding

---

# 4. Query

Represents a user query.

| Field | Type | Description |
|-------|------|-------------|
| query_id | UUID | Primary key |
| query_text | Text | User question |
| user_id | UUID | User identifier |
| created_at | Timestamp | Query timestamp |

---

# 5. Generation Log

Stores every generated response.

| Field | Type | Description |
|-------|------|-------------|
| generation_id | UUID | Primary key |
| query_id | UUID | Foreign key |
| model_name | String | Selected LLM |
| prompt | Text | Final prompt |
| response | Text | Generated answer |
| latency_ms | Integer | Response latency |
| token_usage | Integer | Total tokens |
| created_at | Timestamp | Generation time |

Relationship

- One Query → One Generation Log

---

# 6. Evaluation

Stores quality metrics for generated responses.

| Field | Type | Description |
|-------|------|-------------|
| evaluation_id | UUID | Primary key |
| query_id | UUID | Foreign key |
| faithfulness | Float | 0–1 score |
| answer_relevance | Float | 0–1 score |
| context_precision | Float | 0–1 score |
| context_recall | Float | 0–1 score |
| user_rating | Integer | Rating (1–5) |
| evaluated_at | Timestamp | Evaluation time |

Relationship

- One Query → One Evaluation

---

# 7. Pipeline Configuration

Stores reusable RAG pipeline settings.

| Field | Type | Description |
|-------|------|-------------|
| pipeline_id | UUID | Primary key |
| name | String | Pipeline name |
| embedding_model | String | Embedding model |
| chunk_size | Integer | Chunk size |
| chunk_overlap | Integer | Chunk overlap |
| top_k | Integer | Retrieved chunks |
| created_at | Timestamp | Creation timestamp |

---

# 8. Pipeline Run

Stores execution history for pipelines.

| Field | Type | Description |
|-------|------|-------------|
| run_id | UUID | Primary key |
| pipeline_id | UUID | Foreign key |
| status | String | Running / Completed / Failed |
| started_at | Timestamp | Start time |
| completed_at | Timestamp | Completion time |

Relationship

- One Pipeline → Many Runs

---

# 9. Fine-Tune Job

Stores fine-tuning experiments.

| Field | Type | Description |
|-------|------|-------------|
| job_id | UUID | Primary key |
| base_model | String | Base LLM |
| dataset_version | String | Dataset used |
| status | String | Queued / Running / Completed |
| training_accuracy | Float | Training accuracy |
| validation_accuracy | Float | Validation accuracy |
| created_at | Timestamp | Submission time |

---

# 10. Model Registry

Tracks deployed models.

| Field | Type | Description |
|-------|------|-------------|
| model_id | UUID | Primary key |
| model_name | String | Registered model |
| version | String | Version number |
| deployment_status | String | Active / Archived |
| evaluation_score | Float | Overall score |
| registered_at | Timestamp | Registration time |

Relationship

- One Fine-Tune Job → One Registered Model

---

# Summary

The NeuroFlow data model separates concerns across documents, retrieval, generation, evaluation, pipelines  and model management. This modular design simplifies scaling, maintenance  and future feature additions while supporting enterprise-grade Retrieval-Augmented Generation workflows.


