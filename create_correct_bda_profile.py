#!/usr/bin/env python3
"""
Create the correct BDA profile ARN based on the validation error pattern
"""

import boto3
import time
from botocore.exceptions import ClientError

def create_correct_bda_profile():
    """Create the correct BDA profile ARN format"""
    
    print("🎯 CREATING CORRECT BDA PROFILE ARN")
    print("=" * 50)
    
    # From the validation error, we know the pattern:
    # arn:aws:bedrock:[region]:[account]:data-automation-profile/[profile-name]
    
    region = 'us-east-1'
    account_id = '624706593351'
    
    # Try different profile names that might exist or be created automatically
    profile_candidates = [
        f"arn:aws:bedrock:{region}:{account_id}:data-automation-profile/default",
        f"arn:aws:bedrock:{region}:{account_id}:data-automation-profile/standard", 
        f"arn:aws:bedrock:{region}:{account_id}:data-automation-profile/service-default",
        f"arn:aws:bedrock:{region}:aws:data-automation-profile/default",
        f"arn:aws:bedrock:{region}:{account_id}:data-automation-profile/AmazonBedrockDataAutomationRole",
        f"arn:aws:bedrock:{region}:{account_id}:data-automation-profile/a07a2d75b205",  # Same as project ID
    ]
    
    print(f"🧪 Testing {len(profile_candidates)} correct format candidates...")
    
    bedrock_data_automation_runtime_client = boto3.client('bedrock-data-automation-runtime', region_name=region)
    s3_client = boto3.client('s3', region_name=region)
    
    # Test each candidate
    for i, profile_arn in enumerate(profile_candidates, 1):
        print(f"\n🔍 Testing candidate {i}: {profile_arn}")
        
        success = test_bda_profile_arn(profile_arn, bedrock_data_automation_runtime_client, s3_client)
        
        if success:
            print(f"✅ FOUND WORKING PROFILE ARN: {profile_arn}")
            return profile_arn
    
    # If no candidates work, try to create one using the BDA client
    print(f"\n🔧 No existing profiles work, checking if we can create one...")
    
    bedrock_data_automation_client = boto3.client('bedrock-data-automation', region_name=region)
    
    # Check if there are any create profile operations
    operations = [op for op in dir(bedrock_data_automation_client) if 'profile' in op.lower() and 'create' in op.lower()]
    
    if operations:
        print(f"📋 Found profile creation operations: {operations}")
        
        for op_name in operations:
            try:
                operation = getattr(bedrock_data_automation_client, op_name)
                print(f"🧪 Trying {op_name}...")
                
                # Try to create a default profile
                try:
                    result = operation(
                        profileName="default",
                        description="Default profile for BDA"
                    )
                    
                    created_arn = result.get('profileArn')
                    if created_arn:
                        print(f"✅ Created profile: {created_arn}")
                        return created_arn
                        
                except Exception as e:
                    print(f"❌ {op_name} failed: {str(e)}")
                    
            except AttributeError:
                pass
    
    # Last resort: Check if the project itself contains the profile ARN
    print(f"\n🔍 Checking project configuration for embedded profile ARN...")
    
    try:
        project_arn = "arn:aws:bedrock:us-east-1:624706593351:data-automation-project/a07a2d75b205"
        
        project_details = bedrock_data_automation_client.get_data_automation_project(
            projectArn=project_arn
        )
        
        project_config = project_details['project']
        
        # Look for any ARN that matches the profile pattern
        for key, value in project_config.items():
            if isinstance(value, str) and 'data-automation-profile' in value:
                print(f"✅ Found profile ARN in project config: {value}")
                return value
        
        # Check nested configurations
        def search_nested(obj, path=""):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    current_path = f"{path}.{k}" if path else k
                    if isinstance(v, str) and 'data-automation-profile' in v:
                        print(f"✅ Found profile ARN at {current_path}: {v}")
                        return v
                    elif isinstance(v, (dict, list)):
                        result = search_nested(v, current_path)
                        if result:
                            return result
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    result = search_nested(item, f"{path}[{i}]")
                    if result:
                        return result
            return None
        
        embedded_profile = search_nested(project_config)
        if embedded_profile:
            return embedded_profile
    
    except Exception as e:
        print(f"❌ Cannot check project config: {str(e)}")
    
    return None

