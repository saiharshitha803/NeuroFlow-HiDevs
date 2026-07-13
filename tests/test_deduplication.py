from backend.pipelines.ingestion.deduplication import DeduplicationService


def test_same_content_same_hash():

    data = b"Hello NeuroFlow"

    hash1 = DeduplicationService.compute_hash(data)
    hash2 = DeduplicationService.compute_hash(data)

    assert hash1 == hash2


def test_different_content_different_hash():

    hash1 = DeduplicationService.compute_hash(b"A")
    hash2 = DeduplicationService.compute_hash(b"B")

    assert hash1 != hash2