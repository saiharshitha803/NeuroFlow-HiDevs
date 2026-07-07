# NeuroFlow Architecture

## Overview

NeuroFlow is an enterprise-grade Retrieval-Augmented Generation (RAG) platform that enables users to ingest documents from multiple sources, retrieve the most relevant information using hybrid search techniques, generate accurate responses using Large Language Models (LLMs), continuously evaluate answer quality and improve performance through automated fine-tuning.

The architecture is divided into five major subsystems:

1. Ingestion Subsystem
2. Retrieval Subsystem
3. Generation Subsystem
4. Evaluation Subsystem
5. Fine-Tuning Subsystem

Each subsystem is designed to operate independently while communicating through well-defined interfaces. This modular design improves scalability, maintainability and allows individual components to evolve without affecting the entire system.

## High-Level Architecture

```text
                        +--------------------+
                        |       User         |
                        +---------+----------+
                                  |
                                  v
                        +--------------------+
                        |  React Frontend    |
                        +---------+----------+
                                  |
                                  v
                        +--------------------+
                        |   FastAPI Backend  |
                        +---------+----------+
                                  |
             +--------------------+--------------------+
             |                    |                    |
             v                    v                    v
     Ingestion Service     Query Service      Evaluation Service
             |                    |                    |
             |                    |                    |
             +---------+----------+--------------------+
                       |
                       v
              PostgreSQL + pgvector
                       |
                       v
                 Fine-Tuning Pipeline
                       |
                       v
                  Model Registry
```

### Architecture Description

The React frontend provides an interface for document upload, querying, evaluation dashboards and pipeline management.

The FastAPI backend serves as the orchestration layer. It exposes REST APIs, validates requests, coordinates ingestion, executes retrieval pipelines, streams LLM responses, records evaluation metrics and manages fine-tuning jobs.

Persistent storage is provided by PostgreSQL with the pgvector extension, allowing both structured metadata and vector embeddings to coexist in a single database.

The evaluation subsystem continuously monitors generation quality and feeds high-quality examples into the fine-tuning subsystem, enabling NeuroFlow to improve over time.


# 1. Ingestion Subsystem

## Purpose

The Ingestion Subsystem is responsible for transforming raw data from multiple sources into structured, searchable knowledge. It accepts documents in different formats, extracts their contents, enriches them with metadata, divides them into meaningful chunks, generates vector embeddings and stores both the embeddings and metadata for efficient retrieval.

The objective of this subsystem is to ensure that every uploaded document becomes queryable regardless of its original format.

---

## Supported Input Sources

The ingestion pipeline supports multiple document types to accommodate different enterprise use cases.

| Source Type | Processing Method |
|--------------|------------------|
| PDF | Text extraction using PDF parser |
| DOCX | Document parser |
| TXT / Markdown | Direct text reading |
| CSV | Row-wise extraction |
| Images (PNG, JPG, TIFF) | OCR using Tesseract/EasyOCR |
| Web URLs | HTML scraping and content extraction |

---

## Processing Pipeline

Each uploaded document passes through a sequence of processing stages before becoming searchable.

### Stage 1 – File Upload

Users upload one or more documents through the frontend or REST API.

The backend validates:

- File type
- File size
- MIME type
- Duplicate uploads

---

### Stage 2 – Content Extraction

Different extractors are used depending on the document type.

Examples:

- PDF -- PDF parser
- DOCX -- python-docx
- Images -- OCR
- CSV -- Structured reader
- URL -- HTML parser

The output of this stage is plain text.

---

### Stage 3 – Text Cleaning

The extracted text is normalized by:

- Removing unnecessary whitespace
- Removing headers and footers (when possible)
- Normalizing Unicode characters
- Fixing line breaks
- Removing empty sections

This produces cleaner input for chunking.

---

### Stage 4 – Metadata Extraction

Metadata is extracted and stored separately.

Typical metadata includes:

