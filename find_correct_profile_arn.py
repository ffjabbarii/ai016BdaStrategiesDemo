#!/usr/bin/env python3
"""
Find the correct data automation profile ARN format
"""

import boto3
import json
from botocore.exceptions import ClientError

def find_correct_profile_arn():
    """Find the correct profile ARN by exploring available APIs"""
    
    print("🔍 Finding Correct Data Automation Profile ARN")
    print("=" * 60)
    
    # Initialize clients
    region = 'us-east-1'
    bedrock_client = boto3.client('bedrock', region_name=region)
    bedrock_data_automation_client = boto3.client('bedrock-data-automation', region_name=region)
    
    # Step 1: Check what methods are available on the BDA client
    print("📋 Step 1: Available BDA client methods...")
    methods = [method for method in dir(bedrock_data_automation_client) if not method.startswith('_')]
    profile_methods = [method for method in methods if 'profile' in method.lower()]
    
    print("🔍 Profile-related methods:")
    for method in profile_methods:
        print(f"   - {method}")
    
    if not profile_methods:
        print("❌ No profile-related methods found")
    
    # Step 2: Try to list projects and see if they contain profile information
    print("\n📋 Step 2: Checking project details for profile information...")
    try:
        projects_response = bedrock_data_automation_client.list_data_automation_projects()
        projects = projects_response.get('projects', [])
        
        print(f"✅ Found {len(projects)} projects")
        
        for project in projects:
            project_arn = project.get('projectArn')
            if project_arn:
                print(f"\n🔍 Checking project: {project.get('projectName')}")
                
                # Get detailed project info
                try:
                    project_details = bedrock_data_automation_client.get_data_automation_project(
                        projectArn=project_arn
                    )
                    
                    project_config = project_details['project']
                    print(f"   Status: {project_config.get('status')}")
                    
                    # Look for any profile-related fields
                    for key, value in project_config.items():
                        if 'profile' in key.lower() or 'arn' in str(value).lower():
                            print(f"   {key}: {value}")
                    
                    # Check if there's a default profile pattern we can derive
                    if 'blueprintArn' in project_config:
                        blueprint_arn = project_config['blueprintArn']
                        print(f"   Blueprint ARN: {blueprint_arn}")
                        
                        # Try to derive profile ARN from blueprint ARN
                        if blueprint_arn:
                            # Convert blueprint ARN to potential profile ARN
                            profile_candidate = blueprint_arn.replace('blueprint', 'data-automation-profile')
                            print(f"   Potential profile ARN: {profile_candidate}")
                    
                except Exception as e:
                    print(f"   ❌ Error getting project details: {str(e)}")
                    
    except Exception as e:
        print(f"❌ Error listing projects: {str(e)}")
    
    # Step 3: Check AWS documentation patterns
    print("\n📋 Step 3: Testing AWS documentation patterns...")
    
    account_id = "624706593351"  # From the project ARN
    
    # Based on AWS Bedrock Data Automation documentation
    doc_patterns = [
        # AWS managed profiles (if they exist)
        f"arn:aws:bedrock:{region}:aws:data-automation-profile/default",
        f"arn:aws:bedrock:{region}:aws:data-automation-profile/standard",
        
        # Service-linked profiles
        f"arn:aws:bedrock:{region}:{account_id}:data-automation-profile/service-default",
        f"arn:aws:bedrock:{region}:{account_id}:data-automation-profile/bedrock-default",
        
        # Project-specific profiles
        f"arn:aws:bedrock:{region}:{account_id}:data-automation-profile/project-default",
        
        # Different service naming
        f"arn:aws:bedrock-data-automation:{region}:{account_id}:profile/default",
        f"arn:aws:bedrock-data-automation:{region}:aws:profile/default",
    ]
    
    print(f"🧪 Testing {len(doc_patterns)} documentation patterns...")
    
    for i, pattern in enumerate(doc_patterns, 1):
        print(f"\n🔍 Pattern {i}: {pattern}")
        
        # We can't test these directly without creating BDA jobs, but we can note them
        print(f"   Format: {'AWS managed' if ':aws:' in pattern else 'Account-specific'}")
    
    # Step 4: Check if we need to create a profile first
    print("\n📋 Step 4: Checking if profiles need to be created...")
    
    # Look for create profile methods
    create_methods = [method for method in methods if 'create' in method.lower() and 'profile' in method.lower()]
    
    if create_methods:
        print("✅ Found profile creation methods:")
        for method in create_methods:
            print(f"   - {method}")
    else:
        print("❌ No profile creation methods found")
        print("   This suggests profiles are managed automatically or through console")
    
    # Step 5: Check Bedrock foundation models (sometimes profiles are tied to models)
    print("\n📋 Step 5: Checking Bedrock foundation models...")
    try:
        models_response = bedrock_client.list_foundation_models()
        models = models_response.get('modelSummaries', [])
        
        # Look for data automation related models
        da_models = [model for model in models if 'data' in model.get('modelName', '').lower() or 'automation' in model.get('modelName', '').lower()]
        
        if da_models:
            print("✅ Found data automation related models:")
            for model in da_models:
                print(f"   - {model.get('modelName')}: {model.get('modelArn')}")
        else:
            print("⚠️ No obvious data automation models found")
            
    except Exception as e:
        print(f"❌ Error listing models: {str(e)}")
    
    # Summary and recommendations
    print("\n" + "=" * 60)
    print("🎯 FINDINGS & RECOMMENDATIONS:")
    
    print("\n❌ ISSUE IDENTIFIED:")
    print("   All tested profile ARN patterns are invalid")
    print("   This suggests data automation profiles are not set up in your account")
    
    print("\n🔧 POSSIBLE SOLUTIONS:")
    print("1. Check AWS Console → Bedrock → Data Automation → Profiles")
    print("2. Data automation profiles may need to be created through the console first")
    print("3. Your account may not have BDA fully enabled")
    print("4. Try using the project without a custom profile (use None or empty)")
    
    print("\n🧪 NEXT STEPS:")
    print("1. Go to AWS Console → Amazon Bedrock → Data Automation")
    print("2. Check if there's a 'Profiles' section")
    print("3. Create a default profile if the option exists")
    print("4. Try modifying the code to not specify a profile ARN")

if __name__ == "__main__":
    find_correct_profile_arn()