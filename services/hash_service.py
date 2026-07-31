import hashlib


def generate_hash(text: str) -> str:
    """
    Generate unique SHA256 hash for news title.
    """

    return hashlib.sha256(
        text.strip().lower().encode("utf-8")
    ).hexdigest()
