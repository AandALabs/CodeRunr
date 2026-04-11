from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AWSConfig(BaseSettings):
    """AWS Config"""

    ACCESS_KEY_ID: SecretStr = Field(description="AWS access key id")
    SECRET_ACCESS_KEY: SecretStr = Field(description="AWS secret access key")
    REGION: str = Field(description="AWS Region")

    model_config = SettingsConfigDict(
        env_file=".env", cache_strings=True, extra="ignore", env_prefix="AWS_"
    )


aws_config = AWSConfig()
