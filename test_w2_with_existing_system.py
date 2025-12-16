#!/usr/bin/env python3
"""
Test W-2 upload with your existing BDA system
This script works with your GUI manager and tests the fixed BDA implementation
"""

import requests
import json
import os
import time

def test_w2_upload():
    """Test W-2 upload using your existing system"""
    
    print("🔥 Testing W-2 Upload with Fixed BDA Implementation")
    print("=" * 60)
    print("This test assumes you've started the Python Blueprint API using your GUI manager")
    print()
    
    # Configuration
    API_URL = "http://localhost:8000"  # Your Python Blueprint API
    W2_FILE = "test_files/w-2.pdf"
    
    # Step 1: Check if API is running
    print("1️⃣ Checking if Python Blueprint API is running...")
    try:
        health_response = requests.get(f"{API_URL}/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ API is running: {health_data.get('message', 'Healthy')}")
            print(f"📋 Version: {health_data.get('version', 'Unknown')}")
        else:
            print(f"❌ API health check failed: {health_response.status_code}")
            print("💡 Start the Python Blueprint API using your GUI manager first")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API on port 8000")
        print("💡 Steps to fix:")
        print("   1. Run: python Startup/startup.py")
        print("   2. Click 'Start W-2 Processor' (Python version)")
        print("   3. Wait for green dot 🟢")
        print("   4. Run this test again")
        return False
    except Exception as e:
        print(f"❌ Error checking API: {e}")
        return False
    
    # Step 2: Check W-2 file
    print(f"\n2️⃣ Checking W-2 file: {W2_FILE}")
    if not os.path.exists(W2_FILE):
        print(f"❌ W-2 file not found: {W2_FILE}")
        print("💡 Make sure the w-2.pdf file exists in test_files directory")
        return False
    
    file_size = os.path.getsize(W2_FILE)
    print(f"✅ W-2 file found ({file_size:,} bytes)")
    
    # Step 3: List existing BDA projects
    print("\n3️⃣ Listing existing BDA projects...")
    try:
        projects_response = requests.get(f"{API_URL}/blueprint/projects")
        if projects_response.status_code == 200:
            projects_data = projects_response.json()
            projects = projects_data.get('projects', [])
            print(f"📋 Found {len(projects)} BDA projects")
            
            # Show project details
            for i, project in enumerate(projects, 1):
                service = project.get('service', 'Unknown')
                status = project.get('status', 'Unknown')
                print(f"   {i}. {project['project_name']} ({service}) - {status}")
                
                # Check if it's a real BDA project
                if 'bedrock' in project.get('project_arn', '').lower():
                    print(f"      🎉 This is a REAL Amazon Bedrock Data Automation project!")
                else:
                    print(f"      ⚠️ This is a fallback Textract project")
        else:
            print(f"❌ Failed to list projects: {projects_response.status_code}")
            projects = []
    except Exception as e:
        print(f"❌ Error listing projects: {e}")
        projects = []
    
    # Step 4: Create a new BDA project for testing
    print("\n4️⃣ Creating new BDA project for testing...")
    project_name = f"test-w2-fixed-{int(time.time())}"
    
    try:
        create_response = requests.post(
            f"{API_URL}/blueprint/create",
            params={
                'project_name': project_name,
                'document_type': 'w2',
                'description': 'Test project with fixed dataAutomationProfileArn'
            }
        )
        
        if create_response.status_code == 200:
            create_data = create_response.json()
            print(f"✅ BDA project created: {create_data['project_name']}")
            print(f"📍 Project ARN: {create_data.get('project_arn', 'N/A')}")
            
            # Check if it's a real BDA project
            if 'bedrock' in create_data.get('project_arn', '').lower():
                print("🎉 SUCCESS: Real Amazon Bedrock Data Automation project created!")
            else:
                print("⚠️ Fallback Textract project created (BDA not available)")
        else:
            print(f"❌ Project creation failed: {create_response.status_code}")
            try:
                error_data = create_response.json()
                print(f"Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"Error response: {create_response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating project: {e}")
        return False
    
    # Step 5: Upload W-2 to the new project (this tests the fix)
    print(f"\n5️⃣ Uploading W-2 to project: {project_name}")
    print("🔧 This will test the FIXED dataAutomationProfileArn implementation")
    
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
            print(f"📍 S3 URI: {upload_data.get('s3_uri', 'N/A')}")
            print(f"🏷️ Service: {upload_data.get('service', 'N/A')}")
            
            # Check for BDA processing job (this indicates the fix worked)
            if 'invocation_arn' in upload_data:
                print("\n🎉 SUCCESS: BDA PROCESSING JOB CREATED!")
                print(f"📋 Invocation ARN: {upload_data['invocation_arn']}")
                print("✅ The dataAutomationProfileArn fix is working!")
                print("📍 Check AWS Console → Amazon Bedrock → Data Automation → Projects")
                print(f"🔍 Look for project: {project_name}")
                return True
            elif 'processing_result' in upload_data:
                print("\n⚠️ PARTIAL SUCCESS: Document processed but no BDA job created")
                print("📋 This means the dataAutomationProfileArn issue may still exist")
                print("🔧 Check the API logs for profile ARN resolution details")
                return False
            else:
                print("\n📋 Document uploaded to S3 storage")
                print("⚠️ No BDA processing job created - check implementation")
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
    print("🔥 BDA W-2 Test - Works with Your Existing System")
    print("This test uses your GUI manager's Python Blueprint API on port 8000")
    print()
    
    success = test_w2_upload()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TEST PASSED!")
        print("✅ The dataAutomationProfileArn fix is working correctly")
        print("✅ Your W-2 document should appear in the BDA project interface")
        print("📍 Next: Check AWS Console → Amazon Bedrock → Data Automation")
    else:
        print("❌ TEST FAILED!")
        print("🔧 The dataAutomationProfileArn issue may still need attention")
        print("💡 Check the API server logs for detailed error messages")
    
    print("\n📋 System Integration:")
    print("✅ Works with your existing GUI manager")
    print("✅ Uses your Python Blueprint API (port 8000)")
    print("✅ No need for separate scripts")

if __name__ == "__main__":
    main()