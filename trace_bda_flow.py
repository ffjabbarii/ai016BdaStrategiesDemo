#!/usr/bin/env python3
"""
Trace the complete BDA flow to see where it's failing
"""

import requests
import json

def trace_bda_flow():
    """Trace the complete BDA upload flow"""
    
    print("🔍 Tracing BDA Upload Flow")
    print("=" * 50)
    
    API_URL = "http://localhost:8000"
    
    # Step 1: Check API health
    print("📋 Step 1: API Health Check...")
    try:
        health = requests.get(f"{API_URL}/health")
        print(f"✅ API Status: {health.status_code}")
    except Exception as e:
        print(f"❌ API not accessible: {e}")
        return
    
    # Step 2: List projects
    print("\n📋 Step 2: List BDA Projects...")
    try:
        projects_resp = requests.get(f"{API_URL}/blueprint/projects")
        if projects_resp.status_code == 200:
            projects = projects_resp.json().get('projects', [])
            print(f"✅ Found {len(projects)} projects")
            
            bda_project = None
            for project in projects:
                if 'bedrock' in project.get('project_arn', '').lower():
                    bda_project = project
                    print(f"   🎯 BDA Project: {project['project_name']}")
                    print(f"      ARN: {project['project_arn']}")
                    print(f"      Status: {project.get('status', 'Unknown')}")
                    break
            
            if not bda_project:
                print("❌ No BDA project found")
                return
        else:
            print(f"❌ Failed to list projects: {projects_resp.status_code}")
            return
    except Exception as e:
        print(f"❌ Error listing projects: {e}")
        return
    
    # Step 3: Test document upload with detailed tracing
    print(f"\n📋 Step 3: Upload Document with Tracing...")
    project_name = bda_project['project_name']
    
    try:
        # Enable verbose logging by adding a debug parameter
        with open("test_files/w-2.pdf", 'rb') as f:
            files = {'file': ('w-2.pdf', f, 'application/pdf')}
            
            print(f"📤 Uploading to project: {project_name}")
            print(f"   File: test_files/w-2.pdf")
            
            # Make the upload request
            upload_resp = requests.post(
                f"{API_URL}/blueprint/project/{project_name}/upload",
                files=files
            )
        
        print(f"\n📊 Upload Response:")
        print(f"   Status Code: {upload_resp.status_code}")
        
        if upload_resp.status_code == 200:
            data = upload_resp.json()
            print(f"   Response Type: SUCCESS")
            
            # Analyze the response to understand the flow
            print(f"\n🔍 Response Analysis:")
            print(f"   Status: {data.get('status', 'Unknown')}")
            print(f"   Service: {data.get('service', 'Unknown')}")
            print(f"   Message: {data.get('message', 'No message')}")
            
            # Check for BDA-specific indicators
            if data.get('invocation_arn'):
                print(f"✅ BDA Job Created: {data['invocation_arn']}")
                print(f"   This means BDA processing worked!")
            else:
                print(f"❌ No BDA invocation ARN found")
                print(f"   This means BDA job creation failed")
            
            # Check for fallback indicators
            if 'processing_result' in data:
                print(f"⚠️ Found processing_result - indicates fallback processing")
            
            if data.get('service') == 'BDA Project Storage':
                print(f"⚠️ Service is 'BDA Project Storage' - indicates BDA failed, used storage fallback")
            elif data.get('service') == 'Amazon Bedrock Data Automation':
                print(f"✅ Service is 'Amazon Bedrock Data Automation' - BDA success!")
            
            # Show full response for debugging
            print(f"\n📋 Full Response:")
            print(json.dumps(data, indent=2))
            
        else:
            print(f"   Response Type: ERROR")
            try:
                error_data = upload_resp.json()
                print(f"\n❌ Error Details:")
                print(json.dumps(error_data, indent=2))
                
                # Parse the error to understand the failure point
                error_detail = error_data.get('detail', '')
                if 'Document upload failed' in error_detail:
                    print(f"\n🔍 Error Analysis:")
                    print(f"   Failure Point: Document upload/processing")
                    
                    if 'Direct processing failed' in error_detail:
                        print(f"   Issue: BDA failed, direct processing also failed")
                        print(f"   Root Cause: Likely document format or Textract issue")
                    elif 'BDA processing job failed' in error_detail:
                        print(f"   Issue: BDA job creation failed")
                        print(f"   Root Cause: Likely profile ARN or permissions issue")
                    
                    if 'unsupported document format' in error_detail.lower():
                        print(f"   Specific Issue: Document format not supported by Textract")
                        print(f"   Solution: Check PDF conversion logic")
                
            except:
                print(f"   Raw Error: {upload_resp.text}")
    
    except Exception as e:
        print(f"❌ Upload test failed: {e}")

def main():
    trace_bda_flow()
    
    print(f"\n" + "=" * 50)
    print(f"🎯 NEXT STEPS:")
    print(f"1. If BDA job creation is failing → Check profile ARN issue")
    print(f"2. If document format error → Check PyMuPDF and PDF conversion")
    print(f"3. If permissions error → Check AWS IAM permissions")
    print(f"4. If other error → Check the specific error message above")

if __name__ == "__main__":
    main()