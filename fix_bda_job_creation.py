#!/usr/bin/env python3
"""
Fix BDA job creation - focus ONLY on making invoke_data_automation_async work
"""

import boto3
import time
from botocore.exceptions import ClientError

def fix_bda_job_creation():
    """Fix the actual BDA job creation - no fallbacks, no distractions"""
    
    print("🎯 FIXING BDA JOB CREATION")
    print("=" * 50)
    
    # Use the exact project from your system
    project_arn = "arn:aws:bedrock:us-east-1:624706593351:data-automation-project/a07a2d75b205"
    region = 'us-east-1'
    
    # Initialize the correct BDA runtime client
    bedrock_data_automation_runtime_client = boto3.client('bedrock-data-automation-runtime', region_name=region)
    s3_client = boto3.client('s3', region_name=region)
    
    # Create a simple test setup
    test_bucket = f"bda-job-test-{int(time.time())}"
    
    try:
        print(f"📦 Creating test bucket: {test_bucket}")
        s3_client.create_bucket(Bucket=test_bucket)
        
        # Upload a simple text file (not PDF to avoid format issues)
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
        
        print(f"📤 Input: {input_s3_uri}")
        print(f"📥 Output: {output_s3_uri}")
        
        # TEST 1: BDA job WITHOUT profile ARN
        print(f"\n🧪 TEST 1: BDA job without profile ARN")
        try:
            response = bedrock_data_automation_runtime_client.invoke_data_automation_async(
                inputConfiguration={
                    's3Uri': input_s3_uri
                },
                outputConfiguration={
                    's3Uri': output_s3_uri
                },
                dataAutomationConfiguration={
                    'dataAutomationProjectArn': project_arn
                }
                # NO dataAutomationProfileArn
            )
            
            invocation_arn = response.get('invocationArn')
            print(f"✅ SUCCESS! BDA job created: {invocation_arn}")
            
            # Clean up and return the working configuration
            s3_client.delete_object(Bucket=test_bucket, Key=test_key)
            s3_client.delete_bucket(Bucket=test_bucket)
            
            return {
                'success': True,
                'method': 'no_profile_arn',
                'invocation_arn': invocation_arn,
                'config': {
                    'inputConfiguration': {'s3Uri': 'INPUT_S3_URI'},
                    'outputConfiguration': {'s3Uri': 'OUTPUT_S3_URI'},
                    'dataAutomationConfiguration': {'dataAutomationProjectArn': project_arn}
                }
            }
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            error_message = e.response.get('Error', {}).get('Message', '')
            print(f"❌ Failed: {error_code} - {error_message}")
        
        # TEST 2: Check if we need a different project configuration
        print(f"\n🧪 TEST 2: Check project configuration")
        
        bedrock_data_automation_client = boto3.client('bedrock-data-automation', region_name=region)
        
        try:
            project_details = bedrock_data_automation_client.get_data_automation_project(
                projectArn=project_arn
            )
            
            project = project_details['project']
            print(f"📋 Project Status: {project.get('status')}")
            print(f"📋 Project Name: {project.get('projectName')}")
            
            # Check if project has required configuration
            if project.get('status') != 'ACTIVE':
                print(f"❌ Project is not ACTIVE: {project.get('status')}")
                print(f"   BDA jobs require ACTIVE projects")
                return {'success': False, 'error': 'Project not active'}
            
            # Look for any profile information in the project
            for key, value in project.items():
                if 'profile' in key.lower() or 'Profile' in key:
                    print(f"📋 Found profile field: {key} = {value}")
            
        except Exception as e:
            print(f"❌ Cannot get project details: {str(e)}")
        
        # Clean up
        s3_client.delete_object(Bucket=test_bucket, Key=test_key)
        s3_client.delete_bucket(Bucket=test_bucket)
        
        return {'success': False, 'error': 'BDA job creation failed'}
        
    except Exception as e:
        print(f"❌ Test setup failed: {str(e)}")
        return {'success': False, 'error': str(e)}

def apply_fix_to_blueprint_processor(working_config):
    """Apply the working BDA configuration to blueprint_processor.py"""
    
    if not working_config.get('success'):
        print("❌ No working configuration to apply")
        return
    
    print(f"\n🔧 APPLYING FIX TO BLUEPRINT PROCESSOR")
    print(f"✅ Working method: {working_config['method']}")
    
    # The fix is simple: remove the dataAutomationProfileArn parameter entirely
    print(f"🎯 SOLUTION: Remove dataAutomationProfileArn from invoke_data_automation_async calls")
    print(f"   Let BDA use the default profile automatically")
    
    # Show the exact working code
    print(f"\n📋 WORKING CODE:")
    print(f"""
bda_response = self.bedrock_data_automation_runtime_client.invoke_data_automation_async(
    inputConfiguration={{
        's3Uri': permanent_s3_uri
    }},
    outputConfiguration={{
        's3Uri': f"s3://{{project_bucket}}/bda-output/"
    }},
    dataAutomationConfiguration={{
        'dataAutomationProjectArn': project_arn
    }}
    # NO dataAutomationProfileArn parameter!
)
""")

def main():
    result = fix_bda_job_creation()
    
    print(f"\n" + "=" * 50)
    print(f"🎯 RESULT:")
    
    if result.get('success'):
        print(f"✅ BDA JOB CREATION FIXED!")
        print(f"   Method: {result['method']}")
        print(f"   Invocation ARN: {result['invocation_arn']}")
        
        apply_fix_to_blueprint_processor(result)
        
    else:
        print(f"❌ BDA JOB CREATION STILL FAILING")
        print(f"   Error: {result.get('error', 'Unknown')}")
        print(f"\n🔧 NEXT ACTIONS:")
        print(f"1. Check if BDA is enabled in your AWS account")
        print(f"2. Verify project status is ACTIVE")
        print(f"3. Check IAM permissions for bedrock-data-automation-runtime")

if __name__ == "__main__":
    main()