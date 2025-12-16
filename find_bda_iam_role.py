#!/usr/bin/env python3
"""
Find the correct IAM role ARN for BDA dataAutomationProfileArn parameter
"""

import boto3
from botocore.exceptions import ClientError

def find_bda_iam_role():
    """Find IAM roles that can be used for BDA"""
    
    print("🎯 FINDING BDA IAM ROLE ARN")
    print("=" * 50)
    
    iam_client = boto3.client('iam')
    account_id = "624706593351"  # From your project ARN
    
    try:
        # List all IAM roles
        print("📋 Searching for BDA-related IAM roles...")
        
        paginator = iam_client.get_paginator('list_roles')
        bda_roles = []
        
        for page in paginator.paginate():
            for role in page['Roles']:
                role_name = role['RoleName']
                role_arn = role['Arn']
                
                # Look for roles that might be related to Bedrock or Data Automation
                if any(keyword in role_name.lower() for keyword in [
                    'bedrock', 'data-automation', 'dataautomation', 'bda'
                ]):
                    bda_roles.append({
                        'name': role_name,
                        'arn': role_arn,
                        'created': role['CreateDate']
                    })
                    print(f"✅ Found BDA-related role: {role_name}")
                    print(f"   ARN: {role_arn}")
        
        if not bda_roles:
            print("❌ No BDA-related roles found")
            print("🔍 Looking for service-linked roles...")
            
            # Look for service-linked roles
            for page in paginator.paginate():
                for role in page['Roles']:
                    role_name = role['RoleName']
                    role_arn = role['Arn']
                    
                    # Check if it's a service-linked role for AWS services
                    if 'service-role' in role_name.lower() or role['Path'].startswith('/aws-service-role/'):
                        print(f"📋 Service role: {role_name}")
                        
                        # Check if it has Bedrock permissions
                        try:
                            # Get role policies
                            attached_policies = iam_client.list_attached_role_policies(RoleName=role_name)
                            inline_policies = iam_client.list_role_policies(RoleName=role_name)
                            
                            has_bedrock_permissions = False
                            
                            # Check attached policies
                            for policy in attached_policies['AttachedPolicies']:
                                if 'bedrock' in policy['PolicyName'].lower():
                                    has_bedrock_permissions = True
                                    break
                            
                            # Check inline policies
                            for policy_name in inline_policies['PolicyNames']:
                                if 'bedrock' in policy_name.lower():
                                    has_bedrock_permissions = True
                                    break
                            
                            if has_bedrock_permissions:
                                bda_roles.append({
                                    'name': role_name,
                                    'arn': role_arn,
                                    'created': role['CreateDate'],
                                    'type': 'service-linked'
                                })
                                print(f"✅ Found service role with Bedrock permissions: {role_name}")
                                print(f"   ARN: {role_arn}")
                        
                        except Exception as e:
                            # Skip roles we can't access
                            pass
        
        # If still no roles found, suggest creating one
        if not bda_roles:
            print("\n❌ No suitable IAM roles found")
            print("🔧 You need to create an IAM role for BDA")
            
            suggested_role_name = "AmazonBedrockDataAutomationRole"
            suggested_arn = f"arn:aws:iam::{account_id}:role/{suggested_role_name}"
            
            print(f"\n📋 SUGGESTED IAM ROLE CREATION:")
            print(f"Role Name: {suggested_role_name}")
            print(f"Role ARN: {suggested_arn}")
            print(f"Trust Policy: Allow bedrock.amazonaws.com")
            print(f"Permissions: AmazonBedrockFullAccess, S3 access")
            
            return {
                'success': False,
                'suggested_arn': suggested_arn,
                'suggested_name': suggested_role_name
            }
        
        # Test the found roles
        print(f"\n🧪 Testing found roles with BDA...")
        
        # Use the most likely role (first BDA-specific one)
        test_role = bda_roles[0]
        test_arn = test_role['arn']
        
        print(f"🧪 Testing role: {test_role['name']}")
        print(f"   ARN: {test_arn}")
        
        # Test this role with BDA
        success = test_bda_with_role(test_arn)
        
        if success:
            return {
                'success': True,
                'role_arn': test_arn,
                'role_name': test_role['name']
            }
        else:
            # Try other roles
            for role in bda_roles[1:]:
                print(f"\n🧪 Testing role: {role['name']}")
                success = test_bda_with_role(role['arn'])
                if success:
                    return {
                        'success': True,
                        'role_arn': role['arn'],
                        'role_name': role['name']
                    }
            
            return {
                'success': False,
                'available_roles': bda_roles,
                'message': 'Found roles but none worked with BDA'
            }
    
    except Exception as e:
        print(f"❌ Error searching for roles: {str(e)}")
        return {'success': False, 'error': str(e)}

