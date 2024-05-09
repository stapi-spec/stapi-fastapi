from pydantic import PositiveInt
from pydantic_settings import BaseSettings


class DeploymentProfile(BaseSettings):
    memory: PositiveInt = 1024
    timeout: PositiveInt = 30
    aws_ecr_repository_arn: str
    image_tag_or_digest: str = "latest"
    backend_name: str = "stapi_fastapi_landsat:LandsatBackend"
