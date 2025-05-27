import os

import aws_cdk as cdk
from aws_cdk import (
    CfnOutput,
    Duration,
    Environment,
    RemovalPolicy,
    Stack,
    aws_apigatewayv2,
    aws_apigatewayv2_integrations,
    aws_certificatemanager,
    aws_cloudfront,
    aws_iam,
    aws_lambda,
    aws_logs,
    aws_s3,
)
from config import AppConfig
from constructs import Construct


class FederatedCollectionSearchStack(Stack):
    def __init__(  # type: ignore
        self,
        scope: Construct,
        app_config: AppConfig,
        **kwargs,
    ) -> None:
        id = f"{app_config.project_id}-{app_config.stage}"
        super().__init__(scope, id, **kwargs)

        discovery_lambda = aws_lambda.Function(
            self,
            f"{id}-lambda",
            runtime=aws_lambda.Runtime.PYTHON_3_12,
            code=aws_lambda.Code.from_docker_build(
                path="./infrastructure",
                file="Dockerfile.api",
                build_args={
                    "PYTHON_VERSION": "3.12",
                    "API_VERSION": app_config.api_version,
                },
            ),
            handler="federated_collection_discovery.main.handler",
            environment={
                "FEDERATED_STAC_API_URLS": app_config.stac_api_urls,
                "FEDERATED_CMR_URLS": app_config.cmr_urls,
            },
            memory_size=256,
            timeout=Duration.seconds(20),
            log_retention=aws_logs.RetentionDays.ONE_WEEK,
        )

        if app_config.api_domain_name and app_config.api_certificate_arn:
            api_certificate = aws_certificatemanager.Certificate.from_certificate_arn(
                self, "APICertificate", app_config.api_certificate_arn
            )
            default_domain_mapping = aws_apigatewayv2.DomainMappingOptions(
                domain_name=aws_apigatewayv2.DomainName(
                    self,
                    "ApiDomainName",
                    domain_name=app_config.api_domain_name,
                    certificate=api_certificate,
                )
            )
        else:
            default_domain_mapping = None

        discovery_api = aws_apigatewayv2.HttpApi(
            self,
            f"{id}-endpoint",
            default_integration=aws_apigatewayv2_integrations.HttpLambdaIntegration(
                f"{id}-api-integration",
                handler=discovery_lambda,
            ),
            default_domain_mapping=default_domain_mapping,
        )

        if not discovery_api.url:
            raise ValueError("there is no url associated with discovery_api!")

        CfnOutput(
            self,
            "ApiEndpoint",
            value=(
                f"https://{app_config.api_domain_name}"
                if app_config.api_domain_name
                else discovery_api.url.strip("/")
            ),
        )

        # S3 bucket and CloudFront distribution for hosting the client application
        oai = aws_cloudfront.OriginAccessIdentity(self, f"{id}-oai")
        client_bucket = aws_s3.Bucket(
            self,
            f"{id}-client-bucket",
            bucket_name=f"{id}-client-bucket",
            website_index_document="index.html",
            website_error_document="index.html",
            removal_policy=RemovalPolicy.DESTROY,
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL,
            auto_delete_objects=True,
            enforce_ssl=True,
        )

        client_bucket.add_to_resource_policy(
            aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                actions=["s3:GetObject"],
                resources=[client_bucket.arn_for_objects("*")],
                principals=[oai.grant_principal],
            )
        )
        CfnOutput(self, "ClientBucketName", value=client_bucket.bucket_name)

        if app_config.client_domain_name and app_config.client_certificate_arn:
            client_certificate = (
                aws_certificatemanager.Certificate.from_certificate_arn(
                    self, "ClientCertificate", app_config.client_certificate_arn
                )
            )
            viewer_certificate = aws_cloudfront.ViewerCertificate.from_acm_certificate(
                client_certificate, aliases=[app_config.client_domain_name]
            )
        else:
            viewer_certificate = None

        distribution = aws_cloudfront.CloudFrontWebDistribution(
            self,
            f"{id}-client-cloudfront",
            origin_configs=[
                aws_cloudfront.SourceConfiguration(
                    s3_origin_source=aws_cloudfront.S3OriginConfig(
                        s3_bucket_source=client_bucket,
                        origin_access_identity=oai,
                    ),
                    behaviors=[aws_cloudfront.Behavior(is_default_behavior=True)],
                )
            ],
            error_configurations=[
                aws_cloudfront.CfnDistribution.CustomErrorResponseProperty(
                    error_code=404, response_code=200, response_page_path="/index.html"
                )
            ],
            viewer_certificate=viewer_certificate,
            web_acl_id=app_config.web_acl_arn or None,
            logging_config=aws_cloudfront.LoggingConfiguration(
                bucket=aws_s3.Bucket.from_bucket_name(
                    self,
                    "MaapLoggingBucket",
                    f"maap-service-logging-{app_config.stage}",
                ),
                include_cookies=False,
                prefix="federated-search/",
            ),
        )
        CfnOutput(
            self,
            "CloudFrontId",
            value=distribution.distribution_id,
        )

        client_url = f"https://{distribution.distribution_domain_name}"

        CfnOutput(
            self,
            "ClientUrl",
            value=client_url,
        )


app = cdk.App()
app_config = AppConfig()

FederatedCollectionSearchStack(
    app,
    app_config=app_config,
    env=Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("AWS_REGION")
    ),
)

app.synth()
