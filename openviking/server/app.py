# Copyright (c) 2026 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0
"""FastAPI application for OpenViking HTTP Server."""

import time
from contextlib import asynccontextmanager
from typing import Callable, Optional

import json
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import httpx

from openviking.server.api_keys import APIKeyManager
from openviking.server.config import ServerConfig, load_server_config, validate_server_config
from openviking.server.dependencies import set_service
from openviking.server.models import ERROR_CODE_TO_HTTP_STATUS, ErrorInfo, Response
from openviking.server.routers import (
    admin_router,
    bot_router,
    content_router,
    debug_router,
    filesystem_router,
    observer_router,
    pack_router,
    relations_router,
    resources_router,
    search_router,
    sessions_router,
    system_router,
    tasks_router,
)
from openviking.service.core import OpenVikingService
from openviking.service.task_tracker import get_task_tracker
from openviking_cli.exceptions import OpenVikingError
from openviking_cli.utils import get_logger

logger = get_logger(__name__)


class DynamicCORSMiddleware(BaseHTTPMiddleware):
    """Custom CORS middleware that supports wildcard origin with credentials."""

    def __init__(self, app: ASGIApp, allow_origins: list[str], allow_credentials: bool = True):
        super().__init__(app)
        self.allow_origins = allow_origins
        self.allow_credentials = allow_credentials

    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")
        response = await call_next(request)

        # If wildcard is configured and credentials are allowed, dynamically set the origin
        if "*" in self.allow_origins and self.allow_credentials and origin:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Vary"] = "Origin"
        elif "*" in self.allow_origins:
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Vary"] = "Origin"
        elif origin in self.allow_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Vary"] = "Origin"

        # Add other CORS headers
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "*"
        if self.allow_credentials:
            response.headers["Access-Control-Allow-Credentials"] = "true"

        return response


