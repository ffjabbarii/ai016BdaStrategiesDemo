#!/usr/bin/env python3
"""
Find the actual valid profile ARN that BDA expects
"""

import boto3
import time
from botocore.exceptions import ClientError

def find_valid_profile_arn():
    """Find the correct profile ARN format that actually works"""
    
    print("🎯 FINDING VALID PROFILE ARN")
    print("=" * 50)
    
    region = 'us-east-1'
    account_id = "624706593351"  # From your project ARN
    project_arn = "arn:aws:bedrock:us-east-1:624706593351:data-automation-project/a07a2d75b205"
    
    bedrock_data_automation_runtime_client = boto3.client('bedrock-data-automation-runtime', region_name=region)
    bedrock_data_automation_client = boto3.client('bedrock-data-automation', region_name=region)
    s3_client = boto3.client('s3', region_name=region)
    
    # Create test setup
    test_bucket = f"bda-profile-test-{int(time.time())}"
    
    try:
        s3_client.create_bucket(Bucket=test_bucket)
        test_content = "Employee Name: John Doe\nSSN: 123-45-6789"
        test_key = "test.txt"
        
        s3_client.put_object(
            Bucket=test_bucket,
            Key=test_key,
            Body=test_content.encode('utf-8'),
            ContentType='text/plain'
        )
        
        input_s3_uri = f"s3://{test_bucket}/{test_key}"
        output_s3_uri = f"s3://{test_bucket}/output/"
        
        print(f"📤 Test setup complete: {input_s3_uri}")
        
        # Try different profile ARN patterns based on AWS documentation
        profile_patterns = [
            # Standard AWS managed profile
            f"arn:aws:bedrock:{region}:aws:data-automation-profile/default",
            
            # Account-specific profiles
            f"arn:aws:bedrock:{region}:{account_id}:data-automation-profile/default",
            f"arn:aws:bedrock:{region}:{account_id}:data-automation-profile/standard",
            
            # Service-linked profiles
            f"arn:aws:bedrock:{region}:{account_id}:data-automation-profile/service-role/AmazonBedrockDataAutomationServiceRole",
            
            # Project-based profiles
            f"arn:aws:bedrock:{region}:{account_id}:data-automation-profile/project-default",
            
            # Alternative service naming
            f"arn:aws:bedrock-data-automation:{region}:{account_id}:profile/default",
            f"arn:aws:bedrock-data-automation:{region}:aws:profile/default",
            
            # Check if there's a profile with the same ID as the project
            f"arn:aws:bedrock:{region}:{account_id}:data-automation-profile/a07a2d75b205",
        ]
        
        print(f"\n🧪 Testing {len(profile_patterns)} profile ARN patterns...")
        
        for i, profile_arn in enumerate(profile_patterns, 1):
            print(f"\n🔍 Pattern {i}: {profile_arn}")
            
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
                print(f"✅ SUCCESS! Working profile ARN: {profile_arn}")
                print(f"✅ BDA job created: {invocation_arn}")
                
                # Clean up and return success
                s3_client.delete_object(Bucket=test_bucket, Key=test_key)
                s3_client.delete_bucket(Bucket=test_bucket)
                
                return {
                    'success': True,
                    'profile_arn': profile_arn,
                    'invocation_arn': invocation_arn,
                    'pattern_number': i
                }
                
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', '')
                error_message = e.response.get('Error', {}).get('Message', '')
                print(f"❌ Failed: {error_code}")
                
                if error_code == 'ValidationException':
                    print(f"   Invalid ARN format")
                elif error_code == 'ResourceNotFoundException':
                    print(f"   Profile not found")
                elif error_code == 'AccessDeniedException':
                    print(f"   Access denied - profile may exist but no permission")
                else:
                    print(f"   {error_message}")
        
        # If no patterns worked, check what profiles might exist
        print(f"\n🔍 Checking for existing profiles...")
        
        # Try to list data automation projects to see if they contain profile info
        try:
            projects_response = bedrock_data_automation_client.list_data_automation_projects()
            projects = projects_response.get('projects', [])
            
            for project in projects:
                if project.get('projectArn') == project_arn:
                    print(f"📋 Found our project in list")
                    
                    # Get detailed project info
                    try:
                        project_details = bedrock_data_automation_client.get_data_automation_project(
                            projectArn=project_arn
                        )
                        
                        project_config = project_details['project']
                        print(f"📋 Project details:")
                        
                        for key, value in project_config.items():
                            if 'profile' in key.lower() or 'Profile' in key or 'arn' in str(value).lower():
                                print(f"   {key}: {value}")
                        
                        # Look for any ARN that might be a profile
                        for key, value in project_config.items():
                            if isinstance(value, str) and 'arn:aws:' in value and 'profile' in value:
                                print(f"\n🎯 Found potential profile ARN in project: {value}")
                                
                                # Test this ARN
                                try:
                                    response = bedrock_data_automation_runtime_client.invoke_data_automation_async(
                                        inputConfiguration={'s3Uri': input_s3_uri},
                                        outputConfiguration={'s3Uri': output_s3_uri},
                                        dataAutomationConfiguration={'dataAutomationProjectArn': project_arn},
                                        dataAutomationProfileArn=value
                                    )
                                    
                                    invocation_arn = response.get('invocationArn')
                                    print(f"✅ SUCCESS! Project profile ARN works: {value}")
                                    
                                    # Clean up and return
                                    s3_client.delete_object(Bucket=test_bucket, Key=test_key)
                                    s3_client.delete_bucket(Bucket=test_bucket)
                                    
                                    return {
                                        'success': True,
                                        'profile_arn': value,
                                        'invocation_arn': invocation_arn,
                                        'source': 'project_config'
                                    }
                                    
                                except Exception as e:
                                    print(f"❌ Project profile ARN failed: {str(e)}")
                        
                    except Exception as e:
                        print(f"❌ Cannot get project details: {str(e)}")
                    
                    break
        
        except Exception as e:
            print(f"❌ Cannot list projects: {str(e)}")
        
        # Clean up
        s3_client.delete_object(Bucket=test_bucket, Key=test_key)
        s3_client.delete_bucket(Bucket=test_bucket)
        
        return {'success': False, 'error': 'No valid profile ARN found'}
        
    except Exception as e:
        print(f"❌ Test setup failed: {str(e)}")
        return {'success': False, 'error': str(e)}

def main():
    result = find_valid_profile_arn()
    
    print(f"\n" + "=" * 50)
    print(f"🎯 RESULT:")
    
    if result.get('success'):
        print(f"✅ FOUND WORKING PROFILE ARN!")
        print(f"   Profile ARN: {result['profile_arn']}")
        print(f"   Invocation ARN: {result['invocation_arn']}")
        print(f"   Source: {result.get('source', 'pattern_test')}")
        
        print(f"\n🔧 UPDATE YOUR CODE:")
        print(f"Replace the profile ARN resolution with:")
        print(f'profile_arn = "{result["profile_arn"]}"')
        
    else:
        print(f"❌ NO VALID PROFILE ARN FOUND")
        print(f"   Error: {result.get('error', 'Unknown')}")
        print(f"\n🔧 NEXT STEPS:")
        print(f"1. Check AWS Console → Bedrock → Data Automation → Profiles")
        print(f"2. You may need to create a data automation profile first")
        print(f"3. Contact AWS support about BDA profile setup")

if __name__ == "__main__":
    main()