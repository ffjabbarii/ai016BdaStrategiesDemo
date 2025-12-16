#!/usr/bin/env python3
"""
Check if our project ARN is valid and get the correct format
"""

import boto3
import json

def check_project_arn():
    """Check project ARN validity"""
    
    print("🔍 CHECKING PROJECT ARN VALIDITY")
    print("=" * 50)
    
    bda_client = boto3.client('bedrock-data-automation', region_name='us-east-1')
    
    # Our current project ARN
    current_project_arn = "arn:aws:bedrock:us-east-1:624706593351:data-automation-project/a07a2d75b205"
    
    print(f"🎯 Current project ARN: {current_project_arn}")
    
    # List all projects to see the correct format
    try:
        response = bda_client.list_data_automation_projects()
        projects = response.get('projects', [])
        
        print(f"\n📋 All project ARNs in your account:")
        
        for i, project in enumerate(projects, 1):
            project_arn = project.get('projectArn')
            project_name = project.get('projectName')
            
            print(f"{i}. {project_name}")
            print(f"   ARN: {project_arn}")
            
            # Check if this matches our current ARN
            if project_arn == current_project_arn:
                print(f"   ✅ This matches our current ARN")
            
            # Test this project ARN with BDA
            print(f"   🧪 Testing this ARN with BDA...")
            
            try:
                # Test with a minimal BDA call
                runtime_client = boto3.client('bedrock-data-automation-runtime', region_name='us-east-1')
                
                # We can't actually call it without S3 setup, but we can check the ARN format
                # by looking at the project details
                project_details = bda_client.get_data_automation_project(projectArn=project_arn)
                
                print(f"   ✅ Project ARN is valid (can retrieve details)")
                print(f"   Status: {project_details['project'].get('status')}")
                
            except Exception as e:
                print(f"   ❌ Project ARN issue: {str(e)}")
        
        # Find our target project
        target_project = None
        for project in projects:
            if project.get('projectName') == 'test-w2-fixed-1765841521':
                target_project = project
                break
        
        if target_project:
            correct_arn = target_project['projectArn']
            print(f"\n🎯 CORRECT ARN FOR OUR PROJECT:")
            print(f"   Project Name: {target_project['projectName']}")
            print(f"   Correct ARN: {correct_arn}")
            
            if correct_arn != current_project_arn:
                print(f"   ❌ Our ARN is WRONG!")
                print(f"   Current: {current_project_arn}")
                print(f"   Correct: {correct_arn}")
                return correct_arn
            else:
                print(f"   ✅ Our ARN is correct")
                
                # If ARN is correct but still failing, check project status
                project_details = bda_client.get_data_automation_project(projectArn=correct_arn)
                status = project_details['project'].get('status')
                
                if status != 'COMPLETED':
                    print(f"   ⚠️ Project status: {status} (should be COMPLETED)")
                else:
                    print(f"   ✅ Project status: {status}")
                
                return correct_arn
        else:
            print(f"\n❌ Target project 'test-w2-fixed-1765841521' not found!")
            return None
            
    except Exception as e:
        print(f"❌ Error checking projects: {str(e)}")
        return None

def test_with_correct_arn(correct_arn):
    """Test BDA with the correct project ARN"""
    
    if not correct_arn:
        return
    
    print(f"\n🧪 TESTING WITH CORRECT PROJECT ARN")
    print("=" * 50)
    
    runtime_client = boto3.client('bedrock-data-automation-runtime', region_name='us-east-1')
    s3_client = boto3.client('s3', region_name='us-east-1')
    
    # Create test setup
    import time
    test_bucket = f"bda-correct-arn-test-{int(time.time())}"
    
    try:
        s3_client.create_bucket(Bucket=test_bucket)
        
        test_content = "Test W-2 content"
        test_key = "test-w2.txt"
        s3_client.put_object(
            Bucket=test_bucket,
            Key=test_key,
            Body=test_content.encode('utf-8'),
            ContentType='text/plain'
        )
        
        input_s3_uri = f"s3://{test_bucket}/{test_key}"
        output_s3_uri = f"s3://{test_bucket}/output/"
        profile_arn = "arn:aws:bedrock:us-east-1:aws:data-automation-profile/default"
        
        print(f"📤 Input: {input_s3_uri}")
        print(f"🎯 Correct Project ARN: {correct_arn}")
        print(f"👤 Profile ARN: {profile_arn}")
        
        try:
            response = runtime_client.invoke_data_automation_async(
                inputConfiguration={
                    's3Uri': input_s3_uri
                },
                outputConfiguration={
                    's3Uri': output_s3_uri
                },
                dataAutomationConfiguration={
                    'dataAutomationProjectArn': correct_arn
                },
                dataAutomationProfileArn=profile_arn
            )
            
            invocation_arn = response.get('invocationArn')
            print(f"\n✅ SUCCESS! BDA JOB CREATED!")
            print(f"   Invocation ARN: {invocation_arn}")
            print(f"   Full Response: {response}")
            
            # Clean up
            s3_client.delete_object(Bucket=test_bucket, Key=test_key)
            s3_client.delete_bucket(Bucket=test_bucket)
            
            return True
            
        except Exception as e:
            print(f"\n❌ Still failed with correct ARN:")
            print(f"   Error: {str(e)}")
            
            # Clean up
            s3_client.delete_object(Bucket=test_bucket, Key=test_key)
            s3_client.delete_bucket(Bucket=test_bucket)
            
            return False
    
    except Exception as e:
        print(f"❌ Test setup failed: {str(e)}")
        return False

def main():
    print("🚀 PROJECT ARN VALIDATION")
    print("=" * 30)
    
    # Check project ARN
    correct_arn = check_project_arn()
    
    # Test with correct ARN
    if correct_arn:
        success = test_with_correct_arn(correct_arn)
        
        print(f"\n" + "=" * 50)
        print(f"🎯 FINAL RESULT:")
        
        if success:
            print(f"✅ BDA WORKING WITH CORRECT PROJECT ARN!")
            print(f"   Update blueprint processor with: {correct_arn}")
        else:
            print(f"❌ Still failing even with correct project ARN")
            print(f"   There may be other issues with BDA setup")
    else:
        print(f"\n❌ Could not determine correct project ARN")

if __name__ == "__main__":
    main()