def create_app(
    config: Optional[ServerConfig] = None,
    service: Optional[OpenVikingService] = None,
) -> FastAPI:
    """Create FastAPI application.

    Args:
        config: Server configuration. If None, loads from default location.
        service: Pre-initialized OpenVikingService (optional).

    Returns:
        FastAPI application instance
    """
    if config is None:
        config = load_server_config()

    validate_server_config(config)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Application lifespan handler."""
        nonlocal service
        if service is None:
            service = OpenVikingService()
            await service.initialize()
            logger.info("OpenVikingService initialized")

        set_service(service)

        # Initialize APIKeyManager after service (needs AGFS)
        if config.root_api_key:
            api_key_manager = APIKeyManager(
                root_key=config.root_api_key,
                agfs_client=service._agfs,
            )
            await api_key_manager.load()
            app.state.api_key_manager = api_key_manager
            logger.info("APIKeyManager initialized")
        else:
            app.state.api_key_manager = None
            logger.warning(
                "Dev mode: no root_api_key configured, authentication disabled. "
                "This is allowed because the server is bound to localhost (%s). "
                "Do NOT expose this server to the network without configuring "
                "server.root_api_key in ov.conf.",
                config.host,
            )

        # Start TaskTracker cleanup loop
        task_tracker = get_task_tracker()
        task_tracker.start_cleanup_loop()

        yield

        # Cleanup
        task_tracker.stop_cleanup_loop()
        if service:
            await service.close()
            logger.info("OpenVikingService closed")

    app = FastAPI(
        title="OpenViking API",
        description="OpenViking HTTP Server - Agent-native context database",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.state.config = config

    # Add CORS middleware
    # Use dynamic CORS middleware to support wildcard with credentials
    allow_origins = config.cors_origins if config.cors_origins else ["*"]
    app.add_middleware(DynamicCORSMiddleware, allow_origins=allow_origins, allow_credentials=True)

    # Add request timing middleware
    @app.middleware("http")
    async def add_timing(request: Request, call_next: Callable):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

    # Add proxy middleware for /api/proxy
    @app.middleware("http")
    async def proxy_api(request: Request, call_next: Callable):
        if request.url.path.startswith("/api/proxy"):
            try:
                # Read request body
                body = await request.json()

                # Get API key from request header or from nested in body
                api_key = request.headers.get("X-API-Key")
                if not api_key and isinstance(body, dict) and isinstance(body.get("headers"), dict):
                    api_key = body.get("headers", {}).get("X-API-Key")

                # Build headers
                headers = {"Content-Type": "application/json"}
                if api_key:
                    headers["X-API-Key"] = api_key

                # Forward to OpenViking API
                async with httpx.AsyncClient() as client:
                    # Build target URL
                    target_path = body.get("path", "")
                    query_params = body.get("query", {})
                    target_url = f"http://localhost:1933{target_path}"
                    if query_params:
                        target_url += "?" + "&".join(f"{k}={v}" for k, v in query_params.items())

                    # Forward request
                    method = body.get("method", "GET").upper()
                    # Extract the actual request data (not the proxy wrapper)
                    request_data = body.get("data") if body.get("data") is not None else {}

                    if method == "GET":
                        response = await client.get(target_url, headers=headers, timeout=300.0)
                    elif method == "POST":
                        response = await client.post(target_url, headers=headers, json=request_data, timeout=300.0)
                    elif method == "PUT":
                        response = await client.put(target_url, headers=headers, json=request_data, timeout=300.0)
                    elif method == "DELETE":
                        response = await client.delete(target_url, headers=headers, json=request_data, timeout=300.0)
                    else:
                        return JSONResponse(
                            status_code=400,
                            content={"status": "error", "error": {"code": "INVALID_METHOD", "message": f"Unsupported method: {method}"}}
                        )

                    response.raise_for_status()
                    return JSONResponse(content=response.json(), status_code=response.status_code)
            except httpx.RequestError as e:
                logger.error(f"Failed to connect to OpenViking API: {e}")
                return JSONResponse(
                    status_code=502,
                    content={"status": "error", "error": {"code": "SERVICE_UNAVAILABLE", "message": f"OpenViking API unavailable: {str(e)}"}}
                )
            except httpx.HTTPStatusError as e:
                logger.error(f"OpenViking API returned error: {e}")
                try:
                    content = e.response.json()
                except:
                    content = {"status": "error", "error": {"code": "API_ERROR", "message": str(e)}}
                return JSONResponse(
                    status_code=e.response.status_code,
                    content=content
                )
            except Exception as e:
                logger.error(f"Proxy error: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"status": "error", "error": {"code": "INTERNAL", "message": str(e)}}
                )

        response = await call_next(request)
        return response

    # Add exception handler for OpenVikingError
    @app.exception_handler(OpenVikingError)
    async def openviking_error_handler(request: Request, exc: OpenVikingError):
        http_status = ERROR_CODE_TO_HTTP_STATUS.get(exc.code, 500)
        return JSONResponse(
            status_code=http_status,
            content=Response(
                status="error",
                error=ErrorInfo(
                    code=exc.code,
                    message=exc.message,
                    details=exc.details,
                ),
            ).model_dump(),
        )

    # Catch-all for unhandled exceptions so clients always get JSON
    @app.exception_handler(Exception)
    async def general_error_handler(request: Request, exc: Exception):
        logger.warning("Unhandled exception: %s", exc)
        return JSONResponse(
            status_code=500,
            content=Response(
                status="error",
                error=ErrorInfo(
                    code="INTERNAL",
                    message=str(exc),
                ),
            ).model_dump(),
        )

    # Configure Bot API if --with-bot is enabled
    if config.with_bot:
        import openviking.server.routers.bot as bot_module

        bot_module.set_bot_api_url(config.bot_api_url)
        logger.info(f"Bot API proxy enabled, forwarding to {config.bot_api_url}")
    else:
        logger.info("Bot API proxy disabled (use --with-bot to enable)")

    # Register routers
    app.include_router(system_router)
    app.include_router(admin_router)
    app.include_router(resources_router)
    app.include_router(filesystem_router)
    app.include_router(content_router)
    app.include_router(search_router)
    app.include_router(relations_router)
    app.include_router(sessions_router)
    app.include_router(pack_router)
    app.include_router(debug_router)
    app.include_router(observer_router)
    app.include_router(tasks_router)
    app.include_router(bot_router, prefix="/bot/v1")

    return app
