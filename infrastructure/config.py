from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class AppConfig(BaseSettings):
    project_id: str = Field(
        description="Project ID", default="federated-collection-discovery"
    )
    stage: str = Field(description="Stage of deployment", default="test")
    api_version: str = Field(
        description="Version of federated-collection-discovery "
        "application to install",
        default="0.1.0",
    )
    stac_api_urls: str = Field(
        description="Comma separated list of STAC API urls to include in the federated "
        "collection discovery app",
        default="",
    )
    cmr_urls: str = Field(
        description="Comma separated list of CMR urls to include in the federated "
        "collection discovery app",
        default="",
    )

    model_config = SettingsConfigDict(
        env_file=".env-cdk", yaml_file="config.yaml", extra="allow"
    )
