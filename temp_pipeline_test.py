from backend.models_config.pipeline_config import PipelineConfig

config = {
    "name": "legal-research-v2",
    "description": "Optimized for legal document analysis",
    "ingestion": {
        "chunking_strategy": "hierarchical",
        "chunk_size_tokens": 400,
        "chunk_overlap_tokens": 80,
        "extractors_enabled": [
            "pdf",
            "docx",
        ],
    },
    "retrieval": {
        "dense_k": 30,
        "sparse_k": 20,
        "reranker": "cross-encoder",
        "top_k_after_rerank": 8,
        "query_expansion": True,
        "metadata_filters_enabled": True,
    },
    "generation": {
        "model_routing": {
            "task_type": "rag_generation",
            "max_cost_per_call": 0.05,
        },
        "max_context_tokens": 6000,
        "temperature": 0.2,
        "system_prompt_variant": "precise",
    },
    "evaluation": {
        "auto_evaluate": True,
        "training_threshold": 0.82,
    },
}

pipeline = PipelineConfig(**config)

print(pipeline.model_dump())