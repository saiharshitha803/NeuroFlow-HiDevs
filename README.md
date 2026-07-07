# NeuroFlow-HiDevs

## Overview

NeuroFlow is an enterprise-grade Retrieval-Augmented Generation (RAG) platform designed to ingest, retrieve, evaluate and continuously improve knowledge-based AI systems. It supports multi-format document ingestion, hybrid retrieval, intelligent LLM routing, automated evaluation and fine-tuning workflows.

This repository contains the architecture and implementation of the NeuroFlow system.

---

## Features

- Multi-format document ingestion (PDF, DOCX, Images, CSV, URLs)
- Hybrid Retrieval (Vector Search + BM25 + Metadata Filtering)
- Reciprocal Rank Fusion (RRF)
- Cross-Encoder Re-ranking
- Token Streaming Responses
- Automated Evaluation Framework
- Fine-tuning Pipeline
- MLflow Experiment Tracking
- PostgreSQL + pgvector
- FastAPI Backend
- React Frontend

---

## Project Structure

```
NeuroFlow-HiDevs/
├── backend/
├── frontend/
├── pipelines/
├── evaluation/
├── infra/
├── docs/
└── README.md
```

---

## Tech Stack

### Backend

- FastAPI
- PostgreSQL
- pgvector
- SQLAlchemy
- Celery
- Redis

### Frontend

- React
- TypeScript
- Tailwind CSS

### Machine Learning

- Sentence Transformers
- Cross Encoder
- OpenAI / Local LLMs
- MLflow

### Infrastructure

- Docker
- Prometheus
- Grafana

---

## Current Status

- ✅ Architecture Design
- ⏳ API Implementation
- ⏳ Retrieval Engine
- ⏳ Evaluation Framework
- ⏳ Fine-Tuning Pipeline

---

## License

MIT License