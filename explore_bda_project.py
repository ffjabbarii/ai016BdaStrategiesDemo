#!/usr/bin/env python3
"""
Explore BDA project components using AWS CLI commands
Shows all pieces of the BDA project: documents, reports, invocations, etc.
"""

import subprocess
import json
import sys
from datetime import datetime

def run_aws_command(command, description):
    """Run AWS CLI command and return formatted results"""
    print(f"\n🔍 {description}")
    print("=" * 60)
    print(f"Command: {' '.join(command)}")
    print("-" * 60)
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            output = result.stdout.strip()
            if output:
                try:
                    # Try to parse as JSON for pretty printing
                    data = json.loads(output)
                    print(json.dumps(data, indent=2, default=str))
                    return data
                except json.JSONDecodeError:
                    # Not JSON, print as text
                    print(output)
                    return output
            else:
                print("✅ Command succeeded but returned no output")
                return None
        else:
            error = result.stderr.strip()
            if "Unknown operation" in error or "Invalid choice" in error:
                print("❌ Command not available (BDA CLI not supported)")
            elif "AccessDenied" in error:
                print("❌ Access denied - check permissions")
            else:
                print(f"❌ Error: {error}")
            return None
            
    except subprocess.TimeoutExpired:
        print("❌ Command timed out")
        return None
    except Exception as e:
        print(f"❌ Error running command: {str(e)}")
        return None

def explore_bda_project():
    """Explore BDA project using AWS CLI commands"""
    
    print("🚀 BDA PROJECT EXPLORATION")
    print("=" * 80)
    print("Exploring your BDA project components using AWS CLI commands")
    print("=" * 80)
    
    # Your project details
    project_arn = "arn:aws:bedrock:us-east-1:624706593351:data-automation-project/a07a2d75b205"
    project_name = "test-w2-fixed-1765841521"
    region = "us-east-1"
    
    print(f"🎯 Target Project: {project_name}")
    print(f"📍 Project ARN: {project_arn}")
    print(f"🌍 Region: {region}")
    
    # 1. List all BDA projects
    projects_data = run_aws_command([
        "aws", "bedrock-data-automation", "list-data-automation-projects",
        "--region", region
    ], "List All BDA Projects")
    
    # 2. Get detailed project information
    project_data = run_aws_command([
        "aws", "bedrock-data-automation", "get-data-automation-project",
        "--project-arn", project_arn,
        "--region", region
    ], f"Get Detailed Project Information: {project_name}")
    
    # 3. List blueprints (if any)
    blueprints_data = run_aws_command([
        "aws", "bedrock-data-automation", "list-blueprints",
        "--region", region
    ], "List Available Blueprints")
    
    # 4. Try to get project invocations/jobs
    invocations_data = run_aws_command([
        "aws", "bedrock-data-automation-runtime", "list-data-automation-invocations",
        "--project-arn", project_arn,
        "--region", region
    ], "List Project Invocations/Jobs")
    
    # Alternative invocation listing (different API pattern)
    if not invocations_data:
        invocations_data = run_aws_command([
            "aws", "bedrock-data-automation-runtime", "list-invocations",
            "--region", region
        ], "List All Invocations (Alternative)")
    
    # 5. Get invocation status for recent jobs
    if invocations_data and isinstance(invocations_data, dict):
        invocations = invocations_data.get('invocations', [])
        for invocation in invocations[:3]:  # Check first 3 invocations
            invocation_arn = invocation.get('invocationArn')
            if invocation_arn:
                run_aws_command([
                    "aws", "bedrock-data-automation-runtime", "get-data-automation-status",
                    "--invocation-arn", invocation_arn,
                    "--region", region
                ], f"Get Invocation Status: {invocation_arn.split('/')[-1]}")
    
    # 6. List project tags
    run_aws_command([
        "aws", "bedrock-data-automation", "list-tags-for-resource",
        "--resource-arn", project_arn,
        "--region", region
    ], "List Project Tags")
    
    # 7. Check CloudWatch logs for BDA
    run_aws_command([
        "aws", "logs", "describe-log-groups",
        "--log-group-name-prefix", "/aws/bedrock/data-automation",
        "--region", region
    ], "Check BDA CloudWatch Log Groups")
    
    # 8. List S3 buckets related to the project
    project_id = project_arn.split('/')[-1]
    run_aws_command([
        "aws", "s3api", "list-buckets",
        "--query", f"Buckets[?contains(Name, '{project_id}')]",
        "--region", region
    ], f"Find S3 Buckets Related to Project ID: {project_id}")
    
    # 9. Check specific project bucket contents
    project_bucket = f"bda-project-storage-{project_id}"
    run_aws_command([
        "aws", "s3", "ls", f"s3://{project_bucket}/",
        "--recursive"
    ], f"List Contents of Project Bucket: {project_bucket}")
    
    # 10. Get bucket policy and configuration
    run_aws_command([
        "aws", "s3api", "get-bucket-location",
        "--bucket", project_bucket
    ], f"Get Bucket Location: {project_bucket}")
    
    run_aws_command([
        "aws", "s3api", "get-bucket-versioning",
        "--bucket", project_bucket
    ], f"Get Bucket Versioning: {project_bucket}")
    
    # 11. List recent CloudTrail events for BDA
    run_aws_command([
        "aws", "logs", "filter-log-events",
        "--log-group-name", "/aws/cloudtrail",
        "--filter-pattern", "bedrock-data-automation",
        "--start-time", str(int((datetime.now().timestamp() - 86400) * 1000)),  # Last 24 hours
        "--region", region
    ], "Recent CloudTrail Events for BDA (Last 24 hours)")

