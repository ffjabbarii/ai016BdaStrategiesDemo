#!/usr/bin/env python3
"""
Test BDA profile ARNs directly to find the working one
"""

import boto3
import time
from botocore.exceptions import ClientError

def test_bda_profile_directly():
    """Test BDA profile ARNs directly with minimal setup"""
    
    print("🎯 TESTING BDA PROFILE ARNS DIRECTLY")
    print("=" * 50)
    
    region = 'us-east-1'
    account_id = '624706593351'
    project_arn = "arn:aws:bedrock:us-east-1:624706593351:data-automation-project/a07a2d75b205"
    
    # Initialize clients
    bedrock_data_automation_runtime_client = boto3.client('bedrock-data-automation-runtime', region_name=region)
    s3_client = boto3.client('s3', region_name=region)
    
    # Create simple test setup
    test_bucket = f"bda-direct-test-{int(time.time())}"
    
    try:
        print(f"📦 Creating test bucket: {test_bucket}")
        s3_client.create_bucket(Bucket=test_bucket)
        
        # Upload simple text content (not PDF to avoid format issues)
        test_content = "Employee Name: John Doe\nSSN: 123-45-6789\nWages: $50000"
        test_key = "simple-w2.txt"
        
        s3_client.put_object(
            Bucket=test_bucket,
            Key=test_key,
            Body=test_content.encode('utf-8'),
            ContentType='text/plain'
        )
        
        input_s3_uri = f"s3://{test_bucket}/{test_key}"
        output_s3_uri = f"s3://{test_bucket}/output/"
        
        print(f"📤 Test input: {input_s3_uri}")
        print(f"📥 Test output: {output_s3_uri}")
        
        # Test different profile ARN patterns
        profile_candidates = [
            # Standard patterns
            f"arn:aws:bedrock:{region}:{account_id}:data-automation-profile/default",
            f"arn:aws:bedrock:{region}:aws:data-automation-profile/default",
            f"arn:aws:bedrock:{region}:{account_id}:data-automation-profile/standard",
            
            # Project-based patterns
            f"arn:aws:bedrock:{region}:{account_id}:data-automation-profile/a07a2d75b205",
            
            # Service patterns
            f"arn:aws:bedrock:{region}:{account_id}:data-automation-profile/service-default",
            f"arn:aws:bedrock:{region}:{account_id}:data-automation-profile/bedrock-default",
            
            # Alternative naming
            f"arn:aws:bedrock:{region}:{account_id}:data-automation-profile/AmazonBedrockDataAutomationRole",
        ]
        
        print(f"\n🧪 Testing {len(profile_candidates)} profile ARN candidates...")
        
        for i, profile_arn in enumerate(profile_candidates, 1):
            print(f"\n🔍 Testing {i}: {profile_arn}")
            
            try:
                response = bedrock_data_automation_runtime_client.invoke_data_automation_async(
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
                print(f"✅ SUCCESS! Working profile ARN found!")
                print(f"   Profile ARN: {profile_arn}")
                print(f"   Invocation ARN: {invocation_arn}")
                
                # Clean up and return success
                s3_client.delete_object(Bucket=test_bucket, Key=test_key)
                s3_client.delete_bucket(Bucket=test_bucket)
                
                return profile_arn
                
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', '')
                error_message = e.response.get('Error', {}).get('Message', '')
                
                if error_code == 'ValidationException':
                    if 'regular expression pattern' in error_message:
                        print(f"❌ Invalid ARN format")
                    else:
                        print(f"❌ Validation error: {error_message}")
                elif error_code == 'ResourceNotFoundException':
                    print(f"❌ Profile not found")
                elif error_code == 'AccessDeniedException':
                    print(f"❌ Access denied")
                else:
                    print(f"❌ Error: {error_code} - {error_message}")
        
        # If no profiles work, the issue might be that profiles need to be created first
        print(f"\n❌ No working profile ARN found")
        print(f"🔍 Checking if profiles need to be created...")
        
        # Check AWS Console guidance
        print(f"\n📋 NEXT STEPS:")
        print(f"1. Go to AWS Console → Amazon Bedrock → Data Automation")
        print(f"2. Look for 'Profiles' or 'Configuration' section")
        print(f"3. Create a profile if the option exists")
        print(f"4. Note the exact ARN format that gets created")
        
        # Clean up
        s3_client.delete_object(Bucket=test_bucket, Key=test_key)
        s3_client.delete_bucket(Bucket=test_bucket)
        
        return None
        
    except Exception as e:
        print(f"❌ Test setup failed: {str(e)}")
        
        # Clean up on error
        try:
            s3_client.delete_object(Bucket=test_bucket, Key=test_key)
            s3_client.delete_bucket(Bucket=test_bucket)
        except:
            pass
        
        return None

def check_console_guidance():
    """Provide guidance for checking AWS Console"""
    
    print(f"\n🔧 AWS CONSOLE CHECK REQUIRED")
    print("=" * 40)
    
    print(f"Since no profile ARNs work, you need to:")
    print(f"")
    print(f"1. Open AWS Console → Amazon Bedrock → Data Automation")
    print(f"2. Look for one of these sections:")
    print(f"   - Profiles")
    print(f"   - Configuration")
    print(f"   - Settings")
    print(f"   - Project Settings")
    print(f"")
    print(f"3. If you see a 'Create Profile' option:")
    print(f"   - Create a profile named 'default'")
    print(f"   - Copy the exact ARN that gets generated")
    print(f"")
    print(f"4. If you don't see profile options:")
    print(f"   - BDA profiles might not be available in your region")
    print(f"   - Contact AWS support about BDA profile setup")
    print(f"")
    print(f"5. Alternative: Check if your BDA project has embedded profile info")

def main():
    working_profile = test_bda_profile_directly()
    
    print(f"\n" + "=" * 50)
    print(f"🎯 RESULT:")
    
    if working_profile:
        print(f"✅ FOUND WORKING PROFILE ARN!")
        print(f"   {working_profile}")
        
        print(f"\n🔧 UPDATE YOUR CODE:")
        print(f"Replace the profile ARN in blueprint_processor.py with:")
        print(f'profile_arn = "{working_profile}"')
        
        # Update the blueprint processor automatically
        try:
            with open("python/BlueprintAPI/src/blueprint_processor.py", 'r') as f:
                content = f.read()
            
            # Replace the profile ARN
            old_line = 'profile_arn = profile_candidates[0]  # default profile'
            new_line = f'profile_arn = "{working_profile}"  # working profile'
            
            if old_line in content:
                content = content.replace(old_line, new_line)
                
                with open("python/BlueprintAPI/src/blueprint_processor.py", 'w') as f:
                    f.write(content)
                
                print(f"✅ Blueprint processor updated automatically")
                print(f"🧪 Test with: python debug_bda_upload.py")
            else:
                print(f"⚠️ Manual update required in blueprint_processor.py")
        
        except Exception as e:
            print(f"❌ Auto-update failed: {str(e)}")
            print(f"   Manually update blueprint_processor.py")
    
    else:
        print(f"❌ NO WORKING PROFILE ARN FOUND")
        check_console_guidance()

if __name__ == "__main__":
    main()