#!/usr/bin/env python3
"""
Test BDA job creation without specifying a profile ARN
"""

import boto3
import json
import time
from botocore.exceptions import ClientError

def test_bda_without_profile():
    """Test BDA job creation without profile ARN"""
    
    print("🔍 Testing BDA Job Creation WITHOUT Profile ARN")
    print("=" * 60)
    
    # Initialize clients
    region = 'us-east-1'
    bedrock_data_automation_runtime_client = boto3.client('bedrock-data-automation-runtime', region_name=region)
    s3_client = boto3.client('s3', region_name=region)
    
    # Test project ARN
    project_arn = "arn:aws:bedrock:us-east-1:624706593351:data-automation-project/a07a2d75b205"
    print(f"🎯 Testing project: {project_arn}")
    
    # Create test S3 setup
    test_bucket = f"bda-test-no-profile-{int(time.time())}"
    
    try:
        print(f"\n📦 Creating test bucket: {test_bucket}")
        s3_client.create_bucket(Bucket=test_bucket)
        
        # Upload a small test file
        test_content = b"Test document for BDA processing"
        test_key = "test-document.txt"
        s3_client.put_object(
            Bucket=test_bucket,
            Key=test_key,
            Body=test_content,
            ContentType='text/plain'
        )
        
        input_s3_uri = f"s3://{test_bucket}/{test_key}"
        output_s3_uri = f"s3://{test_bucket}/output/"
        
        print(f"📤 Test input: {input_s3_uri}")
        print(f"📥 Test output: {output_s3_uri}")
        
        # Test 1: Try without dataAutomationProfileArn parameter
        print(f"\n🧪 Test 1: BDA job WITHOUT profile ARN parameter...")
        try:
            bda_response = bedrock_data_automation_runtime_client.invoke_data_automation_async(
                inputConfiguration={
                    's3Uri': input_s3_uri
                },
                outputConfiguration={
                    's3Uri': output_s3_uri
                },
                dataAutomationConfiguration={
                    'dataAutomationProjectArn': project_arn
                }
                # No dataAutomationProfileArn specified
            )
            
            invocation_arn = bda_response.get('invocationArn')
            print(f"✅ SUCCESS! BDA job created without profile: {invocation_arn}")
            
            # Clean up and return success
            s3_client.delete_object(Bucket=test_bucket, Key=test_key)
            s3_client.delete_bucket(Bucket=test_bucket)
            
            print(f"\n🎯 SOLUTION FOUND!")
            print(f"   Remove the dataAutomationProfileArn parameter entirely")
            print(f"   BDA will use the default profile automatically")
            return True
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            error_message = e.response.get('Error', {}).get('Message', '')
            print(f"❌ Test 1 failed: {error_code}")
            print(f"   Message: {error_message}")
        
        # Test 2: Try with empty string profile ARN
        print(f"\n🧪 Test 2: BDA job with empty profile ARN...")
        try:
            bda_response = bedrock_data_automation_runtime_client.invoke_data_automation_async(
                inputConfiguration={
                    's3Uri': input_s3_uri
                },
                outputConfiguration={
                    's3Uri': output_s3_uri
                },
                dataAutomationConfiguration={
                    'dataAutomationProjectArn': project_arn
                },
                dataAutomationProfileArn=""  # Empty string
            )
            
            invocation_arn = bda_response.get('invocation_arn')
            print(f"✅ SUCCESS! BDA job created with empty profile: {invocation_arn}")
            
            # Clean up and return success
            s3_client.delete_object(Bucket=test_bucket, Key=test_key)
            s3_client.delete_bucket(Bucket=test_bucket)
            return True
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            error_message = e.response.get('Error', {}).get('Message', '')
            print(f"❌ Test 2 failed: {error_code}")
            print(f"   Message: {error_message}")
        
        # Test 3: Check if the project has a default profile we can extract
        print(f"\n🧪 Test 3: Checking project for default profile information...")
        
        bedrock_data_automation_client = boto3.client('bedrock-data-automation', region_name=region)
        
        try:
            project_details = bedrock_data_automation_client.get_data_automation_project(
                projectArn=project_arn
            )
            
            project_config = project_details['project']
            print(f"📋 Project configuration keys: {list(project_config.keys())}")
            
            # Look for any profile-related information
            for key, value in project_config.items():
                if 'profile' in key.lower():
                    print(f"   Found profile field: {key} = {value}")
                    
                    # Try using this profile
                    if value and isinstance(value, str) and value.startswith('arn:'):
                        print(f"\n🧪 Test 3a: Using project profile: {value}")
                        try:
                            bda_response = bedrock_data_automation_runtime_client.invoke_data_automation_async(
                                inputConfiguration={
                                    's3Uri': input_s3_uri
                                },
                                outputConfiguration={
                                    's3Uri': output_s3_uri
                                },
                                dataAutomationConfiguration={
                                    'dataAutomationProjectArn': project_arn
                                },
                                dataAutomationProfileArn=value
                            )
                            
                            invocation_arn = bda_response.get('invocationArn')
                            print(f"✅ SUCCESS! BDA job created with project profile: {invocation_arn}")
                            
                            # Clean up and return success
                            s3_client.delete_object(Bucket=test_bucket, Key=test_key)
                            s3_client.delete_bucket(Bucket=test_bucket)
                            return True
                            
                        except ClientError as e:
                            error_code = e.response.get('Error', {}).get('Code', '')
                            print(f"❌ Project profile failed: {error_code}")
            
        except Exception as e:
            print(f"❌ Failed to get project details: {str(e)}")
        
        # Clean up test resources
        print(f"\n🧹 Cleaning up test resources...")
        s3_client.delete_object(Bucket=test_bucket, Key=test_key)
        s3_client.delete_bucket(Bucket=test_bucket)
        
    except Exception as e:
        print(f"❌ Test setup failed: {str(e)}")
        return False
    
    print(f"\n❌ All tests failed - BDA job creation not working")
    return False

def main():
    success = test_bda_without_profile()
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY:")
    
    if success:
        print("✅ SOLUTION FOUND - Update your code accordingly")
    else:
        print("❌ BDA job creation still failing")
        print("\n🔧 RECOMMENDATIONS:")
        print("1. Check AWS Console → Bedrock → Data Automation → Profiles")
        print("2. Verify BDA is fully enabled in your AWS account")
        print("3. Check IAM permissions for BDA operations")
        print("4. Consider contacting AWS support about BDA profile setup")

if __name__ == "__main__":
    main()