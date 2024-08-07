#!/usr/bin/env python3

import aws_cdk as cdk


from aws_cdk import (
    Stack,
)
from constructs import Construct

from config import AppConfig


class FederatedCollectionSearchStack(Stack):
    def __init__(self, scope: Construct, app_config: AppConfig, **kwargs) -> None:
        super().__init__(scope, app_config.project_id, **kwargs)

        # The code that defines your stack goes here

        # example resource
        # queue = sqs.Queue(
        #     self, "CdkQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )


app = cdk.App()
app_config = AppConfig()

FederatedCollectionSearchStack(
    app,
    app_config=app_config,
)

app.synth()
