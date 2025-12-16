#!/usr/bin/env python3
"""
Create the required IAM role for BDA and update blueprint processor
"""

import boto3
import json
from botocore.exceptions import ClientError

def create_bda_iam_role():
    """Create IAM role for BDA with proper permissions"""
    
    print("🎯 CREATING BDA IAM ROLE")
    print("=" * 50)
    
    iam_client = boto3.client('iam')
    
    role_name = "AmazonBedrockDataAutomationRole"
    account_id = "624706593351"
    role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"
    
    # Trust policy for Bedrock service
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "bedrock.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    # Permissions policy for BDA
    permissions_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock:*",
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:DeleteObject",
                    "s3:ListBucket"
                ],
                "Resource": "*"
            }
        ]
    }
    
    try:
        # Check if role already exists
        try:
            existing_role = iam_client.get_role(RoleName=role_name)
            print(f"✅ Role already exists: {role_name}")
            print(f"   ARN: {existing_role['Role']['Arn']}")
            return existing_role['Role']['Arn']
            
        except ClientError as e:
            if e.response['Error']['Code'] != 'NoSuchEntity':
                raise
        
        # Create the role
        print(f"🔧 Creating IAM role: {role_name}")
        
        create_response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="IAM role for Amazon Bedrock Data Automation",
            MaxSessionDuration=3600
        )
        
        created_arn = create_response['Role']['Arn']
        print(f"✅ Created role: {created_arn}")
        
        # Attach AWS managed policy for Bedrock
        print(f"🔧 Attaching AmazonBedrockFullAccess policy...")
        try:
            iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn="arn:aws:iam::aws:policy/AmazonBedrockFullAccess"
            )
            print(f"✅ Attached AmazonBedrockFullAccess")
        except ClientError as e:
            if 'NoSuchEntity' in str(e):
                print(f"⚠️ AmazonBedrockFullAccess policy not found, creating custom policy...")
            else:
                raise
        
        # Create and attach custom policy for S3 and BDA
        policy_name = "BedrockDataAutomationPolicy"
        
        try:
            policy_response = iam_client.create_policy(
                PolicyName=policy_name,
                PolicyDocument=json.dumps(permissions_policy),
                Description="Custom policy for Bedrock Data Automation"
            )
            
            policy_arn = policy_response['Policy']['Arn']
            print(f"✅ Created custom policy: {policy_arn}")
            
            # Attach the custom policy
            iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn=policy_arn
            )
            print(f"✅ Attached custom policy to role")
            
        except ClientError as e:
            if 'EntityAlreadyExists' in str(e):
                # Policy already exists, just attach it
                policy_arn = f"arn:aws:iam::{account_id}:policy/{policy_name}"
                iam_client.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy_arn
                )
                print(f"✅ Attached existing custom policy")
            else:
                print(f"⚠️ Policy creation failed: {str(e)}")
        
        print(f"\n✅ IAM role setup complete!")
        print(f"   Role ARN: {created_arn}")
        
        return created_arn
        
    except Exception as e:
        print(f"❌ Failed to create IAM role: {str(e)}")
        return None

def update_blueprint_processor_with_role(role_arn):
    """Update blueprint processor with the IAM role ARN"""
    
    print(f"\n🔧 UPDATING BLUEPRINT PROCESSOR")
    print(f"Role ARN: {role_arn}")
    print("=" * 50)
    
    try:
        # Read the current blueprint processor
        with open("python/BlueprintAPI/src/blueprint_processor.py", 'r') as f:
            content = f.read()
        
        # Find and replace the profile ARN resolution function
        # Look for the function that tries multiple profile patterns
        old_pattern = "async def _get_or_create_data_automation_profile(self, project_arn: str) -> str:"
        
        if old_pattern in content:
            # Find the start and end of the function
            start_idx = content.find(old_pattern)
            if start_idx != -1:
                # Find the next function or end of class
                lines = content[start_idx:].split('\n')
                function_lines = []
                indent_level = None
                
                for i, line in enumerate(lines):
                    if i == 0:  # First line (function definition)
                        function_lines.append(line)
                        continue
                    
                    # Determine indent level from first non-empty line
                    if indent_level is None and line.strip():
                        indent_level = len(line) - len(line.lstrip())
                    
                    # If we hit a line with same or less indentation (and it's not empty), we've reached the end
                    if line.strip() and indent_level is not None:
                        current_indent = len(line) - len(line.lstrip())
                        if current_indent <= indent_level and (line.strip().startswith('def ') or line.strip().startswith('async def ') or line.strip().startswith('class ')):
                            break
                    
                    function_lines.append(line)
                
                old_function = '\n'.join(function_lines)
                
                # Create new simple function
                new_function = f"""    async def _get_or_create_data_automation_profile(self, project_arn: str) -> str:
        \"\"\"Get the IAM role ARN for BDA processing\"\"\"
        # Use the created IAM role ARN for BDA
        role_arn = "{role_arn}"
        print(f"📋 Using BDA IAM role: {{role_arn}}")
        return role_arn"""
                
                # Replace the function
                content = content.replace(old_function, new_function)
                print("✅ Updated _get_or_create_data_automation_profile function")
            else:
                print("❌ Could not find function start")
                return False
        else:
            print("❌ Could not find function to replace")
            return False
        
        # Write the updated content
        with open("python/BlueprintAPI/src/blueprint_processor.py", 'w') as f:
            f.write(content)
        
        print(f"✅ Blueprint processor updated with IAM role ARN")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update blueprint processor: {str(e)}")
        return False

