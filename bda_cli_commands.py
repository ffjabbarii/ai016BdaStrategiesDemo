#!/usr/bin/env python3
"""
BDA Project CLI Commands Generator
Creates AWS CLI commands to explore your BDA project components
"""

def generate_bda_cli_commands():
    """Generate AWS CLI commands for BDA project exploration"""
    
    # Your project details
    project_arn = "arn:aws:bedrock:us-east-1:624706593351:data-automation-project/a07a2d75b205"
    project_name = "test-w2-fixed-1765841521"
    project_id = "a07a2d75b205"
    region = "us-east-1"
    account_id = "624706593351"
    
    print("🚀 BDA PROJECT CLI COMMANDS")
    print("=" * 80)
    print(f"Project: {project_name}")
    print(f"ARN: {project_arn}")
    print("=" * 80)
    
    commands = {
        "📋 PROJECT INFORMATION": [
            {
                "desc": "List all your BDA projects",
                "cmd": f"aws bedrock-data-automation list-data-automation-projects --region {region}"
            },
            {
                "desc": "Get detailed information about your specific project",
                "cmd": f"aws bedrock-data-automation get-data-automation-project --project-arn {project_arn} --region {region}"
            },
            {
                "desc": "Get project tags and metadata",
                "cmd": f"aws bedrock-data-automation list-tags-for-resource --resource-arn {project_arn} --region {region}"
            }
        ],
        
        "🔧 BLUEPRINTS & CONFIGURATION": [
            {
                "desc": "List available blueprints in your account",
                "cmd": f"aws bedrock-data-automation list-blueprints --region {region}"
            },
            {
                "desc": "Get blueprint details (if using custom blueprints)",
                "cmd": f"aws bedrock-data-automation get-blueprint --blueprint-arn <BLUEPRINT_ARN> --region {region}"
            }
        ],
        
        "🚀 INVOCATIONS & JOBS": [
            {
                "desc": "List all invocations/jobs for your project",
                "cmd": f"aws bedrock-data-automation-runtime list-data-automation-invocations --project-arn {project_arn} --region {region}"
            },
            {
                "desc": "List all invocations in your account",
                "cmd": f"aws bedrock-data-automation-runtime list-invocations --region {region}"
            },
            {
                "desc": "Get status of a specific invocation",
                "cmd": f"aws bedrock-data-automation-runtime get-data-automation-status --invocation-arn <INVOCATION_ARN> --region {region}"
            },
            {
                "desc": "Get results of a completed invocation",
                "cmd": f"aws bedrock-data-automation-runtime get-data-automation-result --invocation-arn <INVOCATION_ARN> --region {region}"
            }
        ],
        
        "📁 STORAGE & DOCUMENTS": [
            {
                "desc": "List S3 buckets related to your project",
                "cmd": f"aws s3api list-buckets --query \"Buckets[?contains(Name, '{project_id}')]\" --region {region}"
            },
            {
                "desc": "List all documents in your project bucket",
                "cmd": f"aws s3 ls s3://bda-project-storage-{project_id}/ --recursive"
            },
            {
                "desc": "List documents folder specifically",
                "cmd": f"aws s3 ls s3://bda-project-storage-{project_id}/documents/"
            },
            {
                "desc": "List BDA output results",
                "cmd": f"aws s3 ls s3://bda-project-storage-{project_id}/bda-output/"
            },
            {
                "desc": "Get bucket information",
                "cmd": f"aws s3api get-bucket-location --bucket bda-project-storage-{project_id}"
            },
            {
                "desc": "Get bucket versioning status",
                "cmd": f"aws s3api get-bucket-versioning --bucket bda-project-storage-{project_id}"
            }
        ],
        
        "📊 MONITORING & LOGS": [
            {
                "desc": "List BDA CloudWatch log groups",
                "cmd": f"aws logs describe-log-groups --log-group-name-prefix /aws/bedrock/data-automation --region {region}"
            },
            {
                "desc": "Get recent BDA log events",
                "cmd": f"aws logs filter-log-events --log-group-name /aws/bedrock/data-automation --start-time $(date -d '1 day ago' +%s)000 --region {region}"
            },
            {
                "desc": "Get CloudWatch metrics for BDA",
                "cmd": f"aws cloudwatch get-metric-statistics --namespace AWS/Bedrock --metric-name Invocations --start-time $(date -u -d '1 day ago' +%Y-%m-%dT%H:%M:%S) --end-time $(date -u +%Y-%m-%dT%H:%M:%S) --period 3600 --statistics Sum --region {region}"
            }
        ],
        
        "🔍 SPECIFIC DOCUMENT ANALYSIS": [
            {
                "desc": "Download a specific document from your project",
                "cmd": f"aws s3 cp s3://bda-project-storage-{project_id}/documents/1765904567_w-2.pdf ./downloaded-w2.pdf"
            },
            {
                "desc": "Get document metadata",
                "cmd": f"aws s3api head-object --bucket bda-project-storage-{project_id} --key documents/1765904567_w-2.pdf"
            },
            {
                "desc": "List all processing results",
                "cmd": f"aws s3 ls s3://bda-project-storage-{project_id}/results/ --recursive"
            }
        ]
    }
    
    # Print all commands organized by category
    for category, cmd_list in commands.items():
        print(f"\n{category}")
        print("=" * 60)
        
        for i, cmd_info in enumerate(cmd_list, 1):
            print(f"\n{i}. {cmd_info['desc']}")
            print(f"   {cmd_info['cmd']}")
    
    # Print the most important commands for quick reference
    print(f"\n🎯 QUICK REFERENCE - MOST IMPORTANT COMMANDS")
    print("=" * 60)
    
    quick_commands = [
        f"aws bedrock-data-automation get-data-automation-project --project-arn {project_arn} --region {region}",
        f"aws s3 ls s3://bda-project-storage-{project_id}/ --recursive",
        f"aws bedrock-data-automation-runtime list-invocations --region {region}",
        f"aws bedrock-data-automation-runtime get-data-automation-status --invocation-arn <YOUR_INVOCATION_ARN> --region {region}"
    ]
    
    for i, cmd in enumerate(quick_commands, 1):
        print(f"\n{i}. {cmd}")
    
    print(f"\n💡 TIPS:")
    print(f"• Replace <INVOCATION_ARN> with actual ARN from list-invocations command")
    print(f"• Replace <BLUEPRINT_ARN> with actual ARN from list-blueprints command")
    print(f"• Add --output table for better formatting: --output table")
    print(f"• Add --query for specific fields: --query 'project.projectName'")
    
    print(f"\n🔗 RELATED AWS CONSOLE LINKS:")
    print(f"• BDA Projects: https://console.aws.amazon.com/bedrock/home?region={region}#/data-automation/projects")
    print(f"• S3 Bucket: https://s3.console.aws.amazon.com/s3/buckets/bda-project-storage-{project_id}?region={region}")
    print(f"• CloudWatch Logs: https://console.aws.amazon.com/cloudwatch/home?region={region}#logsV2:log-groups")