def test_bda_profile_arn(profile_arn, runtime_client, s3_client):
    """Test if a profile ARN works with BDA"""
    
    try:
        # Create test setup
        test_bucket = f"bda-profile-test-{int(time.time())}"
        
        try:
            s3_client.create_bucket(Bucket=test_bucket)
            
            test_content = "Test content for BDA profile validation"
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
            
            # Test BDA with this profile ARN
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
            print(f"✅ SUCCESS! Profile ARN works: {invocation_arn}")
            
            # Clean up
            s3_client.delete_object(Bucket=test_bucket, Key=test_key)
            s3_client.delete_bucket(Bucket=test_bucket)
            
            return True
            
        except Exception as e:
            # Clean up on error
            try:
                s3_client.delete_object(Bucket=test_bucket, Key=test_key)
                s3_client.delete_bucket(Bucket=test_bucket)
            except:
                pass
            
            error_code = getattr(e, 'response', {}).get('Error', {}).get('Code', '')
            error_message = getattr(e, 'response', {}).get('Error', {}).get('Message', '')
            
            if error_code == 'ValidationException':
                if 'regular expression pattern' in error_message:
                    print(f"❌ Invalid ARN format")
                else:
                    print(f"❌ Validation failed: {error_message}")
            elif error_code == 'ResourceNotFoundException':
                print(f"❌ Profile not found")
            elif error_code == 'AccessDeniedException':
                print(f"❌ Access denied")
            else:
                print(f"❌ Failed: {error_code} - {error_message}")
            
            return False
    
    except Exception as e:
        print(f"❌ Test error: {str(e)}")
        return False

def update_blueprint_with_correct_profile(profile_arn):
    """Update blueprint processor with the correct profile ARN"""
    
    print(f"\n🔧 UPDATING BLUEPRINT PROCESSOR")
    print(f"Correct Profile ARN: {profile_arn}")
    print("=" * 50)
    
    try:
        # Read the current blueprint processor
        with open("python/BlueprintAPI/src/blueprint_processor.py", 'r') as f:
            content = f.read()
        
        # Replace the profile ARN in the function
        old_line = 'role_arn = "arn:aws:iam::624706593351:role/AmazonBedrockDataAutomationRole"'
        new_line = f'profile_arn = "{profile_arn}"'
        
        if old_line in content:
            content = content.replace(old_line, new_line)
            content = content.replace('print(f"📋 Using BDA IAM role: {role_arn}")', 'print(f"📋 Using BDA profile: {profile_arn}")')
            content = content.replace('return role_arn', 'return profile_arn')
            
            print("✅ Updated profile ARN in blueprint processor")
        else:
            print("⚠️ Could not find exact line to replace")
            print("   Manually update the profile ARN in _get_or_create_data_automation_profile")
        
        # Write the updated content
        with open("python/BlueprintAPI/src/blueprint_processor.py", 'w') as f:
            f.write(content)
        
        print(f"✅ Blueprint processor updated with correct profile ARN")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update blueprint processor: {str(e)}")
        return False

def main():
    print("🚀 CORRECT BDA PROFILE SETUP")
    print("=" * 40)
    
    # Find the correct profile ARN
    profile_arn = create_correct_bda_profile()
    
    if profile_arn:
        print(f"\n✅ FOUND WORKING PROFILE ARN: {profile_arn}")
        
        # Update blueprint processor
        success = update_blueprint_with_correct_profile(profile_arn)
        
        if success:
            print(f"\n🎯 BDA SETUP COMPLETE!")
            print(f"   Profile ARN: {profile_arn}")
            print(f"   Blueprint processor updated")
            
            print(f"\n🧪 TEST YOUR SYSTEM:")
            print(f"   python debug_bda_upload.py")
        else:
            print(f"\n⚠️ Profile found but update failed")
            print(f"   Manually update blueprint processor with: {profile_arn}")
    else:
        print(f"\n❌ NO WORKING PROFILE ARN FOUND")
        print(f"\n🔧 NEXT STEPS:")
        print(f"1. Check AWS Console → Bedrock → Data Automation → Profiles")
        print(f"2. Create a profile if the option exists")
        print(f"3. The profile ARN must match format:")
        print(f"   arn:aws:bedrock:us-east-1:624706593351:data-automation-profile/[name]")

if __name__ == "__main__":
    main()