def test_bda_with_new_role(role_arn):
    """Test BDA with the new IAM role"""
    
    print(f"\n🧪 TESTING BDA WITH NEW ROLE")
    print("=" * 40)
    
    try:
        import time
        
        bedrock_data_automation_runtime_client = boto3.client('bedrock-data-automation-runtime', region_name='us-east-1')
        s3_client = boto3.client('s3', region_name='us-east-1')
        
        # Create test setup
        test_bucket = f"bda-role-test-{int(time.time())}"
        
        try:
            s3_client.create_bucket(Bucket=test_bucket)
            
            test_content = "Employee Name: John Doe\nSSN: 123-45-6789\nWages: $50000"
            test_key = "test-w2.txt"
            
            s3_client.put_object(
                Bucket=test_bucket,
                Key=test_key,
                Body=test_content.encode('utf-8'),
                ContentType='text/plain'
            )
            
            input_s3_uri = f"s3://{test_bucket}/{test_key}"
            output_s3_uri = f"s3://{test_bucket}/output/"
            project_arn = "arn:aws:bedrock:us-east-1:624706593351:data-automation-project/a07a2d75b205"
            
            print(f"📤 Test input: {input_s3_uri}")
            print(f"📥 Test output: {output_s3_uri}")
            print(f"🎯 Project: {project_arn}")
            print(f"👤 Role: {role_arn}")
            
            # Test BDA with the new role
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
                dataAutomationProfileArn=role_arn
            )
            
            invocation_arn = response.get('invocationArn')
            print(f"\n✅ SUCCESS! BDA job created with new role!")
            print(f"   Invocation ARN: {invocation_arn}")
            
            # Clean up
            s3_client.delete_object(Bucket=test_bucket, Key=test_key)
            s3_client.delete_bucket(Bucket=test_bucket)
            
            return True
            
        except Exception as e:
            # Clean up on error
            try:
                s3_client.delete_object(Bucket=test_bucket, Key=test_key)
                s3_client.delete_bucket(Bucket=test_bucket)
            except:
                pass
            
            error_code = getattr(e, 'response', {}).get('Error', {}).get('Code', '')
            error_message = getattr(e, 'response', {}).get('Error', {}).get('Message', str(e))
            print(f"\n❌ BDA test failed: {error_code}")
            print(f"   Message: {error_message}")
            
            if error_code == 'AccessDeniedException':
                print(f"   💡 The role may need time to propagate (wait 1-2 minutes)")
            elif error_code == 'ValidationException':
                print(f"   💡 Role ARN format might be incorrect")
            
            return False
    
    except Exception as e:
        print(f"❌ Test setup failed: {str(e)}")
        return False

def main():
    print("🚀 BDA IAM ROLE SETUP")
    print("=" * 30)
    
    # Step 1: Create IAM role
    role_arn = create_bda_iam_role()
    
    if not role_arn:
        print("❌ Failed to create IAM role")
        return
    
    # Step 2: Update blueprint processor
    success = update_blueprint_processor_with_role(role_arn)
    
    if not success:
        print("❌ Failed to update blueprint processor")
        return
    
    # Step 3: Test BDA
    print(f"\n⏳ Waiting 10 seconds for IAM role to propagate...")
    import time
    time.sleep(10)
    
    test_success = test_bda_with_new_role(role_arn)
    
    print(f"\n" + "=" * 50)
    print(f"🎯 FINAL RESULT:")
    
    if test_success:
        print(f"✅ BDA SETUP COMPLETE!")
        print(f"   IAM Role: {role_arn}")
        print(f"   Blueprint processor updated")
        print(f"   BDA job creation working")
        
        print(f"\n🧪 TEST YOUR SYSTEM:")
        print(f"   python debug_bda_upload.py")
        
    else:
        print(f"⚠️ IAM ROLE CREATED BUT BDA TEST FAILED")
        print(f"   Role ARN: {role_arn}")
        print(f"   Blueprint processor updated")
        print(f"   Wait 1-2 minutes for IAM propagation, then test")
        
        print(f"\n🧪 TEST AFTER WAITING:")
        print(f"   python debug_bda_upload.py")

if __name__ == "__main__":
    main()