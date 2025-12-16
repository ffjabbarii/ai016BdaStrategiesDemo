#!/usr/bin/env python3
"""
Check existing BDA projects for profile information
"""

import boto3
import json

def check_existing_projects():
    """Check existing BDA projects for profile ARN clues"""
    
    print("🔍 CHECKING EXISTING BDA PROJECTS")
    print("=" * 50)
    
    try:
        bda_client = boto3.client('bedrock-data-automation', region_name='us-east-1')
        
        # List all projects
        response = bda_client.list_data_automation_projects()
        projects = response.get('projects', [])
        
        print(f"✅ Found {len(projects)} BDA projects")
        
        for i, project in enumerate(projects, 1):
            project_arn = project.get('projectArn')
            project_name = project.get('projectName')
            
            print(f"\n📋 Project {i}: {project_name}")
            print(f"   ARN: {project_arn}")
            
            # Get detailed project information
            try:
                details = bda_client.get_data_automation_project(projectArn=project_arn)
                project_details = details['project']
                
                print(f"   Status: {project_details.get('status')}")
                print(f"   Created: {project_details.get('creationTime')}")
                
                # Look for any profile-related information
                profile_clues = []
                
                def search_for_profiles(obj, path=""):
                    """Recursively search for profile ARNs"""
                    if isinstance(obj, dict):
                        for key, value in obj.items():
                            current_path = f"{path}.{key}" if path else key
                            
                            # Check if this looks like a profile ARN
                            if isinstance(value, str):
                                if 'profile' in key.lower():
                                    profile_clues.append(f"{current_path}: {value}")
                                elif 'arn:aws:' in value and 'profile' in value:
                                    profile_clues.append(f"{current_path}: {value}")
                                elif 'arn:aws:iam' in value and 'role' in value:
                                    profile_clues.append(f"{current_path}: {value} (IAM Role)")
                            
                            # Recurse into nested objects
                            elif isinstance(value, (dict, list)):
                                search_for_profiles(value, current_path)
                    
                    elif isinstance(obj, list):
                        for idx, item in enumerate(obj):
                            search_for_profiles(item, f"{path}[{idx}]")
                
                # Search the entire project configuration
                search_for_profiles(project_details)
                
                if profile_clues:
                    print(f"   🎯 Profile clues found:")
                    for clue in profile_clues:
                        print(f"      {clue}")
                else:
                    print(f"   ❌ No profile information found")
                
                # Show the full configuration for our target project
                if project_name == "test-w2-fixed-1765841521":
                    print(f"\n📋 FULL CONFIGURATION FOR TARGET PROJECT:")
                    print(json.dumps(project_details, indent=2, default=str))
                
            except Exception as e:
                print(f"   ❌ Error getting project details: {str(e)}")
        
        return projects
        
    except Exception as e:
        print(f"❌ Error listing projects: {str(e)}")
        return []

def test_common_profile_patterns():
    """Test common profile ARN patterns based on existing projects"""
    
    print(f"\n🧪 TESTING COMMON PROFILE PATTERNS")
    print("=" * 50)
    
    region = 'us-east-1'
    account_id = '624706593351'
    
    # Based on the fact that projects exist, try these patterns
    patterns = [
        # AWS managed (most likely)
        f"arn:aws:bedrock:{region}:aws:data-automation-profile/default",
        
        # Account-specific
        f"arn:aws:bedrock:{region}:{account_id}:data-automation-profile/default",
        
        # Service-linked role (since we found the IAM role)
        f"arn:aws:iam::{account_id}:role/AmazonBedrockDataAutomationRole",
        
        # Alternative service naming
        f"arn:aws:bedrock-data-automation:{region}:aws:profile/default",
        f"arn:aws:bedrock-data-automation:{region}:{account_id}:profile/default",
    ]
    
    runtime_client = boto3.client('bedrock-data-automation-runtime', region_name=region)
    
    # Create minimal test setup
    import time
    test_bucket = f"bda-pattern-test-{int(time.time())}"
    s3_client = boto3.client('s3', region_name=region)
    
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
        
        print(f"📤 Test setup: {input_s3_uri}")
        
        for i, pattern in enumerate(patterns, 1):
            print(f"\n🧪 Testing pattern {i}: {pattern}")
            
            try:
                response = runtime_client.invoke_data_automation_async(
                    inputConfiguration={'s3Uri': input_s3_uri},
                    outputConfiguration={'s3Uri': output_s3_uri},
                    dataAutomationProfileArn=pattern
                )
                
                invocation_arn = response.get('invocationArn')
                print(f"✅ SUCCESS! Working profile ARN: {pattern}")
                print(f"   Invocation ARN: {invocation_arn}")
                
                # Clean up and return success
                s3_client.delete_object(Bucket=test_bucket, Key=test_key)
                s3_client.delete_bucket(Bucket=test_bucket)
                
                return pattern
                
            except Exception as e:
                error_type = type(e).__name__
                error_msg = str(e)
                
                if 'ValidationException' in error_type and 'invalid' in error_msg.lower():
                    print(f"❌ Invalid ARN format")
                elif 'ResourceNotFoundException' in error_type:
                    print(f"❌ Profile not found")
                elif 'AccessDeniedException' in error_type:
                    print(f"❌ Access denied")
                else:
                    print(f"❌ {error_type}: {error_msg[:100]}")
        
        # Clean up
        s3_client.delete_object(Bucket=test_bucket, Key=test_key)
        s3_client.delete_bucket(Bucket=test_bucket)
        
        return None
        
    except Exception as e:
        print(f"❌ Test setup failed: {str(e)}")
        return None

def main():
    print("🚀 BDA PROJECT ANALYSIS")
    print("=" * 30)
    
    # Check existing projects for clues
    projects = check_existing_projects()
    
    # Test profile patterns
    working_profile = test_common_profile_patterns()
    
    print(f"\n" + "=" * 50)
    print(f"🎯 RESULT:")
    
    if working_profile:
        print(f"✅ FOUND WORKING PROFILE ARN!")
        print(f"   {working_profile}")
        print(f"\n🔧 UPDATE YOUR CODE:")
        print(f"Use this exact ARN in your blueprint processor")
    else:
        print(f"❌ NO WORKING PROFILE ARN FOUND")
        print(f"\n🔧 NEXT STEPS:")
        print(f"1. Check if BDA profiles need to be enabled in your account")
        print(f"2. Contact AWS support about BDA profile setup")
        print(f"3. Check AWS Console → Bedrock → Data Automation for profile options")

if __name__ == "__main__":
    main()