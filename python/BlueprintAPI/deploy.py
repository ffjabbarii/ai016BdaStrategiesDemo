"""
Deployment script for Blueprint API project
"""
import boto3
import json
import zipfile
import os
from pathlib import Path

class BlueprintAPIDeployer:
    def __init__(self):
        self.lambda_client = boto3.client('lambda')
        self.apigateway_client = boto3.client('apigateway')
        self.iam_client = boto3.client('iam')
        
    def deploy(self):
        """Deploy the Blueprint API project"""
        print("Starting Blueprint API deployment...")
        
        # 1. Create IAM role
        role_arn = self._create_lambda_role()
        
        # 2. Package Lambda function
        zip_path = self._package_lambda()
        
        # 3. Create/Update Lambda function
        function_arn = self._deploy_lambda(zip_path, role_arn)
        
        # 4. Create API Gateway
        api_id = self._create_api_gateway(function_arn)
        
        print(f"Deployment complete! API Gateway ID: {api_id}")
        print(f"Lambda Function ARN: {function_arn}")
        
    def _create_lambda_role(self):
        """Create IAM role for Lambda function"""
        role_name = "BlueprintAPILambdaRole"
        
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        try:
            response = self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description="Role for Blueprint API Lambda function"
            )
            
            # Attach policies
            self.iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
            )
            
            self.iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn="arn:aws:iam::aws:policy/AmazonTextractFullAccess"
            )
            
            return response['Role']['Arn']
            
        except Exception as e:
            print(f"Role creation error: {e}")
            # Role might already exist
            response = self.iam_client.get_role(RoleName=role_name)
            return response['Role']['Arn']
    
    def _package_lambda(self):
        """Package Lambda function code"""
        zip_path = "blueprint_api_lambda.zip"
        
        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            # Add source files
            for file_path in Path('src').rglob('*.py'):
                zip_file.write(file_path, file_path.name)
            
            # Add shared utilities
            shared_path = Path('../shared/utils')
            if shared_path.exists():
                for file_path in shared_path.rglob('*.py'):
                    zip_file.write(file_path, f"utils/{file_path.name}")
        
        return zip_path
    
    def _deploy_lambda(self, zip_path, role_arn):
        """Deploy Lambda function"""
        function_name = "blueprint-api-processor"
        
        with open(zip_path, 'rb') as zip_file:
            zip_content = zip_file.read()
        
        try:
            response = self.lambda_client.create_function(
                FunctionName=function_name,
                Runtime='python3.9',
                Role=role_arn,
                Handler='api.lambda_handler',
                Code={'ZipFile': zip_content},
                Description='Blueprint API document processor',
                Timeout=300,
                MemorySize=512
            )
            
            return response['FunctionArn']
            
        except Exception as e:
            if 'ResourceConflictException' in str(e):
                # Update existing function
                response = self.lambda_client.update_function_code(
                    FunctionName=function_name,
                    ZipFile=zip_content
                )
                return response['FunctionArn']
            else:
                raise e
    
    def _create_api_gateway(self, function_arn):
        """Create API Gateway for Lambda function"""
        # Implementation for API Gateway creation
        print("API Gateway creation would be implemented here")
        return "api-gateway-id"

if __name__ == "__main__":
    deployer = BlueprintAPIDeployer()
    deployer.deploy()