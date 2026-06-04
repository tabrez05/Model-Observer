from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    PROJECT_NAME: str = "ML Experiment Tracker"
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://ml_tracker:changeme@localhost:5432/ml_tracker"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # MinIO
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin123"
    MINIO_BUCKET: str = "ml-artifacts"

    # Stream settings
    REDIS_STREAM_MAXLEN: int = 1000       # max entries per run stream
    PERSIST_EVERY_N_STEPS: int = 10       # write Redis → PG every N steps
    SSE_HEARTBEAT_INTERVAL: float = 5.0  # seconds between SSE heartbeats

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]


settings = Settings()
