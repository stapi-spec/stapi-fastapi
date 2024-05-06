import aws_cdk.aws_apigatewayv2 as apigatewayv2
import aws_cdk.aws_apigatewayv2_integrations as apigateway_integrations
import aws_cdk.aws_lambda as _lambda
from aws_cdk import App, CfnOutput, Duration, Stack
from aws_cdk import aws_logs as logs
from aws_cdk.aws_ecr import Repository
from constructs import Construct

from deploy_cdk.profile import DeploymentProfile


class LambdaService(Construct):
    function: _lambda.Function
    gateway: apigatewayv2.HttpApi

    def __init__(self, scope: Construct, id: str, profile: DeploymentProfile) -> None:
        super().__init__(scope, id)

        repository = Repository.from_repository_arn(
            self, "Repository", profile.aws_ecr_repository_arn
        )

        self.function = _lambda.Function(
            self,
            "Lambda",
            runtime=_lambda.Runtime.FROM_IMAGE,
            handler=_lambda.Handler.FROM_IMAGE,
            code=_lambda.Code.from_ecr_image(
                repository=repository,
                tag_or_digest=profile.image_tag_or_digest,
                entrypoint=["poetry", "run", "python3", "-m", "awslambdaric"],
                cmd=["lambda_handler.handler"],
                working_directory="/app",
            ),
            memory_size=profile.memory,
            timeout=Duration.seconds(profile.timeout),
            environment={"BACKEND_NAME": profile.backend_name},
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        repository.grant_pull(self.function)

        self.api = apigatewayv2.HttpApi(
            self,
            "Gateway",
            default_integration=apigateway_integrations.HttpLambdaIntegration(
                "DefaultIntegration", handler=self.function
            ),
        )


class StapiStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        profile: DeploymentProfile,
    ) -> None:
        super().__init__(scope, id)

        service = LambdaService(self, "Service", profile)
        CfnOutput(self, "Endpoint", value=service.api.url)


def main():
    app = App()
    profile = DeploymentProfile()
    StapiStack(app, f"Stapi{profile.backend_name.capitalize()}Backend", profile)
    app.synth()


if __name__ == "__main__":
    main()
