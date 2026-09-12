import hashlib
import secrets


def generate_session_token() -> str:
    """Generates a high-entropy cryptographically secure random session token."""
    return secrets.token_urlsafe(32)


def hash_session_token(token: str) -> str:
    """Computes SHA-256 digest of a session token for secure database indexing."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