def create_bda_exploration_commands():
    """Create a list of useful AWS CLI commands for BDA exploration"""
    
    project_arn = "arn:aws:bedrock:us-east-1:624706593351:data-automation-project/a07a2d75b205"
    project_id = "a07a2d75b205"
    region = "us-east-1"
    
    commands = [
        # Project Management
        f"aws bedrock-data-automation list-data-automation-projects --region {region}",
        f"aws bedrock-data-automation get-data-automation-project --project-arn {project_arn} --region {region}",
        f"aws bedrock-data-automation list-tags-for-resource --resource-arn {project_arn} --region {region}",
        
        # Blueprints
        f"aws bedrock-data-automation list-blueprints --region {region}",
        
        # Invocations/Jobs
        f"aws bedrock-data-automation-runtime list-data-automation-invocations --project-arn {project_arn} --region {region}",
        f"aws bedrock-data-automation-runtime list-invocations --region {region}",
        
        # S3 Storage
        f"aws s3 ls s3://bda-project-storage-{project_id}/ --recursive",
        f"aws s3api list-buckets --query \"Buckets[?contains(Name, '{project_id}')]\"",
        f"aws s3api get-bucket-location --bucket bda-project-storage-{project_id}",
        
        # Monitoring
        f"aws logs describe-log-groups --log-group-name-prefix /aws/bedrock/data-automation --region {region}",
        f"aws cloudwatch get-metric-statistics --namespace AWS/Bedrock --metric-name Invocations --start-time $(date -u -d '1 day ago' +%Y-%m-%dT%H:%M:%S) --end-time $(date -u +%Y-%m-%dT%H:%M:%S) --period 3600 --statistics Sum --region {region}",
    ]
    
    print(f"\n📋 USEFUL BDA EXPLORATION COMMANDS")
    print("=" * 60)
    print("Copy and paste these commands to explore your BDA project:")
    print()
    
    for i, cmd in enumerate(commands, 1):
        print(f"{i:2d}. {cmd}")
    
    print(f"\n💡 TIP: Replace the project ARN and region as needed for other projects")

def main():
    print("🔍 BDA PROJECT COMPONENT EXPLORER")
    print("=" * 50)
    
    # Check if AWS CLI is available
    try:
        result = subprocess.run(["aws", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ AWS CLI Available: {result.stdout.strip()}")
        else:
            print("❌ AWS CLI not available")
            return
    except:
        print("❌ AWS CLI not found")
        return
    
    # Run the exploration
    explore_bda_project()
    
    # Provide useful commands
    create_bda_exploration_commands()
    
    print(f"\n" + "=" * 80)
    print(f"🎯 EXPLORATION COMPLETE")
    print(f"Use the commands above to further explore your BDA project components")
    print(f"Check the AWS Console → Bedrock → Data Automation for visual interface")

if __name__ == "__main__":
    main()