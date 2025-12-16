#!/usr/bin/env python3
"""
Simple BDA diagnostic - check the most important things
"""

import subprocess
import json

def run_cmd(cmd, desc):
    print(f"\n🔍 {desc}")
    print(f"$ {cmd}")
    try:
        result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            print("✅ SUCCESS:")
            print(result.stdout)
        else:
            print("❌ ERROR:")
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def main():
    print("🔍 Simple BDA Diagnostic")
    print("=" * 40)
    
    # Check 1: AWS credentials
    run_cmd("aws sts get-caller-identity", "Checking AWS credentials")
    
    # Check 2: List BDA projects
    run_cmd("aws bedrock-data-automation list-data-automation-projects --region us-east-1", 
            "Listing BDA projects")
    
    # Check 3: Check S3 bucket
    run_cmd("aws s3 ls s3://bda-project-storage-a07a2d75b205/", 
            "Checking S3 bucket")
    
    # Check 4: List all S3 buckets with 'bda' in name
    run_cmd("aws s3 ls", "Listing all S3 buckets")
    
    print("\n" + "=" * 40)
    print("🎯 Key Questions:")
    print("1. Do you see your BDA project in the list?")
    print("2. Does the S3 bucket exist?")
    print("3. Are there any files in the S3 bucket?")

if __name__ == "__main__":
    main()