import hashlib


class DeduplicationService:
    """
    Computes SHA256 hashes for uploaded content.
    """

    @staticmethod
    def compute_hash(file_bytes: bytes) -> str:
        return hashlib.sha256(file_bytes).hexdigest()