def test_bda_with_role(role_arn):
    """Test if a role ARN works with BDA"""
    
    try:
        import time
        
        bedrock_data_automation_runtime_client = boto3.client('bedrock-data-automation-runtime', region_name='us-east-1')
        s3_client = boto3.client('s3', region_name='us-east-1')
        
        # Create test setup
        test_bucket = f"bda-role-test-{int(time.time())}"
        
        try:
            s3_client.create_bucket(Bucket=test_bucket)
            
            test_content = "Test content for BDA"
            test_key = "test.txt"
            
            s3_client.put_object(
                Bucket=test_bucket,
                Key=test_key,
                Body=test_content.encode('utf-8'),
                ContentType='text/plain'
            )
            
            input_s3_uri = f"s3://{test_bucket}/{test_key}"
            output_s3_uri = f"s3://{test_bucket}/output/"
            project_arn = "arn:aws:bedrock:us-east-1:624706593351:data-automation-project/a07a2d75b205"
            
            # Test BDA with this role ARN
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
                dataAutomationProfileArn=role_arn  # This is the IAM role ARN
            )
            
            invocation_arn = response.get('invocationArn')
            print(f"✅ SUCCESS! Role works with BDA: {invocation_arn}")
            
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
            print(f"❌ Role test failed: {error_code}")
            return False
    
    except Exception as e:
        print(f"❌ Role test error: {str(e)}")
        return False

def main():
    result = find_bda_iam_role()
    
    print(f"\n" + "=" * 50)
    print(f"🎯 RESULT:")
    
    if result.get('success'):
        role_arn = result['role_arn']
        role_name = result['role_name']
        
        print(f"✅ FOUND WORKING IAM ROLE!")
        print(f"   Role Name: {role_name}")
        print(f"   Role ARN: {role_arn}")
        
        print(f"\n🔧 UPDATE YOUR CODE:")
        print(f"Replace the dataAutomationProfileArn with:")
        print(f'dataAutomationProfileArn="{role_arn}"')
        
        # Create update script
        with open("update_with_profile_arn.py", 'r') as f:
            content = f.read()
        
        # Update the script with the working ARN
        updated_content = content.replace(
            'update_with_profile_arn("arn:aws:bedrock:us-east-1:624706593351:data-automation-profile/your-profile-name")',
            f'update_with_profile_arn("{role_arn}")'
        )
        
        with open("update_with_profile_arn.py", 'w') as f:
            f.write(updated_content)
        
        print(f"\n🚀 NEXT STEP:")
        print(f"Run: python update_with_profile_arn.py")
        
    else:
        print(f"❌ NO WORKING IAM ROLE FOUND")
        
        if 'suggested_arn' in result:
            print(f"\n🔧 CREATE IAM ROLE:")
            print(f"1. Go to AWS Console → IAM → Roles")
            print(f"2. Create role: {result['suggested_name']}")
            print(f"3. Trust policy: bedrock.amazonaws.com")
            print(f"4. Permissions: AmazonBedrockFullAccess + S3 access")
            print(f"5. Use ARN: {result['suggested_arn']}")
        
        if 'available_roles' in result:
            print(f"\n📋 Available roles to try:")
            for role in result['available_roles']:
                print(f"   {role['name']}: {role['arn']}")

if __name__ == "__main__":
    main()