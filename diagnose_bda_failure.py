#!/usr/bin/env python3
"""
Diagnose exactly why BDA job creation is failing
"""

import boto3
import json
import time
from botocore.exceptions import ClientError

def diagnose_bda_failure():
    """Diagnose the specific BDA failure"""
    
    print("🔍 Diagnosing BDA Job Creation Failure")
    print("=" * 60)
    
    # Initialize clients
    region = 'us-east-1'
    bedrock_data_automation_runtime_client = boto3.client('bedrock-data-automation-runtime', region_name=region)
    bedrock_data_automation_client = boto3.client('bedrock-data-automation', region_name=region)
    s3_client = boto3.client('s3', region_name=region)
    
    # Test project ARN from the logs
    project_arn = "arn:aws:bedrock:us-east-1:624706593351:data-automation-project/a07a2d75b205"
    print(f"🎯 Testing project: {project_arn}")
    
    # Step 1: Verify project exists and is accessible
    try:
        print("\n📋 Step 1: Verifying BDA project exists...")
        project_response = bedrock_data_automation_client.get_data_automation_project(
            projectArn=project_arn
        )
        print(f"✅ Project exists: {project_response['project']['projectName']}")
        print(f"📊 Project status: {project_response['project']['status']}")
        
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', '')
        error_message = e.response.get('Error', {}).get('Message', '')
        print(f"❌ Project verification failed: {error_code} - {error_message}")
        return
    
    # Step 2: Test different profile ARN patterns
    print("\n🔍 Step 2: Testing data automation profile ARNs...")
    
    # Extract account ID from project ARN
    account_id = project_arn.split(':')[4]
    
    profile_candidates = [
        f"arn:aws:bedrock:{region}:{account_id}:data-automation-profile/default",
        f"arn:aws:bedrock:{region}:aws:data-automation-profile/default",
        f"arn:aws:bedrock:{region}:{account_id}:data-automation-profile/standard",
        f"arn:aws:bedrock:{region}:{account_id}:data-automation-profile/a07a2d75b205"
    ]
    
    valid_profile_arn = None
    
    for i, profile_arn in enumerate(profile_candidates, 1):
        print(f"\n🧪 Testing profile {i}: {profile_arn}")
        
        # Create test S3 objects
        test_bucket = f"bda-test-{int(time.time())}"
        try:
            # Create temporary bucket
            s3_client.create_bucket(Bucket=test_bucket)
            
            # Upload a small test file
            test_content = b"Test document content"
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
            
            # Try BDA job creation with this profile
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
                    dataAutomationProfileArn=profile_arn
                )
                
                invocation_arn = bda_response.get('invocationArn')
                print(f"✅ SUCCESS! BDA job created: {invocation_arn}")
                print(f"✅ Valid profile ARN: {profile_arn}")
                valid_profile_arn = profile_arn
                
                # Clean up test bucket
                s3_client.delete_object(Bucket=test_bucket, Key=test_key)
                s3_client.delete_bucket(Bucket=test_bucket)
                
                break
                
            except ClientError as bda_error:
                error_code = bda_error.response.get('Error', {}).get('Code', '')
                error_message = bda_error.response.get('Error', {}).get('Message', '')
                print(f"❌ BDA job failed: {error_code}")
                print(f"   Message: {error_message}")
                
                # Clean up test bucket
                try:
                    s3_client.delete_object(Bucket=test_bucket, Key=test_key)
                    s3_client.delete_bucket(Bucket=test_bucket)
                except:
                    pass
                
        except Exception as setup_error:
            print(f"❌ Test setup failed: {str(setup_error)}")
            continue
    
    # Step 3: List available profiles if none worked
    if not valid_profile_arn:
        print("\n📋 Step 3: Attempting to list available profiles...")
        try:
            # Try to list profiles (this API may not exist)
            profiles_response = bedrock_data_automation_client.list_data_automation_profiles()
            print("✅ Available profiles:")
            for profile in profiles_response.get('profiles', []):
                print(f"   - {profile.get('profileArn', 'Unknown ARN')}")
                
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == 'UnknownOperationException':
                print("⚠️ list_data_automation_profiles API not available")
            else:
                print(f"❌ Failed to list profiles: {error_code}")
    
    # Step 4: Check project configuration
    print("\n🔧 Step 4: Checking project configuration...")
    try:
        project_details = bedrock_data_automation_client.get_data_automation_project(
            projectArn=project_arn
        )
        
        config = project_details['project']
        print(f"📋 Project configuration:")
        print(f"   Name: {config.get('projectName')}")
        print(f"   Status: {config.get('status')}")
        print(f"   Created: {config.get('creationTime')}")
        
        if 'standardOutputConfiguration' in config:
            print(f"   Has output config: ✅")
        else:
            print(f"   Missing output config: ❌")
            
        if 'blueprintArn' in config:
            print(f"   Blueprint ARN: {config['blueprintArn']}")
        else:
            print(f"   No custom blueprint (using default): ✅")
            
    except Exception as e:
        print(f"❌ Failed to get project details: {str(e)}")
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 DIAGNOSIS SUMMARY:")
    
    if valid_profile_arn:
        print(f"✅ SOLUTION FOUND!")
        print(f"   Use this profile ARN: {valid_profile_arn}")
        print(f"   Update your code to use this exact ARN")
    else:
        print("❌ NO VALID PROFILE ARN FOUND")
        print("   Possible issues:")
        print("   1. Data automation profiles not set up in your account")
        print("   2. Insufficient permissions for BDA operations")
        print("   3. BDA service not fully available in your region")
        print("   4. Project configuration issues")
        
    print("\n🔧 NEXT STEPS:")
    if valid_profile_arn:
        print("1. Update blueprint_processor.py to use the working profile ARN")
        print("2. Test the upload again")
    else:
        print("1. Check AWS Console → Bedrock → Data Automation → Profiles")
        print("2. Verify your AWS permissions include BDA operations")
        print("3. Consider creating a data automation profile manually")

if __name__ == "__main__":
    diagnose_bda_failure()