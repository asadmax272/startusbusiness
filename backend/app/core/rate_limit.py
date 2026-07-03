"""
Minimal in-memory sliding-window rate limiter.

Deliberately dependency-free so it doesn't require a network install to
verify. Fine for a single Railway instance. If you scale to multiple
instances, this state won't be shared between them — move to Redis
(e.g. swap the dict below for redis INCR+EXPIRE) at that point.
"""

import time
from collections import defaultdict

from fastapi import HTTPException, Request

_hits: dict[str, list[float]] = defaultdict(list)


def rate_limit(max_requests: int, window_seconds: int):
    def dependency(request: Request):
        key = f"{request.client.host if request.client else 'unknown'}:{request.url.path}"
        now = time.time()
        window_start = now - window_seconds
        _hits[key] = [t for t in _hits[key] if t > window_start]
        if len(_hits[key]) >= max_requests:
            raise HTTPException(429, "Too many requests. Please try again shortly.")
        _hits[key].append(now)

    return dependency
