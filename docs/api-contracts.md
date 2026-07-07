# NeuroFlow API Contracts

## Overview

This document defines the REST API contracts for the NeuroFlow platform.

The APIs enable:

- Document ingestion
- Query execution
- Streaming responses
- Evaluation monitoring
- Pipeline management
- Fine-tuning management
- Health monitoring

All APIs communicate using JSON unless otherwise specified.

---

## Authentication

All protected endpoints require a Bearer Token.

Example:

Authorization: Bearer <JWT_TOKEN>

---

## Standard Response Format

### Success

```json
{
    "success": true,
    "data": {},
    "message": "Operation completed successfully."
}
```

### Error

```json
{
    "success": false,
    "error": {
        "code": "INVALID_REQUEST",
        "message": "Request validation failed."
    }
}
```

# POST /ingest

## Purpose

Uploads documents or URLs into the NeuroFlow knowledge base.

---

## Authentication

Bearer Token Required

---

## Rate Limit

20 requests per minute

---

## Request Body

```json
{
  "source_type": "file",
  "metadata": {
    "author": "Alice",
    "tags": ["finance", "annual-report"]
  }
}
```

For file uploads, use `multipart/form-data` with the document attached.

---

## Success Response (202 Accepted)

```json
{
  "success": true,
  "data": {
    "ingestion_id": "8f1d4c62-9e12-4ab0-a9c8-51b4d8e12345",
    "status": "processing"
  },
  "message": "Document ingestion started."
}
```

---

## Error Codes

| HTTP Status | Meaning |
|-------------|---------|
| 400 | Invalid request |
| 401 | Unauthorized |
| 413 | File too large |
| 415 | Unsupported file format |
| 429 | Too many requests |
| 500 | Internal server error |


# POST /query

## Purpose

Executes a Retrieval-Augmented Generation (RAG) query.

---

## Authentication

Bearer Token Required

---

## Rate Limit

60 requests per minute

---

## Request Body

```json
{
  "query": "Explain transformer architecture.",
  "top_k": 5,
  "filters": {
    "source": "research",
    "language": "en"
  },
  "stream": true
}
```

---

## Success Response

```json
{
  "success": true,
  "data": {
    "query_id": "e6a9f1d0-1234-5678-90ab-123456789abc",
    "answer": "Transformers use a self-attention mechanism...",
    "sources": [
      {
        "document_id": "doc_001",
        "chunk_id": "chunk_015"
      }
    ]
  }
}
```

---

## Error Codes

| HTTP Status | Meaning |
|-------------|---------|
| 400 | Invalid query |
| 401 | Unauthorized |
| 404 | No matching documents |
| 429 | Rate limit exceeded |
| 500 | Internal server error |


# GET /query/{query_id}/stream

## Purpose

Streams the generated response token-by-token using Server-Sent Events (SSE).

---

## Authentication

Bearer Token Required

---

## Rate Limit

100 requests per minute

---

## Response

Content-Type:

text/event-stream

Example:

```
data: Transformers

data: use

data: self-attention

data: ...
```

---

## Error Codes

| HTTP Status | Meaning |
|-------------|---------|
| 400 | Invalid query ID |
| 401 | Unauthorized |
| 404 | Query not found |
| 500 | Internal server error |


# GET /evaluations

## Purpose

Retrieves a paginated list of evaluation results for generated responses.

---

## Authentication

Bearer Token Required

---

## Rate Limit

30 requests per minute

---

## Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| page | Integer | Page number |
| size | Integer | Number of records per page |
| sort | String | Sort field (optional) |

Example:

GET /evaluations?page=1&size=20

---

## Success Response

```json
{
  "success": true,
  "data": {
    "page": 1,
    "size": 20,
    "total_records": 152,
    "evaluations": [
      {
        "query_id": "q_001",
        "faithfulness": 0.94,
        "answer_relevance": 0.91,
        "context_precision": 0.89,
        "context_recall": 0.92,
        "timestamp": "2026-07-07T12:30:00Z"
      }
    ]
  }
}
```

---

## Error Codes