- Document ID
- File name
- Source type
- Upload timestamp
- Author
- Tags
- Language
- Number of pages
- Document category

Metadata enables filtering during retrieval.

---

### Stage 5 – Chunking

Large documents cannot be embedded as a single vector.

Instead, they are divided into smaller chunks.

Default strategy:

- Semantic chunking

Fallback strategies:

- Sentence-based chunking
- Fixed-size chunking

Each chunk receives:

- Chunk ID
- Chunk index
- Parent document ID
- Text content

---

### Stage 6 – Embedding Generation

Each chunk is converted into a dense vector representation using an embedding model.

Example models include:

- BAAI/bge-large-en
- all-MiniLM-L6-v2
- OpenAI text-embedding models

The generated embeddings capture semantic meaning rather than exact keywords.

---

### Stage 7 – Vector Storage

The chunk text, metadata and embeddings are stored in PostgreSQL using the pgvector extension.

Each stored record contains:

- Chunk text
- Embedding vector
- Metadata
- Document reference

Once stored, the document becomes immediately searchable.

---

## Ingestion Data Flow

```text
                 Upload File / URL
                        │
                        ▼
              File Type Validation
                        │
                        ▼
              Content Extraction
        (PDF / DOCX / OCR / CSV / URL)
                        │
                        ▼
                 Text Cleaning
                        │
                        ▼
              Metadata Extraction
                        │
                        ▼
                  Chunking Engine
                        │
                        ▼
               Embedding Generator
                        │
                        ▼
            PostgreSQL + pgvector
                        │
                        ▼
          Searchable Knowledge Base
```

---

## Responsibilities

The Ingestion Subsystem is responsible for:

- Accepting documents from multiple sources
- Extracting readable content
- Performing OCR for images
- Cleaning and normalizing text
- Extracting metadata
- Splitting documents into chunks
- Generating vector embeddings
- Persisting embeddings and metadata
- Making documents available for retrieval



# 2. Retrieval Subsystem

## Purpose

The Retrieval Subsystem is responsible for identifying the most relevant information required to answer a user's question. Instead of relying solely on vector similarity, NeuroFlow combines semantic search, keyword search and metadata filtering to maximize retrieval quality.

The subsystem retrieves candidate chunks using multiple retrieval techniques in parallel, merges the results using Reciprocal Rank Fusion (RRF), reranks them using a Cross-Encoder model and returns the highest-quality context to the Generation Subsystem.

---

## Retrieval Strategy

NeuroFlow follows a **Hybrid Retrieval** approach consisting of:

- Semantic Vector Search
- Keyword Search (BM25)
- Metadata Filtering
- Reciprocal Rank Fusion (RRF)
- Cross-Encoder Re-ranking

This approach balances semantic understanding with exact keyword matching, improving retrieval accuracy across different query types.

---

## Retrieval Pipeline

### Step 1 – User Query

A user submits a natural language question through the frontend or REST API.

Example:

> "Explain how transformers use self-attention."

---

### Step 2 – Query Embedding

The query is converted into a dense vector using the same embedding model used during document ingestion.

This vector represents the semantic meaning of the query.

---

### Step 3 – Parallel Retrieval

Three retrieval methods execute simultaneously.

#### A. Vector Similarity Search

The query embedding is compared against stored document embeddings using cosine similarity.

Returns:

- Semantically similar chunks

---

#### B. Keyword Search (BM25)

A lexical search engine retrieves chunks containing exact keyword matches.

Useful for:

- Error codes
- Product names
- Technical terms
- Identifiers

---

#### C. Metadata Filtering

Documents can be filtered using metadata before ranking.

Examples include:

- Source
- Author
- Tags
- Document Type
- Language
- Date Range

Metadata filtering reduces the search space and improves relevance.

---

### Step 4 – Reciprocal Rank Fusion (RRF)

