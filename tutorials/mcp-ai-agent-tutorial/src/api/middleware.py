"""FastAPI middleware for CORS, logging, etc."""

from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
import time
import logging

logger = logging.getLogger(__name__)

class TimingMiddleware:
    """Middleware to log request timing."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = time.time()

            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    process_time = time.time() - start_time
                    logger.info(f"Request completed in {process_time:.4f}s")
                await send(message)

            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)
