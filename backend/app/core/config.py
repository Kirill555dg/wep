"""
Application configuration settings
"""

import pydantic_settings


class Settings(pydantic_settings.BaseSettings):
    APP_NAME: str = "Test Constructor API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "postgresql://wep_user:wep_password@127.0.0.1:5433/wep_education"

    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost",
        "http://127.0.0.1",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ]
    BACKEND_CORS_ALLOW_CREDENTIALS: bool = True
    BACKEND_CORS_ALLOW_METHODS: list[str] = ["*"]
    BACKEND_CORS_ALLOW_HEADERS: list[str] = ["Authorization", "Content-Type", "X-Request-ID"]
    BACKEND_CORS_EXPOSE_HEADERS: list[str] = ["X-Request-ID"]

    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    LOG_LEVEL: str | None = None
    LOG_JSON: bool | None = None
    LOG_COLOR: bool | None = None
    SERVICE_NAME: str = "test-constructor"

    # MinIO (S3-compatible object storage)
    MINIO_ENDPOINT: str = "127.0.0.1:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "wep-media"
    MINIO_SECURE: bool = False
    MINIO_PUBLIC_URL: str = "http://127.0.0.1:9000"

    model_config = pydantic_settings.SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
