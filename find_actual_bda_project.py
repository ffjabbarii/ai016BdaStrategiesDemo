#!/usr/bin/env python3
"""
Find the actual BDA project and its associated resources
"""

import subprocess
import json
import re

def find_bda_resources():
    """Find all BDA-related resources"""
    
    print("🔍 FINDING ACTUAL BDA PROJECT AND RESOURCES")
    print("=" * 60)
    
    # 1. List all S3 buckets to find BDA ones
    print("\n📁 SEARCHING FOR BDA S3 BUCKETS:")
    try:
        cmd = ['aws', 's3api', 'list-buckets', '--region', 'us-east-1']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            buckets = json.loads(result.stdout)
            bda_buckets = []
            
            for bucket in buckets['Buckets']:
                bucket_name = bucket['Name']
                if 'bedrock' in bucket_name.lower() or 'data-automation' in bucket_name.lower() or 'bda' in bucket_name.lower():
                    bda_buckets.append(bucket_name)
                    print(f"  📦 {bucket_name} (Created: {bucket['CreationDate']})")
            
            if not bda_buckets:
                print("  ❌ No BDA-related buckets found")
            else:
                # Check contents of each BDA bucket
                for bucket_name in bda_buckets:
                    print(f"\n  📂 Contents of {bucket_name}:")
                    try:
                        cmd = ['aws', 's3', 'ls', f's3://{bucket_name}/', '--recursive']
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                        
                        if result.returncode == 0 and result.stdout.strip():
                            lines = result.stdout.strip().split('\n')
                            print(f"    Found {len(lines)} objects")
                            for line in lines[:10]:  # Show first 10
                                if line.strip():
                                    parts = line.split()
                                    if len(parts) >= 4:
                                        key = ' '.join(parts[3:])
                                        print(f"      📄 {key}")
                            if len(lines) > 10:
                                print(f"      ... and {len(lines) - 10} more files")
                        else:
                            print("    Empty or inaccessible")
                    except Exception as e:
                        print(f"    Error: {str(e)}")
        else:
            print(f"❌ Error listing buckets: {result.stderr}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # 2. Try to list BDA projects with different approaches
    print(f"\n📋 SEARCHING FOR BDA PROJECTS:")
    
    # Try the standard command
    try:
        cmd = ['aws', 'bedrock-agent', 'list-data-automation-projects', '--region', 'us-east-1']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            projects = json.loads(result.stdout)
            if projects.get('projects'):
                print("✅ Found BDA projects:")
                for project in projects['projects']:
                    print(f"  📊 Project: {project.get('projectName', 'Unknown')}")
                    print(f"     ID: {project.get('projectId', 'Unknown')}")
                    print(f"     Status: {project.get('status', 'Unknown')}")
                    print(f"     Created: {project.get('createdAt', 'Unknown')}")
                    print()
            else:
                print("❌ No BDA projects found")
        else:
            print(f"❌ Error listing projects: {result.stderr}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # 3. Check CloudFormation stacks for BDA resources
    print(f"\n☁️ CHECKING CLOUDFORMATION FOR BDA STACKS:")
    try:
        cmd = ['aws', 'cloudformation', 'list-stacks', '--region', 'us-east-1', '--stack-status-filter', 'CREATE_COMPLETE', 'UPDATE_COMPLETE']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            stacks = json.loads(result.stdout)
            bda_stacks = []
            
            for stack in stacks['StackSummaries']:
                stack_name = stack['StackName']
                if any(keyword in stack_name.lower() for keyword in ['bedrock', 'data-automation', 'bda']):
                    bda_stacks.append(stack)
                    print(f"  📚 {stack_name} (Status: {stack['StackStatus']})")
            
            if not bda_stacks:
                print("  ❌ No BDA-related CloudFormation stacks found")
                
        else:
            print(f"❌ Error listing stacks: {result.stderr}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # 4. Check IAM roles for BDA
    print(f"\n👤 CHECKING IAM ROLES FOR BDA:")
    try:
        cmd = ['aws', 'iam', 'list-roles', '--region', 'us-east-1']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            roles = json.loads(result.stdout)
            bda_roles = []
            
            for role in roles['Roles']:
                role_name = role['RoleName']
                if any(keyword in role_name.lower() for keyword in ['bedrock', 'data-automation', 'bda']):
                    bda_roles.append(role)
                    print(f"  👤 {role_name}")
            
            if not bda_roles:
                print("  ❌ No BDA-related IAM roles found")
                
        else:
            print(f"❌ Error listing roles: {result.stderr}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # 5. Provide guidance
    print(f"\n💡 WHAT THIS MEANS:")
    print("If no BDA resources are found, it could mean:")
    print("  • The project was created in a different region")
    print("  • The project creation failed silently")
    print("  • The project is using a different naming convention")
    print("  • Your AWS CLI is not configured for the right account")
    print("  • BDA is not fully enabled in your account/region")
    
    print(f"\n🔄 NEXT STEPS:")
    print("  1. Check AWS Console in different regions (us-west-2, eu-west-1)")
    print("  2. Verify your AWS account ID and permissions")
    print("  3. Try creating a new BDA project from scratch")
    print("  4. Check AWS CloudTrail for BDA API calls")
    print("  5. Contact AWS support if BDA should be available")

if __name__ == "__main__":
    find_bda_resources()