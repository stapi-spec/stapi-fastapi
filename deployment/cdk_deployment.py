from aws_cdk import core
import aws_cdk.aws_lambda as lambda_
import aws_cdk.aws_ecr as ecr

from aws_cdk import core
import aws_cdk.aws_lambda as lambda_
import aws_cdk.aws_ecr as ecr
import aws_cdk.aws_apigateway as apigateway

class STATDeploy(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create an ECR repository
        repository = ecr.Repository(self, "MyRepository",
                                    removal_policy=core.RemovalPolicy.DESTROY)

        # Define the Lambda function using Docker image from ECR
        lambda_function = lambda_.Function(self, "MyLambdaFunction",
                                           code=lambda_.DockerImageCode.from_ecr(
                                               repository=repository,
                                               tag="latest"  # Use your specific tag
                                           ),
                                           handler=lambda_.Handler.FROM_IMAGE,
                                           runtime=lambda_.Runtime.FROM_IMAGE,
                                           timeout=core.Duration.seconds(900),
                                           memory_size=512)

        # Create an API Gateway to trigger the Lambda function
        api = apigateway.LambdaRestApi(self, "MyApiGateway",
                                       handler=lambda_function,
                                       proxy=False)

        # Define a single GET method
        example_resource = api.root.add_resource("example")
        example_resource.add_method("GET")  # Integrates the GET method with Lambda function

app = core.App()
STATDeploy(app, "MyCdkProjectStack")
app.synth()