The ranked results from Vector Search and BM25 Search are merged using **Reciprocal Rank Fusion (RRF)**.

Rather than selecting one retrieval strategy, RRF combines rankings to produce a more robust candidate set.

Benefits include:

- Better recall
- More stable rankings
- Reduced dependency on any single retrieval method

---

### Step 5 – Cross-Encoder Re-ranking

The top candidate chunks are passed through a Cross-Encoder model.

Unlike embedding models, the Cross-Encoder evaluates the **query and document together**, producing a more accurate relevance score.

The chunks are then sorted according to these scores.

---

### Step 6 – Context Window Construction

The highest-ranked chunks are assembled into a context window.

This context window is passed to the Generation Subsystem as supporting evidence for answer generation.

---

## Retrieval Data Flow

```text
                     User Query
                          │
                          ▼
                 Query Embedding
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
 Vector Search      Keyword Search     Metadata Filter
        │                 │                 │
        └────────────┬────┴───────┬─────────┘
                     ▼
         Reciprocal Rank Fusion
                     │
                     ▼
          Cross-Encoder Re-ranker
                     │
                     ▼
             Ranked Candidate Chunks
                     │
                     ▼
          Context Window Construction
                     │
                     ▼
          Generation Subsystem
```

---

## Components

| Component | Responsibility |
|-----------|----------------|
| Query Embedder | Converts user query into embeddings |
| Vector Search | Finds semantically similar chunks |
| BM25 Search | Retrieves keyword matches |
| Metadata Filter | Narrows search using document metadata |
| Reciprocal Rank Fusion | Combines search results |
| Cross-Encoder | Produces high-quality relevance ranking |
| Context Builder | Creates the final context window |

---

## Output

The Retrieval Subsystem returns:

- Ranked document chunks
- Relevance scores
- Metadata
- Source references
- Context window ready for LLM generation

---

## Advantages

The hybrid retrieval architecture offers several benefits:

- Improved recall compared to vector search alone
- Better handling of exact keyword queries
- Reduced irrelevant context
- Higher answer quality
- Improved grounding for LLM responses
- Better performance on enterprise document collections


# 3. Generation Subsystem

## Purpose

The Generation Subsystem is responsible for producing accurate, context-aware and human-readable responses using Large Language Models (LLMs). It receives the ranked context window from the Retrieval Subsystem, constructs an optimized prompt, selects the most appropriate LLM through a routing strategy, streams the generated response to the user and logs the complete interaction for future evaluation and fine-tuning.

The primary goal of this subsystem is to ensure that every generated answer is grounded in retrieved evidence while maintaining low latency and high response quality.

---

## Generation Workflow

The generation process consists of five major stages:

1. Prompt Construction
2. Model Routing
3. LLM Response Generation
4. Token Streaming
5. Logging for Evaluation

---

## Stage 1 – Prompt Construction

The Prompt Builder combines the following information into a structured prompt:

- User query
- Retrieved context
- System instructions
- Conversation history (if available)
- Output formatting instructions

Example Prompt Structure:

```
System:
You are an AI assistant that answers questions only using the provided context.

Context:
<Retrieved Document Chunks>

Question:
<User Query>

Instructions:
- Do not hallucinate.
- Cite retrieved sources where applicable.
- If the answer is not available, clearly state that the information is not found.
```

This structured prompt helps reduce hallucinations and improves factual consistency.

---

## Stage 2 – Model Routing

Instead of sending every request to the same LLM, NeuroFlow intelligently selects the most appropriate model based on several factors.

### Routing Criteria

- Query complexity
- Context length
- Domain (general, legal, medical, technical)
- Cost constraints
- Response latency requirements
- Historical model performance

### Example Routing Matrix

