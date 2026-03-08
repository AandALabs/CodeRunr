from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    PROJECT_NAME: str = "Code Judge"
    BASE_DIR: Path = Path(__file__).parent.parent
    API_V1_STR: str = "/api/v1"

    NON_AUTH_PATHS: list[str] = ["/docs", "/openapi.json", "/api/v1/health"]

    # DATABASE
    POSTGRES_HOST: SecretStr
    POSTGRES_PORT: int
    POSTGRES_USER: SecretStr
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_DB: SecretStr

    # QUEUE (Redis)
    REDIS_URL: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
