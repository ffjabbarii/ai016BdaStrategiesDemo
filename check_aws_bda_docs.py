#!/usr/bin/env python3
"""
Check AWS BDA documentation and API to find correct profile ARN format
"""

import boto3
from botocore.exceptions import ClientError

def check_aws_bda_docs():
    """Check AWS BDA API documentation and available operations"""
    
    print("🎯 CHECKING AWS BDA API DOCUMENTATION")
    print("=" * 60)
    
    region = 'us-east-1'
    
    # Check what operations are available on BDA clients
    print("📋 Available BDA Operations:")
    
    # BDA Client operations
    bedrock_data_automation_client = boto3.client('bedrock-data-automation', region_name=region)
    bda_operations = [op for op in dir(bedrock_data_automation_client) if not op.startswith('_') and not op in ['meta', 'exceptions']]
    
    print(f"\n🔍 bedrock-data-automation client operations:")
    profile_ops = []
    for op in sorted(bda_operations):
        if 'profile' in op.lower():
            profile_ops.append(op)
            print(f"   ✅ {op}")
        elif op in ['create_data_automation_project', 'get_data_automation_project', 'list_data_automation_projects']:
            print(f"   📋 {op}")
    
    if not profile_ops:
        print(f"   ❌ No profile-related operations found")
    
    # BDA Runtime Client operations  
    bedrock_data_automation_runtime_client = boto3.client('bedrock-data-automation-runtime', region_name=region)
    runtime_operations = [op for op in dir(bedrock_data_automation_runtime_client) if not op.startswith('_') and not op in ['meta', 'exceptions']]
    
    print(f"\n🔍 bedrock-data-automation-runtime client operations:")
    for op in sorted(runtime_operations):
        print(f"   📋 {op}")
    
    # Check if there are profile creation operations
    print(f"\n🧪 Testing profile operations...")
    
    for op_name in profile_ops:
        try:
            operation = getattr(bedrock_data_automation_client, op_name)
            print(f"✅ {op_name} is available")
            
            # Try to get help/documentation for this operation
            try:
                # This might give us parameter information
                help_info = operation.__doc__ if hasattr(operation, '__doc__') else "No documentation"
                if help_info and help_info != "No documentation":
                    print(f"   📖 {help_info[:100]}...")
            except:
                pass
                
        except AttributeError:
            print(f"❌ {op_name} not available")
    
    # Try to call list operations to see what exists
    print(f"\n🔍 Checking existing resources...")
    
    try:
        # List projects to see their structure
        projects_response = bedrock_data_automation_client.list_data_automation_projects()
        projects = projects_response.get('projects', [])
        
        print(f"📋 Found {len(projects)} projects")
        
        # Look at our specific project
        project_arn = "arn:aws:bedrock:us-east-1:624706593351:data-automation-project/a07a2d75b205"
        
        for project in projects:
            if project.get('projectArn') == project_arn:
                print(f"\n📋 Our project structure:")
                for key, value in project.items():
                    print(f"   {key}: {value}")
                
                # Get detailed project info
                try:
                    project_details = bedrock_data_automation_client.get_data_automation_project(
                        projectArn=project_arn
                    )
                    
                    print(f"\n📋 Detailed project info:")
                    project_config = project_details['project']
                    
                    for key, value in project_config.items():
                        print(f"   {key}: {value}")
                        
                        # Look for any clues about profile ARN format
                        if isinstance(value, dict):
                            print(f"      (dict with keys: {list(value.keys())})")
                        elif isinstance(value, str) and 'arn:' in value:
                            print(f"      ^ This is an ARN - might give us format clues")
                
                except Exception as e:
                    print(f"❌ Cannot get project details: {str(e)}")
                
                break
    
    except Exception as e:
        print(f"❌ Cannot list projects: {str(e)}")
    
    # Check the invoke_data_automation_async parameters
    print(f"\n🔍 Checking invoke_data_automation_async parameters...")
    
    try:
        # Try to get the operation model to see required parameters
        runtime_client = bedrock_data_automation_runtime_client
        
        # This is a hack to see the operation model
        try:
            # Trigger a parameter validation error to see what parameters are expected
            runtime_client.invoke_data_automation_async()
        except Exception as e:
            error_str = str(e)
            print(f"📋 Parameter validation error (this shows us required params):")
            print(f"   {error_str}")
            
            # Look for clues about profile ARN format in the error
            if 'dataAutomationProfileArn' in error_str:
                print(f"   ✅ dataAutomationProfileArn is confirmed as required parameter")
            
    except Exception as e:
        print(f"❌ Cannot check parameters: {str(e)}")
    
    print(f"\n" + "=" * 60)
    print(f"🎯 FINDINGS:")
    print(f"1. dataAutomationProfileArn is required (confirmed)")
    print(f"2. All our ARN format guesses are wrong (ValidationException)")
    print(f"3. Need to find the correct ARN format from AWS documentation")
    
    print(f"\n🔧 NEXT STEPS:")
    print(f"1. Check AWS Console → Bedrock → Data Automation → Profiles")
    print(f"2. Look for profile creation in the console")
    print(f"3. Check AWS CLI: aws bedrock-data-automation help")
    print(f"4. Check if profiles need to be created before use")

if __name__ == "__main__":
    check_aws_bda_docs()