| HTTP Status | Meaning |
|-------------|---------|
| 400 | Invalid pagination parameters |
| 401 | Unauthorized |
| 500 | Internal server error |


# GET /evaluations/aggregate

## Purpose

Returns rolling evaluation metrics across all generated responses.

---

## Authentication

Bearer Token Required

---

## Rate Limit

20 requests per minute

---

## Success Response

```json
{
  "success": true,
  "data": {
    "average_faithfulness": 0.93,
    "average_answer_relevance": 0.91,
    "average_context_precision": 0.88,
    "average_context_recall": 0.90,
    "evaluated_queries": 1205
  }
}
```

---

## Error Codes

| HTTP Status | Meaning |
|-------------|---------|
| 401 | Unauthorized |
| 500 | Internal server error |


# POST /pipelines

## Purpose

Creates a reusable Retrieval-Augmented Generation pipeline configuration.

---

## Authentication

Bearer Token Required

---

## Rate Limit

10 requests per minute

---

## Request Body

```json
{
  "name": "Default Enterprise Pipeline",
  "embedding_model": "bge-large-en",
  "chunk_size": 512,
  "chunk_overlap": 64,
  "top_k": 5
}
```

---

## Success Response

```json
{
  "success": true,
  "data": {
    "pipeline_id": "pipeline_001",
    "status": "created"
  }
}
```

---

## Error Codes

| HTTP Status | Meaning |
|-------------|---------|
| 400 | Invalid configuration |
| 401 | Unauthorized |
| 409 | Pipeline already exists |
| 500 | Internal server error |


# GET /pipelines/{id}/runs

## Purpose

Retrieves the execution history of a pipeline.

---

## Authentication

Bearer Token Required

---

## Rate Limit

30 requests per minute

---

## Success Response

```json
{
  "success": true,
  "data": {
    "pipeline_id": "pipeline_001",
    "runs": [
      {
        "run_id": "run_001",
        "status": "completed",
        "started_at": "2026-07-07T10:00:00Z",
        "completed_at": "2026-07-07T10:05:00Z"
      }
    ]
  }
}
```

---

## Error Codes

| HTTP Status | Meaning |
|-------------|---------|
| 401 | Unauthorized |
| 404 | Pipeline not found |
| 500 | Internal server error |


# POST /finetune/jobs

## Purpose

Submits a fine-tuning job using a selected dataset.

---

## Authentication

Bearer Token Required

---

## Rate Limit

5 requests per hour

---

## Request Body

```json
{
  "dataset": "dataset_v3",
  "base_model": "llama3",
  "epochs": 3
}
```

---

## Success Response

```json
{
  "success": true,
  "data": {
    "job_id": "job_102",
    "status": "queued"
  }
}
```

---

## Error Codes

| HTTP Status | Meaning |
|-------------|---------|
| 400 | Invalid dataset |
| 401 | Unauthorized |
| 409 | Job already exists |
| 500 | Internal server error |


# GET /finetune/jobs/{id}

## Purpose

Returns the status and metrics of a fine-tuning job.

---

## Authentication

Bearer Token Required

---

## Rate Limit

30 requests per minute

---

## Success Response

```json
{
  "success": true,
  "data": {
    "job_id": "job_102",
    "status": "running",
    "training_accuracy": 0.94,
    "validation_accuracy": 0.92
  }
}
```

---

## Error Codes

| HTTP Status | Meaning |
|-------------|---------|
| 401 | Unauthorized |
| 404 | Job not found |
| 500 | Internal server error |


# GET /health

## Purpose

Checks whether the NeuroFlow API is operational.

---

## Authentication

Not Required

---

## Rate Limit

Unlimited

---

## Success Response

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "vector_store": "connected"
}
```

# GET /metrics

## Purpose

Provides Prometheus-compatible metrics for monitoring system performance.

---

## Authentication

Internal Access Only

---

## Rate Limit

Unlimited

---

## Response

```
http_requests_total 1532
query_latency_seconds 0.43
active_ingestions 12
evaluation_jobs_total 527
```

