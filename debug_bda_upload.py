#!/usr/bin/env python3
"""
Debug BDA upload to see exactly what's happening
"""

import requests
import json
import os

def debug_bda_upload():
    """Debug the BDA upload process"""
    
    print("🔍 Debug BDA Upload Process")
    print("=" * 50)
    
    API_URL = "http://localhost:8000"
    W2_FILE = "test_files/w-2.pdf"
    
    # Check if API is running
    try:
        health = requests.get(f"{API_URL}/health")
        print(f"✅ API Status: {health.status_code}")
    except:
        print("❌ API not running")
        return
    
    # Get projects
    try:
        projects_resp = requests.get(f"{API_URL}/blueprint/projects")
        projects = projects_resp.json().get('projects', [])
        
        # Find a real BDA project
        bda_project = None
        for project in projects:
            if 'bedrock' in project.get('project_arn', '').lower():
                bda_project = project
                break
        
        if not bda_project:
            print("❌ No real BDA project found")
            return
            
        project_name = bda_project['project_name']
        print(f"🎯 Using BDA project: {project_name}")
        print(f"📍 Project ARN: {bda_project['project_arn']}")
        
    except Exception as e:
        print(f"❌ Error getting projects: {e}")
        return
    
    # Upload W-2 with detailed response analysis
    try:
        with open(W2_FILE, 'rb') as f:
            files = {'file': ('w-2.pdf', f, 'application/pdf')}
            
            print(f"\n📤 Uploading W-2 to project: {project_name}")
            upload_resp = requests.post(
                f"{API_URL}/blueprint/project/{project_name}/upload",
                files=files
            )
        
        print(f"📊 Response Status: {upload_resp.status_code}")
        
        if upload_resp.status_code == 200:
            data = upload_resp.json()
            print("\n📋 Full Response Data:")
            print(json.dumps(data, indent=2))
            
            print("\n🔍 Analysis:")
            print(f"Status: {data.get('status', 'Unknown')}")
            print(f"Service: {data.get('service', 'Unknown')}")
            print(f"Message: {data.get('message', 'Unknown')}")
            
            # Check for BDA-specific fields
            invocation_arn = data.get('invocation_arn')
            if invocation_arn:
                print(f"✅ BDA Invocation ARN: {invocation_arn}")
            else:
                print("❌ No invocation_arn in response")
            
            # Check for fallback indicators
            if 'processing_result' in data:
                print("⚠️ Found 'processing_result' - this indicates FALLBACK processing")
                print("   This means BDA job creation failed and it used local Textract instead")
            
            if data.get('service') == 'BDA Project Storage':
                print("⚠️ Service is 'BDA Project Storage' - this indicates FALLBACK")
            
            if data.get('service') == 'Amazon Bedrock Data Automation':
                print("✅ Service is 'Amazon Bedrock Data Automation' - this indicates SUCCESS")
            
            # Check S3 URIs
            s3_uri = data.get('s3_uri') or data.get('document_s3_uri')
            if s3_uri:
                print(f"📄 Document S3 URI: {s3_uri}")
            
            results_uri = data.get('results_s3_uri')
            if results_uri:
                print(f"📊 Results S3 URI: {results_uri}")
                print("⚠️ This suggests fallback processing (local results stored)")
        
        else:
            print(f"❌ Upload failed: {upload_resp.status_code}")
            print(upload_resp.text)
            
    except Exception as e:
        print(f"❌ Upload error: {e}")

def main():
    debug_bda_upload()
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSIS:")
    print("1. If you see 'Amazon Bedrock Data Automation' service → BDA job created successfully")
    print("2. If you see 'BDA Project Storage' service → BDA job failed, used fallback")
    print("3. If you see 'processing_result' in response → Fallback processing was used")
    print("4. If invocation_arn is None → BDA job creation failed")

if __name__ == "__main__":
    main()