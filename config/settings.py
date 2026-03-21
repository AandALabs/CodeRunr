import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, SecretStr


class SandboxConfig(BaseModel):
    MAX_STACK_LIMIT: int = 64 * 1024
    """Max Stack limit in KB"""
    MAX_MEMORY_LIMIT: int = 256 * 1024
    """Max memory limit in KB"""
    MAX_CPU_TIME_LIMIT: float = 30
    """Max CPU time limit in seconds"""
    MAX_WALL_TIME_LIMIT: float = 30
    """Max wall time limit in seconds"""
    MAX_MAX_FILE_SIZE: int = 50 * 1024
    """Max file size in KB"""
    MAX_MAX_PROCESSES_AND_OR_THREADS: int = 64
    """Max number of process and threads"""


class Settings(BaseSettings):
    PROJECT_NAME: str = "CodeRunr"
    BASE_DIR: Path = Path(__file__).parent.parent
    API_V1_STR: str = "/api/v1"

    # Logging and monitoring
    LOG_LEVEL: str = (
        "DEBUG" if os.getenv("ENVIRONMENT", "?") == "development" else "INFO"
    )
    LOG_DIR: Path = BASE_DIR / "logs"
    LOG_FILE_NAME: str = "file.log"
    LOG_TO_FILE: bool = True
    LOG_ROTATION: str = "1 MB"
    LOG_RETENTION: str = "10 days"
    LOG_FORMAT: str = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

    NON_AUTH_PATHS: list[str] = ["/docs", "/openapi.json", "/api/v1/health"]

    # DATABASE
    POSTGRES_HOST: SecretStr
    POSTGRES_PORT: int
    POSTGRES_USER: SecretStr
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_DB: SecretStr

    # QUEUE (Redis)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Sandbox settings
    sanbox: SandboxConfig = SandboxConfig()
    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, extra="ignore"
    )


settings = Settings()
