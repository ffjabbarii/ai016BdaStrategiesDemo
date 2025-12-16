#!/usr/bin/env python3
"""
Test W-2 upload to existing BDA project
This tests the fixed dataAutomationProfileArn with your existing real BDA projects
"""

import requests
import json
import os
import time

def test_existing_bda_project():
    """Test W-2 upload to existing BDA project"""
    
    print("🔥 Testing W-2 Upload to Existing BDA Project")
    print("=" * 60)
    
    # Configuration
    API_URL = "http://localhost:8000"
    W2_FILE = "test_files/w-2.pdf"
    
    # Step 1: Check API
    print("1️⃣ Checking API...")
    try:
        health_response = requests.get(f"{API_URL}/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ API running: {health_data.get('message', 'Healthy')}")
        else:
            print("❌ API not responding correctly")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return False
    
    # Step 2: Check W-2 file
    print(f"\n2️⃣ Checking W-2 file...")
    if not os.path.exists(W2_FILE):
        print(f"❌ W-2 file not found: {W2_FILE}")
        return False
    
    file_size = os.path.getsize(W2_FILE)
    print(f"✅ W-2 file found ({file_size:,} bytes)")
    
    # Step 3: Get existing BDA projects
    print("\n3️⃣ Finding real BDA projects...")
    try:
        projects_response = requests.get(f"{API_URL}/blueprint/projects")
        if projects_response.status_code != 200:
            print("❌ Failed to get projects")
            return False
        
        projects_data = projects_response.json()
        projects = projects_data.get('projects', [])
        
        # Find real BDA projects (not fallback Textract)
        real_bda_projects = []
        for project in projects:
            service = project.get('service', '')
            project_arn = project.get('project_arn', '')
            
            if 'Amazon Bedrock Data Automation' in service and 'bedrock' in project_arn.lower():
                real_bda_projects.append(project)
        
        if not real_bda_projects:
            print("❌ No real BDA projects found")
            return False
        
        print(f"✅ Found {len(real_bda_projects)} real BDA projects:")
        for i, project in enumerate(real_bda_projects, 1):
            print(f"   {i}. {project['project_name']}")
        
        # Use the first real BDA project
        target_project = real_bda_projects[0]
        project_name = target_project['project_name']
        project_arn = target_project['project_arn']
        
        print(f"\n🎯 Using project: {project_name}")
        print(f"📍 Project ARN: {project_arn}")
        
    except Exception as e:
        print(f"❌ Error getting projects: {e}")
        return False
    
    # Step 4: Upload W-2 to test the BDA fix
    print(f"\n4️⃣ Uploading W-2 to BDA project: {project_name}")
    print("🔧 This tests the FIXED dataAutomationProfileArn implementation")
    
    try:
        with open(W2_FILE, 'rb') as f:
            files = {'file': ('w-2.pdf', f, 'application/pdf')}
            
            upload_response = requests.post(
                f"{API_URL}/blueprint/project/{project_name}/upload",
                files=files
            )
        
        if upload_response.status_code == 200:
            upload_data = upload_response.json()
            print("✅ W-2 uploaded successfully!")
            
            # Check for BDA processing job (this indicates the fix worked)
            if 'invocation_arn' in upload_data:
                print("\n🎉 SUCCESS: BDA PROCESSING JOB CREATED!")
                print(f"📋 Invocation ARN: {upload_data['invocation_arn']}")
                print("✅ The dataAutomationProfileArn fix is WORKING!")
                print(f"📍 Project: {project_name}")
                print("🌐 Check AWS Console → Amazon Bedrock → Data Automation → Projects")
                
                # Show additional details
                if 'document_s3_uri' in upload_data:
                    print(f"📄 Document URI: {upload_data['document_s3_uri']}")
                if 'project_bucket' in upload_data:
                    print(f"🪣 Project Bucket: {upload_data['project_bucket']}")
                
                return True
                
            elif 'processing_result' in upload_data:
                print("\n⚠️ PARTIAL SUCCESS: Document processed but no BDA job created")
                print("📋 This suggests the dataAutomationProfileArn issue may still exist")
                print("🔧 Check API logs for profile ARN resolution details")
                
                # Show what we got instead
                if 's3_uri' in upload_data:
                    print(f"📄 Document stored: {upload_data['s3_uri']}")
                
                return False
                
            else:
                print("\n📋 Document uploaded but unclear processing status")
                print("⚠️ Check the response for details")
                print(f"Response keys: {list(upload_data.keys())}")
                return False
                
        else:
            print(f"❌ Upload failed: {upload_response.status_code}")
            try:
                error_data = upload_response.json()
                print(f"Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"Error response: {upload_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error uploading W-2: {e}")
        return False

def main():
    """Main test function"""
    print("🔥 BDA Fix Test - Using Existing Real BDA Projects")
    print("This test uses your existing real Amazon Bedrock Data Automation projects")
    print()
    
    success = test_existing_bda_project()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TEST PASSED!")
        print("✅ The dataAutomationProfileArn fix is working correctly!")
        print("✅ BDA processing job created successfully!")
        print("📍 Check AWS Console for processing results")
    else:
        print("❌ TEST FAILED!")
        print("🔧 The dataAutomationProfileArn issue may need more work")
        print("💡 Check API server logs for detailed error messages")
    
    print("\n📋 Next Steps:")
    if success:
        print("1. Go to AWS Console → Amazon Bedrock → Data Automation")
        print("2. Find your project and check processing jobs")
        print("3. View extracted W-2 fields and results")
    else:
        print("1. Check API server logs for profile ARN errors")
        print("2. Verify AWS credentials and permissions")
        print("3. Test with a smaller document first")

if __name__ == "__main__":
    main()