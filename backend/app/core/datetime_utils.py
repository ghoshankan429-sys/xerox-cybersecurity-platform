import threading
from datetime import datetime, timezone, timedelta

_last_timestamp: datetime | None = None
_lock = threading.Lock()


def get_monotonic_utc_now() -> datetime:
    """Returns a strictly monotonic timezone-aware UTC datetime.

    Guarantees that every invocation returns a datetime strictly greater
    than any previous invocation by at least 1 microsecond, avoiding
    timestamp collisions across rapid sequential operations.
    """
    global _last_timestamp
    with _lock:
        now = datetime.now(timezone.utc)
        if _last_timestamp is not None and now <= _last_timestamp:
            now = _last_timestamp + timedelta(microseconds=1)
        _last_timestamp = now
        return now