| Query Type | Selected Model Tier | Reason |
|-------------|--------------------|--------|
| Simple FAQ | Small Model | Lowest cost and fastest response |
| General Document Q&A | Medium Model | Balanced performance |
| Long Document Summarization | Large Context Model | Handles long context windows |
| Complex Reasoning | Premium Model | Better reasoning capability |
| Code Generation | Code-specialized Model | Optimized for programming tasks |
| Domain-specific Queries | Fine-tuned Domain Model | Higher factual accuracy |

---

## Stage 3 – LLM Response Generation

The selected LLM receives the constructed prompt and begins generating the response.

The model generates text using:

- Retrieved context
- Prompt instructions
- Conversation history
- Internal reasoning capabilities

The response remains grounded in the supplied context to minimize hallucinations.

---

## Stage 4 – Token Streaming

Rather than waiting for the complete answer, NeuroFlow streams the generated response token by token.

Advantages include:

- Lower perceived latency
- Improved user experience
- Early cancellation support
- Better responsiveness for long answers

Streaming is implemented using **Server-Sent Events (SSE)**.

---

## Stage 5 – Interaction Logging

Every generation request is logged for evaluation and future improvement.

The log includes:

- Query ID
- User question
- Retrieved document IDs
- Prompt
- Model used
- Generated response
- Response time
- Token usage
- Timestamp

These logs are later consumed by the Evaluation and Fine-Tuning subsystems.

---

## Generation Data Flow

```text
                 Ranked Context Window
                          │
                          ▼
                  Prompt Builder
                          │
                          ▼
                   Model Router
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
     Small Model     Medium Model    Premium Model
                          │
                          ▼
                 Response Generation
                          │
                          ▼
                 Token Streaming (SSE)
                          │
                          ▼
                     User Response
                          │
                          ▼
                 Generation Log Store
```

---

## Components

| Component | Responsibility |
|-----------|----------------|
| Prompt Builder | Creates structured prompts using retrieved context |
| Model Router | Selects the optimal LLM based on routing policies |
| LLM Engine | Generates context-aware responses |
| Streaming Engine | Streams tokens in real time using SSE |
| Logging Service | Records prompts, responses, metadata and usage statistics |

---

## Output

The Generation Subsystem produces:

- Final generated answer
- Source references
- Token usage statistics
- Response latency
- Complete interaction log

---

## Advantages

The Generation Subsystem provides:

- Context-grounded responses
- Reduced hallucinations
- Dynamic model selection
- Real-time token streaming
- Comprehensive logging for evaluation
- Cost-aware and scalable inference



# 4. Evaluation Subsystem

## Purpose

The Evaluation Subsystem continuously measures the quality of every generated response to ensure that NeuroFlow produces accurate, relevant and trustworthy answers. Instead of relying solely on manual feedback, the system automatically evaluates each response using predefined quality metrics.

The evaluation process runs asynchronously after a response has been delivered to the user, ensuring that user experience is not affected by evaluation latency.

The resulting evaluation scores are stored in PostgreSQL and are later used for monitoring system performance, identifying weaknesses and selecting high-quality examples for fine-tuning.

---

## Evaluation Workflow

Every completed query passes through the following evaluation stages:

1. Retrieve generation logs
2. Evaluate faithfulness
3. Evaluate answer relevance
4. Evaluate context precision
5. Evaluate context recall
6. Store evaluation results
7. Compute rolling quality metrics

---

## Stage 1 – Retrieve Generation Logs

After a response is generated, the Evaluation Service retrieves:

- User query
- Retrieved document chunks
- Prompt
- Generated response
- Source references
- Model information
- Token usage
- User feedback (if available)

These records form the basis of automated evaluation.

---

## Stage 2 – Faithfulness Evaluation

Faithfulness measures whether the generated response is supported by the retrieved context.

Questions considered include:

- Are all claims grounded in retrieved documents?
- Did the model hallucinate information?
- Are unsupported statements present?

The score ranges from **0.0 to 1.0**.

A higher score indicates that the answer is well grounded in the retrieved evidence.

---

## Stage 3 – Answer Relevance

