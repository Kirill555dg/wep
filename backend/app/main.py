import contextlib
import logging
import typing as tp

import fastapi
import fastapi.middleware.cors as fastapi_cors

from app.api import errors as api_errors
from app.api import openapi as api_openapi
from app.api import v1 as api_v1
from app.api.middleware import request_id as request_id_middleware
from app.core import config as core_config
from app.core import logging_config as logging_config
from app.core import minio_client as minio_module

logging_config.setup_logging()
logger = logging.getLogger("app.main")


@contextlib.asynccontextmanager
async def lifespan(_application: fastapi.FastAPI) -> tp.AsyncGenerator[None, None]:
    logger.info(
        "app_started",
        extra={"app_name": core_config.settings.APP_NAME, "version": core_config.settings.APP_VERSION},
    )
    try:
        minio_module.ensure_bucket()
    except Exception as exc:
        logger.warning(f"MinIO bucket init skipped: `{exc}`")
    yield


app = fastapi.FastAPI(
    title=core_config.settings.APP_NAME,
    version=core_config.settings.APP_VERSION,
    debug=core_config.settings.DEBUG,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    fastapi_cors.CORSMiddleware,
    allow_origins=core_config.settings.BACKEND_CORS_ORIGINS,
    allow_credentials=core_config.settings.BACKEND_CORS_ALLOW_CREDENTIALS,
    allow_methods=core_config.settings.BACKEND_CORS_ALLOW_METHODS,
    allow_headers=core_config.settings.BACKEND_CORS_ALLOW_HEADERS,
    expose_headers=core_config.settings.BACKEND_CORS_EXPOSE_HEADERS,
)

app.add_middleware(request_id_middleware.RequestIdMiddleware)

api_errors.register_exception_handlers(app)
api_openapi.install_openapi_patch(app)

app.include_router(api_v1.api_router, prefix=core_config.settings.API_V1_PREFIX)


@app.get("/")
def root() -> dict[str, tp.Any]:
    return {"message": core_config.settings.APP_NAME, "version": core_config.settings.APP_VERSION, "docs": "/api/docs"}
