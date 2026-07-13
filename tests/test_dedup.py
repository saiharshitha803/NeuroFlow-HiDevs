import asyncio

from pipelines.ingestion.dedup import compute_sha256


async def test_hash():

    hash1 = await compute_sha256(
        b"hello world"
    )

    hash2 = await compute_sha256(
        b"hello world"
    )

    assert hash1 == hash2


def test_compute_hash():

    asyncio.run(
        test_hash()
    )