#!/usr/bin/env python3
"""
AWS CLI commands to investigate BDA project and find processing jobs
"""

import subprocess
import json
import sys

def run_aws_command(command, description):
    """Run AWS CLI command and return result"""
    print(f"\n🔍 {description}")
    print(f"Command: {' '.join(command)}")
    print("-" * 60)
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            if result.stdout.strip():
                try:
                    # Try to parse as JSON for pretty printing
                    json_data = json.loads(result.stdout)
                    print(json.dumps(json_data, indent=2))
                except json.JSONDecodeError:
                    # Not JSON, print as is
                    print(result.stdout)
            else:
                print("✅ Command succeeded (no output)")
        else:
            print(f"❌ Error (exit code {result.returncode}):")
            print(result.stderr)
            
        return result.returncode == 0, result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        print("⏰ Command timed out")
        return False, "", "Timeout"
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False, "", str(e)

def main():
    """Check BDA project using AWS CLI"""
    
    print("🔍 AWS CLI Investigation of BDA Project")
    print("=" * 60)
    
    # Your project details
    project_arn = "arn:aws:bedrock:us-east-1:624706593351:data-automation-project/a07a2d75b205"
    project_name = "test-w2-fixed-1765841521"
    region = "us-east-1"
    
    # 1. Check if AWS CLI is configured
    run_aws_command(
        ["aws", "sts", "get-caller-identity"],
        "Checking AWS CLI configuration and credentials"
    )
    
    # 2. List all BDA projects
    run_aws_command(
        ["aws", "bedrock-data-automation", "list-data-automation-projects", "--region", region],
        "Listing all BDA projects in your account"
    )
    
    # 3. Get specific project details
    run_aws_command(
        ["aws", "bedrock-data-automation", "get-data-automation-project", 
         "--project-arn", project_arn, "--region", region],
        f"Getting details for project: {project_name}"
    )
    
    # 4. Try to list invocations (processing jobs)
    run_aws_command(
        ["aws", "bedrock-data-automation-runtime", "list-data-automation-invocations",
         "--project-arn", project_arn, "--region", region],
        "Listing processing jobs/invocations for the project"
    )
    
    # 5. Check S3 bucket for documents
    s3_bucket = "bda-project-storage-a07a2d75b205"
    run_aws_command(
        ["aws", "s3", "ls", f"s3://{s3_bucket}/", "--recursive"],
        f"Checking S3 bucket contents: {s3_bucket}"
    )
    
    # 6. Check if bucket exists
    run_aws_command(
        ["aws", "s3", "ls", f"s3://{s3_bucket}/"],
        f"Checking if S3 bucket exists: {s3_bucket}"
    )
    
    # 7. List all S3 buckets to see what's available
    run_aws_command(
        ["aws", "s3", "ls"],
        "Listing all S3 buckets to find BDA-related buckets"
    )
    
    # 8. Try alternative BDA commands
    run_aws_command(
        ["aws", "bedrock-data-automation", "help"],
        "Checking available BDA commands"
    )
    
    # 9. Try to get invocation details if we have any
    print("\n🔍 Trying to find recent invocations...")
    success, stdout, stderr = run_aws_command(
        ["aws", "bedrock-data-automation-runtime", "list-data-automation-invocations",
         "--project-arn", project_arn, "--region", region, "--max-items", "10"],
        "Looking for recent invocations with details"
    )
    
    if success and stdout:
        try:
            invocations = json.loads(stdout)
            if 'invocations' in invocations and invocations['invocations']:
                print(f"\n✅ Found {len(invocations['invocations'])} invocations!")
                for i, inv in enumerate(invocations['invocations']):
                    inv_arn = inv.get('invocationArn', 'Unknown')
                    status = inv.get('status', 'Unknown')
                    print(f"\nInvocation {i+1}:")
                    print(f"  ARN: {inv_arn}")
                    print(f"  Status: {status}")
                    
                    # Get details for each invocation
                    if inv_arn != 'Unknown':
                        run_aws_command(
                            ["aws", "bedrock-data-automation-runtime", "get-data-automation-invocation",
                             "--invocation-arn", inv_arn, "--region", region],
                            f"Getting details for invocation {i+1}"
                        )
            else:
                print("❌ No invocations found in the response")
        except json.JSONDecodeError:
            print("❌ Could not parse invocations response as JSON")
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY:")
    print("- Check the output above for any processing jobs or invocations")
    print("- Look for S3 bucket contents to see if your W-2 was stored")
    print("- If no invocations are found, the BDA job might not have been created properly")
    print("- If S3 bucket doesn't exist, there might be an issue with the upload process")

if __name__ == "__main__":
    main()