#!/usr/bin/env python3
"""
Try to create a BDA profile or find the correct way to get one
"""

import boto3
from botocore.exceptions import ClientError

def create_bda_profile():
    """Try to create a BDA profile or find existing ones"""
    
    print("🎯 CREATING/FINDING BDA PROFILE")
    print("=" * 50)
    
    region = 'us-east-1'
    account_id = "624706593351"
    
    bedrock_data_automation_client = boto3.client('bedrock-data-automation', region_name=region)
    
    # Check if there are any profile-related operations
    operations = [op for op in dir(bedrock_data_automation_client) if 'profile' in op.lower()]
    
    print(f"📋 Profile-related operations: {operations}")
    
    if not operations:
        print("❌ No profile operations found in BDA client")
        print("   Profiles might be managed through AWS Console only")
        
        print(f"\n🔧 MANUAL STEPS REQUIRED:")
        print(f"1. Go to AWS Console → Amazon Bedrock → Data Automation")
        print(f"2. Look for 'Profiles' section")
        print(f"3. Create a default profile if option exists")
        print(f"4. Note the profile ARN format")
        
        return None
    
    # Try each profile operation
    for op_name in operations:
        print(f"\n🧪 Testing {op_name}...")
        
        try:
            operation = getattr(bedrock_data_automation_client, op_name)
            
            if 'list' in op_name.lower():
                # Try to list profiles
                try:
                    result = operation()
                    print(f"✅ {op_name} succeeded:")
                    print(f"   Result: {result}")
                    
                    # Look for profile ARNs in the result
                    if isinstance(result, dict):
                        for key, value in result.items():
                            if isinstance(value, list):
                                for item in value:
                                    if isinstance(item, dict) and 'arn' in str(item).lower():
                                        print(f"   🎯 Found ARN: {item}")
                    
                except Exception as e:
                    print(f"❌ {op_name} failed: {str(e)}")
            
            elif 'create' in op_name.lower():
                # Try to create a profile (but don't actually do it without knowing parameters)
                print(f"   📋 {op_name} is available for profile creation")
                print(f"   (Not attempting creation without knowing required parameters)")
            
            elif 'get' in op_name.lower():
                print(f"   📋 {op_name} is available for getting profile details")
        
        except AttributeError:
            print(f"❌ {op_name} not actually available")
    
    # Alternative: Check if the project itself contains profile information
    print(f"\n🔍 Checking if project contains profile ARN...")
    
    project_arn = "arn:aws:bedrock:us-east-1:624706593351:data-automation-project/a07a2d75b205"
    
    try:
        project_details = bedrock_data_automation_client.get_data_automation_project(
            projectArn=project_arn
        )
        
        project_config = project_details['project']
        
        # Look for any field that might contain a profile ARN
        for key, value in project_config.items():
            if 'profile' in key.lower():
                print(f"✅ Found profile field: {key} = {value}")
                return value
            elif isinstance(value, str) and 'arn:aws:' in value and value != project_arn:
                print(f"🔍 Found other ARN: {key} = {value}")
                # This might be a profile ARN with different naming
                if 'profile' in value or 'automation' in value:
                    print(f"   ^ This might be the profile ARN!")
                    return value
        
        # Check nested configurations
        for key, value in project_config.items():
            if isinstance(value, dict):
                print(f"📋 Checking nested config: {key}")
                for nested_key, nested_value in value.items():
                    if 'profile' in nested_key.lower() or ('arn:aws:' in str(nested_value) and nested_value != project_arn):
                        print(f"   🎯 Found in {key}.{nested_key}: {nested_value}")
                        return nested_value
    
    except Exception as e:
        print(f"❌ Cannot check project: {str(e)}")
    
    # Last resort: Check AWS documentation patterns
    print(f"\n📚 Checking AWS documentation patterns...")
    
    # Based on other AWS services, profiles might use different ARN formats
    doc_patterns = [
        # IAM-style service role
        f"arn:aws:iam::{account_id}:role/service-role/AmazonBedrockDataAutomationServiceRole",
        
        # Bedrock service profiles
        f"arn:aws:bedrock:{region}:{account_id}:agent-alias/TSTALIASID",  # Example from Bedrock agents
        
        # Check if it's under a different service
        f"arn:aws:iam::{account_id}:role/AmazonBedrockDataAutomationRole",
    ]
    
    print(f"📋 Documentation suggests these patterns might work:")
    for pattern in doc_patterns:
        print(f"   {pattern}")
    
    return None

def main():
    result = create_bda_profile()
    
    print(f"\n" + "=" * 50)
    print(f"🎯 RESULT:")
    
    if result:
        print(f"✅ FOUND POTENTIAL PROFILE ARN: {result}")
        print(f"\n🧪 Test this ARN in your BDA job creation")
    else:
        print(f"❌ NO PROFILE ARN FOUND")
        print(f"\n🔧 REQUIRED ACTIONS:")
        print(f"1. Go to AWS Console → Amazon Bedrock → Data Automation")
        print(f"2. Check if there's a 'Profiles' or 'Configuration' section")
        print(f"3. Create a profile if the option exists")
        print(f"4. Check AWS CLI: aws bedrock-data-automation list-data-automation-profiles")
        print(f"5. Contact AWS support if profiles are not available in your region")

if __name__ == "__main__":
    main()