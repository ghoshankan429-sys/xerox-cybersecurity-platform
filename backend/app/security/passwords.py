import re
import bcrypt


def hash_password(password: str) -> str:
    """Hashes a password using Bcrypt with a secure random salt."""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against a Bcrypt hash in constant time."""
    try:
        password_bytes = plain_password.encode("utf-8")
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


def validate_password_strength(password: str) -> None:
    """
    Validates that a password satisfies robust complexity criteria:
    - Minimum length of 8 characters
    - At least one lowercase letter
    - At least one uppercase letter
    - At least one numerical digit
    - At least one special symbol
    """
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")

    if len(password) > 128:
        raise ValueError("Password must not exceed 128 characters.")

    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least one lowercase letter.")

    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase letter.")

    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least one numerical digit.")

    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?~`]", password):
        raise ValueError("Password must contain at least one special character.")