Answer relevance measures how effectively the response addresses the user's original question.

The evaluation considers:

- Completeness
- Directness
- Accuracy
- Question coverage

The score ranges from **0.0 to 1.0**.

---

## Stage 4 – Context Precision

Context precision evaluates how much of the retrieved context was actually useful.

High precision means:

- Most retrieved chunks contributed to the answer.

Low precision indicates:

- Many retrieved chunks were unnecessary.

Improving precision reduces token usage and inference costs.

---

## Stage 5 – Context Recall

Context recall measures whether the retrieval system successfully found all important supporting information.

Low recall may indicate:

- Missing evidence
- Poor retrieval quality
- Incorrect chunking
- Weak embeddings

Improving recall increases answer completeness.

---

## Stage 6 – Store Evaluation Results

The evaluation results are persisted in PostgreSQL.

Each record contains:

- Query ID
- Model Name
- Faithfulness Score
- Answer Relevance Score
- Context Precision Score
- Context Recall Score
- Evaluation Timestamp
- User Rating (if available)

These records support dashboards, reporting and continuous monitoring.

---

## Stage 7 – Rolling Aggregation

The Evaluation Service continuously computes rolling metrics over different time windows.

Examples include:

- Hourly averages
- Daily averages
- Weekly averages
- Monthly trends

These metrics help identify performance regressions and monitor system improvements over time.

---

## Evaluation Data Flow

```text
              Generation Log
                     │
                     ▼
          Retrieve Query & Context
                     │
                     ▼
          Faithfulness Evaluation
                     │
                     ▼
         Answer Relevance Evaluation
                     │
                     ▼
         Context Precision Evaluation
                     │
                     ▼
          Context Recall Evaluation
                     │
                     ▼
          Store Scores (PostgreSQL)
                     │
                     ▼
       Rolling Quality Aggregation
                     │
                     ▼
         Dashboards & Monitoring
```

---

## Evaluation Metrics

| Metric | Purpose |
|---------|---------|
| Faithfulness | Measures whether answers are grounded in retrieved evidence |
| Answer Relevance | Measures how well the answer addresses the user's question |
| Context Precision | Measures whether retrieved chunks were actually useful |
| Context Recall | Measures whether all important supporting information was retrieved |

---

## Components

| Component | Responsibility |
|-----------|----------------|
| Evaluation Service | Coordinates automated evaluation |
| LLM Judge | Scores answer quality |
| Metrics Engine | Calculates evaluation metrics |
| PostgreSQL | Stores evaluation results |
| Analytics Service | Computes rolling aggregates |
| Dashboard | Displays quality trends and reports |

---

## Outputs

The Evaluation Subsystem produces:

- Individual evaluation reports
- Quality scores
- Rolling performance metrics
- Trend analysis
- High-quality training candidates

---

## Benefits

The Evaluation Subsystem enables:

- Continuous quality monitoring
- Automated regression detection
- Data-driven model improvement
- Retrieval performance optimization
- Fine-tuning dataset generation
- Enterprise-grade observability



# 5. Fine-Tuning Subsystem

## Purpose

The Fine-Tuning Subsystem enables NeuroFlow to continuously improve its performance by learning from high-quality interactions. Instead of manually creating training datasets, the system automatically identifies successful prompt-response pairs from evaluation logs, prepares them for training, tracks experiments and deploys improved models when they consistently outperform the base model.

This subsystem creates a continuous learning loop that allows the system to adapt to domain-specific knowledge and evolving user requirements.

---

## Fine-Tuning Workflow

The fine-tuning pipeline consists of the following stages:

1. Extract evaluation logs
2. Filter high-quality examples
3. Generate JSONL training dataset
4. Submit fine-tuning job
5. Track experiments in MLflow
6. Evaluate trained model
7. Register the best-performing model
8. Route future queries to the improved model

---

## Stage 1 – Extract Evaluation Logs

