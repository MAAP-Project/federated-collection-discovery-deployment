from typing import Optional

from pydantic import Field, model_validator
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)
from typing_extensions import Self


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
    api_domain_name: Optional[str] = Field(
        description="Custom domain name for the API endpoint",
        default=None,
    )
    client_domain_name: Optional[str] = Field(
        description="Custom domain name for the client application",
        default=None,
    )
    api_certificate_arn: Optional[str] = Field(
        description="arn for the certificate for the custom domains",
        default=None,
    )
    client_certificate_arn: Optional[str] = Field(
        description="arn for the certificate for the custom domains",
        default=None,
    )

    @model_validator(mode="after")
    def validate_model(self) -> Self:
        if self.api_certificate_arn is None and self.api_domain_name:
            raise ValueError(
                "If a custom domain is provided for the api, api_certificate_arn must "
                "be provided"
            )

        if self.client_certificate_arn:
            if "us-east-1" not in self.client_certificate_arn:
                raise ValueError(
                    "client_certificate_arn must be in us-east-1 for use in "
                    "CloudFront.",
                    "The provided certificate is not in us-east-1: ",
                    self.client_certificate_arn,
                )

        if self.client_certificate_arn is None and self.client_domain_name:
            raise ValueError(
                "If a custom domain is provided for the client, client_certificate_arn "
                "must be provided"
            )
        return self

    model_config = SettingsConfigDict(
        env_file=".env-cdk", yaml_file="config.yaml", extra="allow"
    )