def create_invocation_explorer():
    """Create commands to explore a specific invocation"""
    
    print(f"\n🔍 INVOCATION EXPLORER")
    print("=" * 60)
    print("Use these commands to explore a specific BDA job/invocation:")
    
    invocation_commands = [
        "# Step 1: Get your latest invocation ARN",
        "aws bedrock-data-automation-runtime list-invocations --region us-east-1 --query 'invocations[0].invocationArn' --output text",
        "",
        "# Step 2: Get invocation status (replace <ARN> with result from step 1)",
        "aws bedrock-data-automation-runtime get-data-automation-status --invocation-arn <ARN> --region us-east-1",
        "",
        "# Step 3: Get invocation results (if completed)",
        "aws bedrock-data-automation-runtime get-data-automation-result --invocation-arn <ARN> --region us-east-1",
        "",
        "# Step 4: Check output files in S3",
        "aws s3 ls s3://bda-project-storage-a07a2d75b205/bda-output/ --recursive"
    ]
    
    for cmd in invocation_commands:
        print(cmd)

def main():
    generate_bda_cli_commands()
    create_invocation_explorer()
    
    print(f"\n" + "=" * 80)
    print(f"🚀 READY TO EXPLORE!")
    print(f"Copy and paste the commands above to explore your BDA project")
    print(f"Start with the 'QUICK REFERENCE' commands for the most important information")

if __name__ == "__main__":
    main()