The subsystem periodically scans the Evaluation Database for completed interactions.

Each record contains:

- User query
- Retrieved context
- Prompt
- Generated response
- Evaluation metrics
- User feedback
- Model information

These records form the candidate dataset for fine-tuning.

---

## Stage 2 – Quality Filtering

Not every interaction is suitable for training.

NeuroFlow selects only high-quality examples using predefined quality thresholds.

Selection Criteria:

- Faithfulness > 0.80
- User Rating ≥ 4
- No detected hallucinations
- Complete response
- Successful retrieval

Only records satisfying all conditions are included in the training dataset.

---

## Stage 3 – JSONL Dataset Generation

Selected examples are converted into the JSONL format required by most fine-tuning APIs.

Example:

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Explain vector databases."
    },
    {
      "role": "assistant",
      "content": "Vector databases store high-dimensional embeddings..."
    }
  ]
}
```

Each line in the JSONL file represents one training example.

---

## Stage 4 – Fine-Tuning Job Submission

The generated dataset is submitted to the selected model provider for fine-tuning.

Typical configuration includes:

- Base model
- Dataset version
- Hyperparameters
- Training epochs
- Learning rate
- Batch size

Each submission creates a new training job with a unique identifier.

---

## Stage 5 – Experiment Tracking

Every fine-tuning experiment is tracked using MLflow.

The following information is recorded:

- Experiment ID
- Dataset version
- Base model
- Training configuration
- Training metrics
- Validation metrics
- Final model version

This enables reproducibility and comparison between experiments.

---

## Stage 6 – Model Evaluation

After training, the newly fine-tuned model is evaluated against the base model using benchmark datasets.

Evaluation criteria include:

- Faithfulness
- Answer Relevance
- Context Precision
- Context Recall
- Response Latency
- Token Cost

The model must demonstrate consistent improvements before deployment.

---

## Stage 7 – Model Registry

If the fine-tuned model outperforms the existing production model, it is registered as the preferred version.

The registry maintains:

- Model version
- Deployment status
- Performance metrics
- Rollback information

This ensures controlled model deployment and version management.

---

## Stage 8 – Intelligent Model Routing

Future user queries are routed to the fine-tuned model whenever it demonstrates better performance for similar query types.

Routing decisions consider:

- Query domain
- Historical accuracy
- Cost
- Latency
- Model specialization

This ensures users always receive responses from the most appropriate model.

---

## Fine-Tuning Data Flow

```text
            Evaluation Database
                    │
                    ▼
        Extract Candidate Examples
                    │
                    ▼
         Quality Filtering Engine
                    │
                    ▼
         JSONL Dataset Generator
                    │
                    ▼
         Fine-Tuning Job Submission
                    │
                    ▼
          MLflow Experiment Tracking
                    │
                    ▼
            Model Evaluation
                    │
          ┌─────────┴─────────┐
          │                   │
          ▼                   ▼
    Better Performance    Lower Performance
          │                   │
          ▼                   ▼
    Register Model       Discard Model
          │
          ▼
 Intelligent Model Routing
```

---

## Components

| Component | Responsibility |
|-----------|----------------|
| Dataset Extractor | Retrieves high-quality evaluation records |
| Quality Filter | Applies selection criteria |
| JSONL Generator | Builds fine-tuning datasets |
| Fine-Tuning Service | Submits training jobs |
| MLflow | Tracks experiments and metrics |
| Model Registry | Stores production-ready models |
| Model Router | Directs future queries to the best-performing model |

---

## Outputs

The Fine-Tuning Subsystem produces:

- High-quality JSONL datasets
- Fine-tuned language models
- Experiment reports
- Registered production models
- Improved routing decisions

---

## Benefits

The Fine-Tuning Subsystem enables:

- Continuous learning
- Domain adaptation
- Improved answer quality
- Reduced hallucinations
- Better model specialization
- Automated model lifecycle management
- Long-term performance improvements