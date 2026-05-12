from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.redis import get_redis


_RATE_LIMITS = {
    "/api/v1/auth/login": (5, 60),
    "/api/v1/auth/register": (3, 3600),
    "/api/v1/blast": (10, 60),
    "/api/v1/analyze/sequence": (20, 60),
    "/api/v1/tn": (30, 60),
    "/api/v1/minetn/upload": (10, 60),
}


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path

        limit = _RATE_LIMITS.get(path)
        if limit is None:
            return await call_next(request)

        max_requests, window_seconds = limit
        key = f"rate_limit:{path}:{client_ip}"

        try:
            redis = await get_redis()
            # Atomic: INCR returns the new count; set expiry only on first request
            current = await redis.incr(key)
            if current == 1:
                await redis.expire(key, window_seconds)
            if current > max_requests:
                ttl = await redis.ttl(key)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Too many requests. Retry in {ttl} seconds.",
                )
        except HTTPException:
            raise
        except Exception:
            return await call_next(request)

        return await call_next(request)
