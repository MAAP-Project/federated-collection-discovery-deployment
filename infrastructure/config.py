from typing import Optional

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class AppConfig(BaseSettings):
    project_id: str = Field(
        description="Project ID", default="federated-collection-discovery-api"
    )
    stage: str = Field(description="Stage of deployment", default="test")
    stac_api_urls: Optional[str] = Field(
        description="Comma separated list of STAC API urls to include in the federated "
        "collection discovery app"
    )
    cmr_urls: Optional[str] = Field(
        description="Comma separated list of CMR urls to include in the federated "
        "collection discovery app",
        default=None,
    )

    model_config = SettingsConfigDict(
        env_file=".env-cdk", yaml_file="config.yaml", extra="allow"
    )
