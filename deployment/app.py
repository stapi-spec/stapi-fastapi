import os
from typing import Any, Dict, Optional

import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2
import aws_cdk.aws_apigatewayv2_integrations_alpha as apigateway_integrations
import aws_cdk.aws_lambda as _lambda
from aws_cdk import App, CfnOutput, Duration, Stack
from aws_cdk import aws_logs as logs
from constructs import Construct


class STATDeploy(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        memory: int = 1024,
        timeout: int = 30,
        runtime: _lambda.Runtime = _lambda.Runtime.PYTHON_3_11,  # Set to 3.11 as the aws_cdk version does not have 3.12
        concurrent: Optional[int] = None,
        environment: Optional[Dict] = None,
        code_dir: str = "/",
        **kwargs: Any,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        lambda_function = _lambda.Function(
            self,
            f"{id}-lambda",
            runtime=runtime,
            code=_lambda.Code.from_docker_build(
                path=os.path.abspath(code_dir),
                file="./Dockerfile",
            ),
            handler="handler.handler",
            memory_size=memory,
            reserved_concurrent_executions=concurrent,
            timeout=Duration.seconds(timeout),
            environment=environment,
            log_retention=logs.RetentionDays.ONE_WEEK,  # Honestly can be removed not sure if required at this stage
        )

        api = apigatewayv2.HttpApi(
            self,
            f"{id}-endpoint",
            default_integration=apigateway_integrations.HttpLambdaIntegration(
                f"{id}-integration", handler=lambda_function
            ),
        )
        CfnOutput(self, "Endpoint", value=api.url)


def main():
    app = App()
    STATDeploy(app, "MyCdkProjectStack")
    app.synth()


if __name__ == "__main__":
    main()
