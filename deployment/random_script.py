import boto3
import subprocess

# AWS Configuration
region = 'your-region'
account_id = 'your-account-id'
repository_name = 'your-repository-name'
function_name = 'your-lambda-function-name'
role_arn = 'arn:aws:iam::your-account-id:role/your-lambda-role'
image_tag = 'latest'

# Create a session using your current credentials
session = boto3.Session(region_name=region)
ecr_client = session.client('ecr')
lambda_client = session.client('lambda')

def create_ecr_repository():
    try:
        response = ecr_client.create_repository(repositoryName=repository_name)
        print(f"Repository created: {response['repository']['repositoryUri']}")
    except ecr_client.exceptions.RepositoryAlreadyExistsException:
        print("Repository already exists.")

def docker_login():
    ecr_token = ecr_client.get_authorization_token()
    username, password = ecr_token['authorizationData'][0]['authorizationToken'].split(':')
    registry = ecr_token['authorizationData'][0]['proxyEndpoint']
    login_command = f"docker login --username {username} --password {password} {registry}"
    subprocess.run(login_command, shell=True, check=True)

def build_and_push_docker_image():
    repository_uri = f"{account_id}.dkr.ecr.{region}.amazonaws.com/{repository_name}"
    
    # Build the Docker image
    subprocess.run(f"docker build -t {repository_name} .", shell=True, check=True)
    
    # Tag the Docker image
    subprocess.run(f"docker tag {repository_name}:latest {repository_uri}:{image_tag}", shell=True, check=True)
    
    # Push the Docker image
    subprocess.run(f"docker push {repository_uri}:{image_tag}", shell=True, check=True)
    return f"{repository_uri}:{image_tag}"

def deploy_lambda_function(image_uri):
    try:
        response = lambda_client.create_function(
            FunctionName=function_name,
            Code={'ImageUri': image_uri},
            PackageType='Image',
            Role=role_arn,
            Timeout=900  # Modify as necessary
        )
        print(f"Lambda function created: {response['FunctionArn']}")
    except lambda_client.exceptions.ResourceConflictException:
        response = lambda_client.update_function_code(
            FunctionName=function_name,
            ImageUri=image_uri
        )
        print(f"Lambda function updated: {response['FunctionArn']}")

def main():
    create_ecr_repository()
    docker_login()
    image_uri = build_and_push_docker_image()
    deploy_lambda_function(image_uri)

if __name__ == "__main__":
    main()
