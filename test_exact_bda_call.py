#!/usr/bin/env python3
"""
Test the exact BDA call that's failing
"""

import boto3
import time
from botocore.exceptions import ClientError

def test_exact_bda_call():
    """Test the exact BDA call from our blueprint processor"""
    
    print("🔍 TESTING EXACT BDA CALL")
    print("=" * 50)
    
    runtime_client = boto3.client('bedrock-data-automation-runtime', region_name='us-east-1')
    s3_client = boto3.client('s3', region_name='us-east-1')
    
    # Create test setup
    test_bucket = f"bda-exact-test-{int(time.time())}"
    
    try:
        s3_client.create_bucket(Bucket=test_bucket)
        
        test_content = "Test W-2 content"
        test_key = "test-w2.txt"
        s3_client.put_object(
            Bucket=test_bucket,
            Key=test_key,
            Body=test_content.encode('utf-8'),
            ContentType='text/plain'
        )
        
        input_s3_uri = f"s3://{test_bucket}/{test_key}"
        output_s3_uri = f"s3://{test_bucket}/output/"
        
        # Use the exact parameters from our blueprint processor
        project_arn = "arn:aws:bedrock:us-east-1:624706593351:data-automation-project/a07a2d75b205"
        profile_arn = "arn:aws:bedrock:us-east-1:aws:data-automation-profile/default"
        
        print(f"📤 Input: {input_s3_uri}")
        print(f"📥 Output: {output_s3_uri}")
        print(f"🎯 Project: {project_arn}")
        print(f"👤 Profile: {profile_arn}")
        
        # Test the exact call from our code
        print(f"\n🧪 Testing exact BDA call...")
        
        try:
            response = runtime_client.invoke_data_automation_async(
                inputConfiguration={
                    's3Uri': input_s3_uri
                },
                outputConfiguration={
                    's3Uri': output_s3_uri
                },
                dataAutomationConfiguration={
                    'dataAutomationProjectArn': project_arn
                },
                dataAutomationProfileArn=profile_arn
            )
            
            invocation_arn = response.get('invocationArn')
            print(f"✅ SUCCESS! BDA job created!")
            print(f"   Invocation ARN: {invocation_arn}")
            print(f"   Full response: {response}")
            
            # Clean up
            s3_client.delete_object(Bucket=test_bucket, Key=test_key)
            s3_client.delete_bucket(Bucket=test_bucket)
            
            return True
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            error_message = e.response.get('Error', {}).get('Message', '')
            
            print(f"❌ BDA call failed:")
            print(f"   Error Code: {error_code}")
            print(f"   Error Message: {error_message}")
            print(f"   Full Response: {e.response}")
            
            # Try without project ARN to isolate the issue
            print(f"\n🧪 Testing without project ARN...")
            
            try:
                response2 = runtime_client.invoke_data_automation_async(
                    inputConfiguration={
                        's3Uri': input_s3_uri
                    },
                    outputConfiguration={
                        's3Uri': output_s3_uri
                    },
                    dataAutomationProfileArn=profile_arn
                    # No dataAutomationConfiguration
                )
                
                invocation_arn2 = response2.get('invocationArn')
                print(f"✅ SUCCESS without project ARN!")
                print(f"   Invocation ARN: {invocation_arn2}")
                
                # Clean up
                s3_client.delete_object(Bucket=test_bucket, Key=test_key)
                s3_client.delete_bucket(Bucket=test_bucket)
                
                return "no_project"
                
            except ClientError as e2:
                error_code2 = e2.response.get('Error', {}).get('Code', '')
                error_message2 = e2.response.get('Error', {}).get('Message', '')
                
                print(f"❌ Also failed without project ARN:")
                print(f"   Error: {error_message2}")
                
                # Try with blueprints instead of project
                print(f"\n🧪 Testing with blueprints parameter...")
                
                try:
                    response3 = runtime_client.invoke_data_automation_async(
                        inputConfiguration={
                            's3Uri': input_s3_uri
                        },
                        outputConfiguration={
                            's3Uri': output_s3_uri
                        },
                        blueprints=[],  # Empty blueprints array
                        dataAutomationProfileArn=profile_arn
                    )
                    
                    invocation_arn3 = response3.get('invocationArn')
                    print(f"✅ SUCCESS with empty blueprints!")
                    print(f"   Invocation ARN: {invocation_arn3}")
                    
                    # Clean up
                    s3_client.delete_object(Bucket=test_bucket, Key=test_key)
                    s3_client.delete_bucket(Bucket=test_bucket)
                    
                    return "blueprints"
                    
                except ClientError as e3:
                    error_message3 = e3.response.get('Error', {}).get('Message', '')
                    print(f"❌ Also failed with blueprints: {error_message3}")
        
        # Clean up on all failures
        s3_client.delete_object(Bucket=test_bucket, Key=test_key)
        s3_client.delete_bucket(Bucket=test_bucket)
        
        return False
        
    except Exception as e:
        print(f"❌ Test setup failed: {str(e)}")
        return False

def main():
    result = test_exact_bda_call()
    
    print(f"\n" + "=" * 50)
    print(f"🎯 RESULT:")
    
    if result == True:
        print(f"✅ BDA WORKS WITH PROJECT ARN!")
        print(f"   The exact call from blueprint processor should work")
        print(f"   Check for other issues in the upload flow")
        
    elif result == "no_project":
        print(f"✅ BDA WORKS WITHOUT PROJECT ARN!")
        print(f"   Remove dataAutomationConfiguration from the call")
        print(f"   Use only the profile ARN")
        
    elif result == "blueprints":
        print(f"✅ BDA WORKS WITH BLUEPRINTS!")
        print(f"   Use blueprints=[] instead of dataAutomationConfiguration")
        
    else:
        print(f"❌ BDA STILL NOT WORKING")
        print(f"   The profile ARN or setup has other issues")
        print(f"   Check the error messages above for clues")

if __name__ == "__main__":
    main()