#!/usr/bin/env python3
"""
Final comprehensive BDA test with all combinations
"""

import boto3
import time
from botocore.exceptions import ClientError

def final_bda_test():
    """Final test of all BDA combinations"""
    
    print("🚀 FINAL COMPREHENSIVE BDA TEST")
    print("=" * 60)
    
    runtime_client = boto3.client('bedrock-data-automation-runtime', region_name='us-east-1')
    s3_client = boto3.client('s3', region_name='us-east-1')
    
    # Correct project ARN (confirmed)
    project_arn = "arn:aws:bedrock:us-east-1:624706593351:data-automation-project/a07a2d75b205"
    
    # Different profile ARN patterns to test
    profile_patterns = [
        # AWS managed
        "arn:aws:bedrock:us-east-1:aws:data-automation-profile/default",
        
        # Account specific
        "arn:aws:bedrock:us-east-1:624706593351:data-automation-profile/default",
        
        # Project-specific (using project ID)
        "arn:aws:bedrock:us-east-1:624706593351:data-automation-profile/a07a2d75b205",
        
        # IAM role (as suggested by internet articles)
        "arn:aws:iam::624706593351:role/AmazonBedrockDataAutomationRole",
        
        # Alternative service naming
        "arn:aws:bedrock-data-automation:us-east-1:aws:profile/default",
        "arn:aws:bedrock-data-automation:us-east-1:624706593351:profile/default",
    ]
    
    # Create test setup
    test_bucket = f"bda-final-test-{int(time.time())}"
    
    try:
        s3_client.create_bucket(Bucket=test_bucket)
        
        test_content = "Final BDA test content"
        test_key = "final-test.txt"
        s3_client.put_object(
            Bucket=test_bucket,
            Key=test_key,
            Body=test_content.encode('utf-8'),
            ContentType='text/plain'
        )
        
        input_s3_uri = f"s3://{test_bucket}/{test_key}"
        output_s3_uri = f"s3://{test_bucket}/output/"
        
        print(f"📤 Test setup: {input_s3_uri}")
        print(f"🎯 Project ARN: {project_arn}")
        
        # Test each profile pattern
        for i, profile_arn in enumerate(profile_patterns, 1):
            print(f"\n🧪 Test {i}: {profile_arn}")
            
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
                print(f"✅ SUCCESS! Working combination found!")
                print(f"   Profile ARN: {profile_arn}")
                print(f"   Invocation ARN: {invocation_arn}")
                
                # Clean up and return success
                s3_client.delete_object(Bucket=test_bucket, Key=test_key)
                s3_client.delete_bucket(Bucket=test_bucket)
                
                return {
                    'success': True,
                    'profile_arn': profile_arn,
                    'project_arn': project_arn,
                    'invocation_arn': invocation_arn
                }
                
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', '')
                error_message = e.response.get('Error', {}).get('Message', '')
                
                if 'invalid' in error_message.lower():
                    print(f"❌ Invalid ARN format")
                elif 'not found' in error_message.lower():
                    print(f"❌ Profile not found")
                elif 'access denied' in error_message.lower():
                    print(f"❌ Access denied")
                else:
                    print(f"❌ {error_code}: {error_message}")
        
        # If no profile patterns work, try without dataAutomationConfiguration
        print(f"\n🧪 TESTING WITHOUT PROJECT (profile only)...")
        
        for i, profile_arn in enumerate(profile_patterns[:2], 1):  # Test top 2 patterns
            print(f"\n🧪 No-project test {i}: {profile_arn}")
            
            try:
                response = runtime_client.invoke_data_automation_async(
                    inputConfiguration={
                        's3Uri': input_s3_uri
                    },
                    outputConfiguration={
                        's3Uri': output_s3_uri
                    },
                    dataAutomationProfileArn=profile_arn
                    # No dataAutomationConfiguration
                )
                
                invocation_arn = response.get('invocationArn')
                print(f"✅ SUCCESS without project!")
                print(f"   Profile ARN: {profile_arn}")
                print(f"   Invocation ARN: {invocation_arn}")
                
                # Clean up and return success
                s3_client.delete_object(Bucket=test_bucket, Key=test_key)
                s3_client.delete_bucket(Bucket=test_bucket)
                
                return {
                    'success': True,
                    'profile_arn': profile_arn,
                    'project_arn': None,
                    'invocation_arn': invocation_arn,
                    'note': 'Works without project ARN'
                }
                
            except ClientError as e:
                error_message = e.response.get('Error', {}).get('Message', '')
                print(f"❌ {error_message}")
        
        # Clean up
        s3_client.delete_object(Bucket=test_bucket, Key=test_key)
        s3_client.delete_bucket(Bucket=test_bucket)
        
        return {'success': False, 'error': 'No working combination found'}
        
    except Exception as e:
        print(f"❌ Test setup failed: {str(e)}")
        return {'success': False, 'error': str(e)}

def update_blueprint_processor(result):
    """Update blueprint processor with working configuration"""
    
    if not result.get('success'):
        return
    
    print(f"\n🔧 UPDATING BLUEPRINT PROCESSOR")
    print("=" * 50)
    
    profile_arn = result['profile_arn']
    project_arn = result.get('project_arn')
    
    print(f"✅ Working Profile ARN: {profile_arn}")
    if project_arn:
        print(f"✅ Working Project ARN: {project_arn}")
    else:
        print(f"⚠️ Works without project ARN")
    
    # Show the exact code to use
    print(f"\n📋 UPDATE YOUR BLUEPRINT PROCESSOR:")
    
    if project_arn:
        print(f"""
bda_response = self.bedrock_data_automation_runtime_client.invoke_data_automation_async(
    inputConfiguration={{'s3Uri': permanent_s3_uri}},
    outputConfiguration={{'s3Uri': f"s3://{{project_bucket}}/bda-output/"}},
    dataAutomationConfiguration={{'dataAutomationProjectArn': '{project_arn}'}},
    dataAutomationProfileArn='{profile_arn}'
)""")
    else:
        print(f"""
bda_response = self.bedrock_data_automation_runtime_client.invoke_data_automation_async(
    inputConfiguration={{'s3Uri': permanent_s3_uri}},
    outputConfiguration={{'s3Uri': f"s3://{{project_bucket}}/bda-output/"}},
    dataAutomationProfileArn='{profile_arn}'
    # No dataAutomationConfiguration needed
)""")

def main():
    print("🎯 FINAL BDA RESOLUTION ATTEMPT")
    print("=" * 40)
    
    result = final_bda_test()
    
    print(f"\n" + "=" * 60)
    print(f"🎯 FINAL RESULT:")
    
    if result.get('success'):
        print(f"✅ BDA IS WORKING!")
        print(f"   Profile ARN: {result['profile_arn']}")
        print(f"   Invocation ARN: {result['invocation_arn']}")
        
        if result.get('note'):
            print(f"   Note: {result['note']}")
        
        update_blueprint_processor(result)
        
        print(f"\n🧪 NEXT STEP:")
        print(f"Update your blueprint processor and test with: python debug_bda_upload.py")
        
    else:
        print(f"❌ BDA STILL NOT WORKING")
        print(f"   Error: {result.get('error', 'Unknown')}")
        
        print(f"\n🔧 FINAL RECOMMENDATIONS:")
        print(f"1. BDA may not be fully available in your account/region")
        print(f"2. Contact AWS support about BDA profile setup")
        print(f"3. Check AWS Console → Bedrock → Data Automation for profile creation")
        print(f"4. Your account may need BDA service enablement")

if __name__ == "__main__":
    main()