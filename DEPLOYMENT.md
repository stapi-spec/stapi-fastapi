# Deployment

This repository provides a [AWS Cloud Development Kit][cdk] based deployment.

## Architecture

The deployment consists of an AWS Lambda behind an AWS API Gateway. The Lambda is using a Docker image for the service code, which must be pulled from an AWS ECR.

The CDK deployment code is _not_ managing the ECR, please provide it yourself.

```
API Gateway -> Lambda -> Container Registry
```

## Prerequisites

- AWS CDK CLI
- AWS ECR with Docker image

## Deploying

### Configuration

Configuration is managed via environment variables:

- MEMORY: Lambda memory in megabytes, defaults to `1024`
- TIMEOUT: Lambda timeout in seconds, defaults to `30`
- AWS_ECR_REPOSITORY_ARN: ARN of the ECR to pull from
- IMAGE_TAG_OR_DIGEST: Docker tag or digest to pull from ECR, defaults to `latest`
- BACKEND_NAME: Backend name to use in service, defaults to `landsat`

As well, CDK will need an AWS profile to be configured.

### Execution

Having set up the configuration env vars as required, execute the CDK deployment with

```
poetry run cdk deploy
```

This will create a new CloudFormation stack named after the `BACKEND_NAME` configured, i.e. `StapiLandsatBackend`.

[cdk]: https://docs.aws.amazon.com/cdk/
