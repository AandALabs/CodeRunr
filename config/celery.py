from typing import Any
from kombu.utils.url import safequote
from pydantic_settings import BaseSettings, SettingsConfigDict

from config.aws import aws_config
from db.session import _build_url


class CeleryConfig(BaseSettings):
    BROKER_URL: str
    """Broker connection URL used by Celery workers."""
    BACKEND_URL: str
    """Result backend connection URL used to store task states and results."""
    BROKER_CONNECTION_RETRY_ON_STARTUP: bool = True
    """Retry broker connection during worker startup until the broker becomes available."""
    BROKER_CONNECTION_MAX_RETRIES: int = 50
    """Maximum number of initial broker connection retries before startup fails."""
    BROKER_TRANSPORT_VISIBILITY_TIMEOUT_SECONDS: int = 30
    """Seconds a fetched message stays hidden before another worker can receive it."""
    BROKER_TRANSPORT_MAX_RETRIES: int = 10
    """Maximum broker transport retry attempts for transient connection errors."""
    BROKER_TRANSPORT_RETRY_TIMEOUT_SECONDS: float = 5.0
    """Socket timeout, in seconds, used by the broker client's retry policy."""
    BROKER_TRANSPORT_POLLING_INTERVAL_SECONDS: float = 0.5
    """Delay, in seconds, between queue polling attempts when no messages are available."""
    BROKER_TRANSPORT_WALL_TIME_SECONDS_SECONDS: float = 15.0
    """SQS long polling wait time, in seconds, used to reduce empty and false-empty ReceiveMessage responses."""
    BROKER_TRANSPORT_AWS_REGION: str = aws_config.REGION
    """AWS Region for SQS queue"""
    BROKER_TRANSPORT_QUEUE_NAME_PREFIX: str = "CELERY_CODERUNR_"
    """SQS queue name prefix used to create queue"""
    TASK_SERIALIZER: str = "json"
    """Serializer used for outbound task payloads."""
    ACCEPT_CONTENT: list[str] = ["json"]
    """Content types accepted for inbound task payloads."""
    RESULT_SERIALIZER: str = "json"
    """Serializer used for task results stored in the backend."""
    RESULT_EXPIRES: int = 60 * 60 * 24
    """Seconds task results remain in the backend before Celery expires them."""
    TIMEZONE: str = "Asia/Kolkata"
    """Application timezone used by Celery for schedules and timestamps."""
    ENABLE_UTC: bool = True
    """Whether Celery stores and processes timestamps in UTC internally."""

    @property
    def broker_transport_options(self) -> dict[str, Any]:
        return {
            "visibility_timeout": self.BROKER_TRANSPORT_VISIBILITY_TIMEOUT_SECONDS,
            "max_retries": self.BROKER_TRANSPORT_MAX_RETRIES,
            "retry_policy": {
                "timeout": self.BROKER_TRANSPORT_RETRY_TIMEOUT_SECONDS,
            },
            "polling_interval": self.BROKER_TRANSPORT_POLLING_INTERVAL_SECONDS,
            "wait_time_seconds": self.BROKER_TRANSPORT_WALL_TIME_SECONDS_SECONDS,
            "region": self.BROKER_TRANSPORT_AWS_REGION,
            "queue_name_prefix": self.BROKER_TRANSPORT_QUEUE_NAME_PREFIX,
        }

    @property
    def celery_kwargs(self) -> dict[str, Any]:
        return {
            "backend": self.BACKEND_URL,
            "broker": self.BROKER_URL,
            "broker_connection_retry_on_startup": self.BROKER_CONNECTION_RETRY_ON_STARTUP,
            "broker_connection_max_retries": self.BROKER_CONNECTION_MAX_RETRIES,
            "broker_transport_options": self.broker_transport_options,
            "task_serializer": self.TASK_SERIALIZER,
            "accept_content": self.ACCEPT_CONTENT,
            "result_serializer": self.RESULT_SERIALIZER,
            "result_expires": self.RESULT_EXPIRES,
            "timezone": self.TIMEZONE,
            "enable_utc": self.ENABLE_UTC,
        }

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, extra="ignore", env_prefix="CELERY_"
    )


def _create_broker_url() -> str:
    AWS_ACCESS_KEY_ID = aws_config.ACCESS_KEY_ID.get_secret_value()
    AWS_SECRET_ACCESS_KEY = aws_config.SECRET_ACCESS_KEY.get_secret_value()

    # URL-encode ONLY for broker URL
    aws_access_key_encoded = safequote(AWS_ACCESS_KEY_ID)
    aws_secret_key_encoded = safequote(AWS_SECRET_ACCESS_KEY)

    # Use encoded credentials in broker URL
    return f"sqs://{aws_access_key_encoded}:{aws_secret_key_encoded}@"


def _create_backend_url() -> str:
    return _build_url("db+postgresql")


celery_config = CeleryConfig(
    BROKER_URL=_create_broker_url(), BACKEND_URL=_create_backend_url()
)
