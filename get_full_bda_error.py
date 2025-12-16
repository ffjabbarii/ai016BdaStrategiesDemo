#!/usr/bin/env python3
"""
Get the full BDA error message to understand what's wrong
"""

import boto3
import time
from botocore.exceptions import ClientError

def get_full_bda_error():
    """Get the complete BDA error message"""
    
    print("🔍 GETTING FULL BDA ERROR MESSAGE")
    print("=" * 50)
    
    runtime_client = boto3.client('bedrock-data-automation-runtime', region_name='us-east-1')
    s3_client = boto3.client('s3', region_name='us-east-1')
    
    # Create test setup
    test_bucket = f"bda-error-test-{int(time.time())}"
    
    try:
        s3_client.create_bucket(Bucket=test_bucket)
        
        test_content = "Test content for error analysis"
        test_key = "test.txt"
        s3_client.put_object(
            Bucket=test_bucket,
            Key=test_key,
            Body=test_content.encode('utf-8'),
            ContentType='text/plain'
        )
        
        input_s3_uri = f"s3://{test_bucket}/{test_key}"
        output_s3_uri = f"s3://{test_bucket}/output/"
        
        print(f"📤 Test setup: {input_s3_uri}")
        
        # Test the most likely profile ARN and get full error
        profile_arn = "arn:aws:bedrock:us-east-1:aws:data-automation-profile/default"
        
        print(f"\n🧪 Testing profile ARN: {profile_arn}")
        
        try:
            response = runtime_client.invoke_data_automation_async(
                inputConfiguration={'s3Uri': input_s3_uri},
                outputConfiguration={'s3Uri': output_s3_uri},
                dataAutomationProfileArn=profile_arn
            )
            
            print(f"✅ Unexpected success!")
            print(f"Response: {response}")
            
        except ClientError as e:
            print(f"\n❌ FULL ERROR DETAILS:")
            print(f"Error Code: {e.response.get('Error', {}).get('Code', 'Unknown')}")
            print(f"Error Message: {e.response.get('Error', {}).get('Message', 'Unknown')}")
            print(f"HTTP Status: {e.response.get('ResponseMetadata', {}).get('HTTPStatusCode', 'Unknown')}")
            print(f"Request ID: {e.response.get('ResponseMetadata', {}).get('RequestId', 'Unknown')}")
            
            # Print the full response
            print(f"\nFull Error Response:")
            print(f"{e.response}")
            
            # Check if it's a pattern validation error
            error_message = e.response.get('Error', {}).get('Message', '')
            
            if 'regular expression pattern' in error_message:
                print(f"\n🎯 PATTERN VALIDATION ERROR DETECTED")
                print(f"The ARN format doesn't match the expected pattern")
                
                # Extract the pattern if mentioned
                if 'arn:aws' in error_message:
                    print(f"Look for the correct pattern in the error message above")
            
            elif 'At least one' in error_message:
                print(f"\n🎯 MISSING PARAMETER ERROR DETECTED")
                print(f"Some required parameter is missing")
            
            elif 'does not exist' in error_message or 'not found' in error_message:
                print(f"\n🎯 RESOURCE NOT FOUND ERROR")
                print(f"The profile ARN doesn't exist")
            
            else:
                print(f"\n🎯 OTHER ERROR TYPE")
                print(f"This might give us a clue about what's expected")
        
        except Exception as e:
            print(f"❌ Unexpected error type: {type(e).__name__}")
            print(f"Error: {str(e)}")
        
        # Clean up
        s3_client.delete_object(Bucket=test_bucket, Key=test_key)
        s3_client.delete_bucket(Bucket=test_bucket)
        
    except Exception as e:
        print(f"❌ Test setup failed: {str(e)}")

def test_with_project_arn():
    """Test what happens if we include dataAutomationConfiguration"""
    
    print(f"\n🧪 TESTING WITH PROJECT CONFIGURATION")
    print("=" * 50)
    
    runtime_client = boto3.client('bedrock-data-automation-runtime', region_name='us-east-1')
    s3_client = boto3.client('s3', region_name='us-east-1')
    
    # Create test setup
    test_bucket = f"bda-project-test-{int(time.time())}"
    
    try:
        s3_client.create_bucket(Bucket=test_bucket)
        
        test_content = "Test content"
        test_key = "test.txt"
        s3_client.put_object(
            Bucket=test_bucket,
            Key=test_key,
            Body=test_content.encode('utf-8'),
            ContentType='text/plain'
        )
        
        input_s3_uri = f"s3://{test_bucket}/{test_key}"
        output_s3_uri = f"s3://{test_bucket}/output/"
        project_arn = "arn:aws:bedrock:us-east-1:624706593351:data-automation-project/a07a2d75b205"
        profile_arn = "arn:aws:bedrock:us-east-1:aws:data-automation-profile/default"
        
        print(f"📤 Testing with project ARN included...")
        
        try:
            response = runtime_client.invoke_data_automation_async(
                inputConfiguration={'s3Uri': input_s3_uri},
                outputConfiguration={'s3Uri': output_s3_uri},
                dataAutomationConfiguration={
                    'dataAutomationProjectArn': project_arn
                },
                dataAutomationProfileArn=profile_arn
            )
            
            print(f"✅ Success with project ARN!")
            print(f"Response: {response}")
            
        except ClientError as e:
            print(f"❌ Still failed with project ARN:")
            print(f"Error: {e.response.get('Error', {}).get('Message', 'Unknown')}")
        
        # Clean up
        s3_client.delete_object(Bucket=test_bucket, Key=test_key)
        s3_client.delete_bucket(Bucket=test_bucket)
        
    except Exception as e:
        print(f"❌ Test setup failed: {str(e)}")

def main():
    print("🚀 BDA ERROR ANALYSIS")
    print("=" * 30)
    
    # Get full error message
    get_full_bda_error()
    
    # Test with project configuration
    test_with_project_arn()
    
    print(f"\n" + "=" * 50)
    print(f"🎯 ANALYSIS COMPLETE")
    print(f"Check the full error messages above for clues about:")
    print(f"1. The correct profile ARN format")
    print(f"2. Missing required parameters")
    print(f"3. Whether profiles need to be created first")

if __name__ == "__main__":
    main()