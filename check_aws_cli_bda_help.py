#!/usr/bin/env python3
"""
Check AWS CLI documentation for BDA profiles
"""

import subprocess
import json

def check_aws_cli_bda_help():
    """Check AWS CLI help for BDA profile information"""
    
    print("🔍 CHECKING AWS CLI BDA DOCUMENTATION")
    print("=" * 60)
    
    # Check bedrock-data-automation CLI help
    commands_to_check = [
        ["aws", "bedrock-data-automation", "help"],
        ["aws", "bedrock-data-automation", "list-data-automation-projects", "help"],
        ["aws", "bedrock-data-automation", "get-data-automation-project", "help"],
        ["aws", "bedrock-data-automation-runtime", "help"],
        ["aws", "bedrock-data-automation-runtime", "invoke-data-automation-async", "help"],
    ]
    
    for cmd in commands_to_check:
        print(f"\n📋 Running: {' '.join(cmd)}")
        print("-" * 40)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                output = result.stdout
                
                # Look for profile-related information
                if 'profile' in output.lower() or 'dataautomationprofilearn' in output.lower():
                    print("✅ Found profile-related information:")
                    
                    # Extract relevant lines
                    lines = output.split('\n')
                    for i, line in enumerate(lines):
                        if 'profile' in line.lower() or 'dataautomationprofilearn' in line.lower():
                            # Print context around the match
                            start = max(0, i-2)
                            end = min(len(lines), i+3)
                            for j in range(start, end):
                                marker = ">>> " if j == i else "    "
                                print(f"{marker}{lines[j]}")
                            print()
                else:
                    print("⚠️ No profile information found in this command")
                    
            else:
                print(f"❌ Command failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("❌ Command timed out")
        except Exception as e:
            print(f"❌ Error running command: {str(e)}")
    
    # Check if we can list any existing profiles
    print(f"\n🔍 CHECKING FOR EXISTING PROFILES")
    print("=" * 40)
    
    profile_commands = [
        ["aws", "bedrock-data-automation", "list-data-automation-profiles"],
        ["aws", "iam", "list-roles", "--query", "Roles[?contains(RoleName, 'Bedrock') || contains(RoleName, 'DataAutomation')].{RoleName:RoleName,Arn:Arn}"],
    ]
    
    for cmd in profile_commands:
        print(f"\n📋 Trying: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if output:
                    print("✅ Found results:")
                    try:
                        # Try to parse as JSON
                        data = json.loads(output)
                        print(json.dumps(data, indent=2))
                    except:
                        # Print as text if not JSON
                        print(output)
                else:
                    print("⚠️ Command succeeded but returned no results")
            else:
                error = result.stderr.strip()
                if "Unknown operation" in error:
                    print("❌ Operation not available (might not exist)")
                elif "AccessDenied" in error:
                    print("❌ Access denied - check permissions")
                else:
                    print(f"❌ Error: {error}")
                    
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    # Check the specific invoke-data-automation-async parameters
    print(f"\n🔍 CHECKING INVOKE PARAMETERS")
    print("=" * 40)
    
    try:
        cmd = ["aws", "bedrock-data-automation-runtime", "invoke-data-automation-async", "help"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            output = result.stdout
            
            # Look for dataAutomationProfileArn documentation
            lines = output.split('\n')
            in_profile_section = False
            
            for i, line in enumerate(lines):
                if 'dataautomationprofilearn' in line.lower():
                    print("✅ Found dataAutomationProfileArn documentation:")
                    
                    # Print context around this parameter
                    start = max(0, i-1)
                    end = min(len(lines), i+10)  # More context for parameter docs
                    
                    for j in range(start, end):
                        if j == i:
                            print(f">>> {lines[j]}")
                        else:
                            print(f"    {lines[j]}")
                        
                        # Stop if we hit the next parameter
                        if j > i and lines[j].strip() and not lines[j].startswith(' '):
                            break
                    break
            else:
                print("❌ dataAutomationProfileArn documentation not found")
                
    except Exception as e:
        print(f"❌ Error checking invoke parameters: {str(e)}")

def check_boto3_docs():
    """Check boto3 documentation for BDA"""
    
    print(f"\n🔍 CHECKING BOTO3 CLIENT DOCUMENTATION")
    print("=" * 50)
    
    try:
        import boto3
        
        # Check BDA runtime client
        client = boto3.client('bedrock-data-automation-runtime', region_name='us-east-1')
        
        # Get the operation model for invoke_data_automation_async
        operation_model = client._service_model.operation_model('InvokeDataAutomationAsync')
        
        print("✅ Found invoke_data_automation_async operation model:")
        
        # Check input shape
        input_shape = operation_model.input_shape
        
        for member_name, member_shape in input_shape.members.items():
            print(f"\n📋 Parameter: {member_name}")
            print(f"   Required: {member_name in input_shape.required_members}")
            print(f"   Type: {member_shape.type_name}")
            
            if hasattr(member_shape, 'documentation'):
                print(f"   Documentation: {member_shape.documentation}")
            
            if member_name == 'dataAutomationProfileArn':
                print(f"   🎯 This is the profile ARN parameter!")
                
                # Check if there are any constraints or patterns
                if hasattr(member_shape, 'metadata'):
                    print(f"   Metadata: {member_shape.metadata}")
                
                # Check for pattern validation
                for constraint_name, constraint_value in getattr(member_shape, 'metadata', {}).items():
                    print(f"   {constraint_name}: {constraint_value}")
    
    except Exception as e:
        print(f"❌ Error checking boto3 docs: {str(e)}")

def main():
    check_aws_cli_bda_help()
    check_boto3_docs()
    
    print(f"\n" + "=" * 60)
    print(f"🎯 SUMMARY:")
    print(f"Look for:")
    print(f"1. Profile ARN format in the CLI help output")
    print(f"2. Any existing IAM roles for Bedrock/DataAutomation")
    print(f"3. Documentation about what dataAutomationProfileArn expects")
    print(f"4. Whether profiles need to be created first")

if __name__ == "__main__":
    main()