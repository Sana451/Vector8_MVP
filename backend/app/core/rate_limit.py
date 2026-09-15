"""Simple in-memory sliding-window rate limiter.

Process-local only: fine for a single-instance deployment, but does not
coordinate across multiple backend workers/replicas. Swap for a shared
store (e.g. Redis) if the backend ever runs as more than one process.
"""

import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, status

from app.core.config import settings


class SlidingWindowRateLimiter:
    """Tracks request timestamps per key within a rolling time window."""

    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, key: str) -> None:
        """Raise HTTP 429 if `key` has exceeded the allowed rate."""
        now = time.monotonic()
        cutoff = now - self.window_seconds

        with self._lock:
            hits = self._hits[key]
            while hits and hits[0] < cutoff:
                hits.popleft()

            if len(hits) >= self.max_requests:
                retry_after = int(hits[0] + self.window_seconds - now) + 1
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=(
                        f"Rate limit exceeded: max {self.max_requests} requests "
                        f"per {self.window_seconds}s. Try again in {retry_after}s."
                    ),
                    headers={"Retry-After": str(retry_after)},
                )

            hits.append(now)


chat_rate_limiter = SlidingWindowRateLimiter(
    max_requests=settings.CHAT_RATE_LIMIT_MAX_REQUESTS,
    window_seconds=settings.CHAT_RATE_LIMIT_WINDOW_SECONDS,
)
