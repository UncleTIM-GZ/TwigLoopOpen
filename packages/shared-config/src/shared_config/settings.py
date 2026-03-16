"""Environment-based settings loaded via pydantic-settings."""

from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """PostgreSQL connection settings."""

    database_url: str = Field(
        default="postgresql+asyncpg://twigloop:twigloop@localhost:5432/twigloop",
        description="Only safe for local dev. Production MUST override via DATABASE_URL env var.",
    )

    model_config = {"env_prefix": ""}


class RedisSettings(BaseSettings):
    """Redis connection settings."""

    redis_url: str = "redis://localhost:6379/0"

    model_config = {"env_prefix": ""}


class JWTSettings(BaseSettings):
    """JWT authentication settings."""

    jwt_secret: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    model_config = {"env_prefix": ""}


class NATSSettings(BaseSettings):
    """NATS JetStream connection settings."""

    nats_url: str = "nats://localhost:4222"

    model_config = {"env_prefix": ""}


class TemporalSettings(BaseSettings):
    """Temporal workflow engine settings."""

    temporal_host: str = "localhost:7233"
    temporal_namespace: str = "twigloop"
    temporal_task_queue: str = "twigloop-workflows"

    model_config = {"env_prefix": ""}


class ClickHouseSettings(BaseSettings):
    """ClickHouse analytics database settings."""

    clickhouse_host: str = "localhost"
    clickhouse_http_port: int = 8123
    clickhouse_native_port: int = 9000
    clickhouse_db: str = "twigloop_analytics"
    clickhouse_user: str = "twigloop"
    clickhouse_password: str = "twigloop"

    model_config = {"env_prefix": ""}


class S3Settings(BaseSettings):
    """S3-compatible (MinIO) object storage settings."""

    s3_endpoint: str = "http://localhost:9010"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket: str = "twigloop"

    model_config = {"env_prefix": ""}


class AppSettings(BaseSettings):
    """Application-level settings."""

    environment: str = "local"
    debug: bool = False
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:3000"

    model_config = {"env_prefix": ""}
