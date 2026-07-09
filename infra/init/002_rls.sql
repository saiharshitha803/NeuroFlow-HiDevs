ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE pipelines ENABLE ROW LEVEL SECURITY;
ALTER TABLE pipeline_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE evaluations ENABLE ROW LEVEL SECURITY;
ALTER TABLE training_pairs ENABLE ROW LEVEL SECURITY;
ALTER TABLE finetune_jobs ENABLE ROW LEVEL SECURITY;

CREATE POLICY documents_pipeline_policy
ON documents
FOR ALL
USING (
    pipeline_id::text =
    current_setting('app.pipeline_id', true)
);

CREATE POLICY chunks_pipeline_policy
ON chunks
FOR ALL
USING (
    document_id IN (
        SELECT id
        FROM documents
        WHERE pipeline_id::text =
        current_setting('app.pipeline_id', true)
    )
);

CREATE POLICY pipelines_policy
ON pipelines
FOR ALL
USING (
    id::text =
    current_setting('app.pipeline_id', true)
);

CREATE POLICY pipeline_runs_policy
ON pipeline_runs
FOR ALL
USING (
    pipeline_id::text =
    current_setting('app.pipeline_id', true)
);

CREATE POLICY evaluations_policy
ON evaluations
FOR ALL
USING (
    run_id IN (
        SELECT id
        FROM pipeline_runs
        WHERE pipeline_id::text =
        current_setting('app.pipeline_id', true)
    )
);

CREATE POLICY training_pairs_policy
ON training_pairs
FOR ALL
USING (
    run_id IN (
        SELECT id
        FROM pipeline_runs
        WHERE pipeline_id::text =
        current_setting('app.pipeline_id', true)
    )
);

CREATE POLICY finetune_jobs_policy
ON finetune_jobs
FOR ALL
USING (TRUE);