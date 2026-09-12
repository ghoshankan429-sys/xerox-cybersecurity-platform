import time
from collections import defaultdict
from typing import Dict, List
from fastapi import HTTPException, status
from app.core.config import settings


class LoginRateLimiter:
    """Sliding-window in-memory brute-force rate limiter for authentication endpoints."""

    def __init__(self, max_attempts: int = 5, window_seconds: int = 300):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self._attempts: Dict[str, List[float]] = defaultdict(list)

    def _cleanup(self, key: str, now: float) -> None:
        cutoff = now - self.window_seconds
        self._attempts[key] = [t for t in self._attempts[key] if t > cutoff]
        if not self._attempts[key]:
            self._attempts.pop(key, None)

    def check_rate_limit(self, key: str) -> None:
        now = time.time()
        self._cleanup(key, now)
        if len(self._attempts[key]) >= self.max_attempts:
            oldest_attempt = min(self._attempts[key])
            retry_after = int(self.window_seconds - (now - oldest_attempt))
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many failed login attempts. Please retry after {max(1, retry_after)} seconds.",
                headers={"Retry-After": str(max(1, retry_after))},
            )

    def record_failure(self, key: str) -> None:
        now = time.time()
        self._cleanup(key, now)
        self._attempts[key].append(now)

    def record_success(self, key: str) -> None:
        self._attempts.pop(key, None)


login_rate_limiter = LoginRateLimiter(
    max_attempts=settings.MAX_LOGIN_ATTEMPTS,
    window_seconds=settings.LOCKOUT_SECONDS,
)
