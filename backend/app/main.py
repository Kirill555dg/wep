"""
FastAPI application entry point
"""

import typing as tp

import logging
import inspect

import fastapi
from fastapi.middleware import cors as fastapi_cors
import redis.asyncio as redis_asyncio

from app.api import errors as api_errors
from app.api import openapi as api_openapi
from app.api.middleware import request_id as request_id_middleware
from app.api import v1 as api_v1
from app.core import config as core_config
from app.core import logging_config as logging_config
from app.realtime import connection_manager as connection_manager_module
from app.realtime import redis_pubsub as redis_pubsub_module

# Configure logging as early as possible.
logging_config.setup_logging()
logger = logging.getLogger("app.main")

# Create FastAPI application
app = fastapi.FastAPI(
    title=core_config.settings.APP_NAME,
    version=core_config.settings.APP_VERSION,
    debug=core_config.settings.DEBUG,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Configure CORS
app.add_middleware(
    fastapi_cors.CORSMiddleware,
    allow_origins=core_config.settings.BACKEND_CORS_ORIGINS,
    allow_credentials=core_config.settings.BACKEND_CORS_ALLOW_CREDENTIALS,
    allow_methods=core_config.settings.BACKEND_CORS_ALLOW_METHODS,
    allow_headers=core_config.settings.BACKEND_CORS_ALLOW_HEADERS,
    expose_headers=core_config.settings.BACKEND_CORS_EXPOSE_HEADERS,
)

# Request correlation / access logging
app.add_middleware(request_id_middleware.RequestIdMiddleware)

# Domain error -> HTTP mapping
api_errors.register_exception_handlers(app)

# OpenAPI schema patching (error envelope + standard responses)
api_openapi.install_openapi_patch(app)


# Include API router
app.include_router(api_v1.api_router, prefix=core_config.settings.API_V1_PREFIX)


@app.get("/")
def root() -> dict[str, tp.Any]:
    """
    Root endpoint

    Returns:
        dict: Welcome message
    """
    return {
        "message": "Web Education Platform API",
        "version": core_config.settings.APP_VERSION,
        "docs": "/api/docs",
    }


# Database initialization (create tables)
@app.on_event("startup")
async def on_startup() -> None:
    """
    Initialize database on application startup
    """
    logger.info(
        "app_started",
        extra={
            "app_name": core_config.settings.APP_NAME,
            "debug": core_config.settings.DEBUG,
            "database_url": core_config.settings.DATABASE_URL,
        },
    )

    # Realtime: WebSocket chat fanout (multi-instance) via Redis Pub/Sub.
    app.state.chat_connection_manager = connection_manager_module.ConnectionManager()
    app.state.redis = None
    app.state.chat_broker = None

    if core_config.settings.REDIS_URL:
        redis_client = redis_asyncio.from_url(core_config.settings.REDIS_URL)
        await redis_client.ping()
        app.state.redis = redis_client
        app.state.chat_broker = redis_pubsub_module.RedisPubSubBroker(
            redis_client,
            manager=app.state.chat_connection_manager,
        )
        logger.info("redis_ready", extra={"redis_url": core_config.settings.REDIS_URL})


@app.on_event("shutdown")
async def on_shutdown() -> None:
    """
    Cleanup on application shutdown
    """
    broker = getattr(app.state, "chat_broker", None)
    if broker is not None:
        try:
            await broker.shutdown()
        except Exception:
            logger.exception("broker_shutdown_failed")

    redis_client = getattr(app.state, "redis", None)
    if redis_client is not None:
        try:
            close_fn = getattr(redis_client, "aclose", None)
            if callable(close_fn):
                await close_fn()
            else:
                maybe = redis_client.close()
                if inspect.isawaitable(maybe):
                    await maybe
        except Exception:
            logger.exception("redis_close_failed")

    logger.info("app_shutting_down", extra={"app_name": core_config.settings.APP_NAME})
