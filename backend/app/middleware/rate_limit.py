from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiter.
    For production, use a Redis-backed rate limiter (e.g., slowapi).
    """

    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self._clients: dict = {}

    async def dispatch(self, request: Request, call_next) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        if client_ip not in self._clients:
            self._clients[client_ip] = []

        # Remove expired timestamps
        self._clients[client_ip] = [
            t for t in self._clients[client_ip] if now - t < self.period
        ]

        if len(self._clients[client_ip]) >= self.calls:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please slow down."},
            )

        self._clients[client_ip].append(now)
        return await call_next(request)
