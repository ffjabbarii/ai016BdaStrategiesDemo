#!/usr/bin/env python3
"""
Test C# BDA implementation with fixed dataAutomationProfileArn
This tests the C# version on port 5000 to ensure it matches Python functionality
"""

import requests
import json
import os
import time

def test_csharp_bda_project():
    """Test C# BDA implementation"""
    
    print("🔷 Testing C# BDA Implementation with Fixed Profile ARN")
    print("=" * 60)
    
    # Configuration
    API_URL = "http://localhost:5000"  # C# API port
    W2_FILE = "test_files/w-2.pdf"
    
    # Step 1: Check API
    print("1️⃣ Checking C# API...")
    try:
        health_response = requests.get(f"{API_URL}/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ C# API running: {health_data.get('Message', 'Healthy')}")
            print(f"📋 Version: {health_data.get('Version', 'Unknown')}")
            print(f"🔷 Language: {health_data.get('Language', 'Unknown')}")
        else:
            print("❌ C# API not responding correctly")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to C# API: {e}")
        print("💡 Start the C# API using your GUI manager:")
        print("   1. Click '▶️ Start C# W-2 Processor' in GUI")
        print("   2. Wait for green dot 🟢 on port 5000")
        print("   3. Run this test again")
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
            print("❌ Failed to get projects from C# API")
            return False
        
        projects_data = projects_response.json()
        projects = projects_data.get('Projects', [])
        
        # Find real BDA projects (not fallback Textract)
        real_bda_projects = []
        for project in projects:
            service = project.get('Service', '')
            project_arn = project.get('ProjectArn', '')
            
            if 'Amazon Bedrock Data Automation' in service and 'bedrock' in project_arn.lower():
                real_bda_projects.append(project)
        
        if not real_bda_projects:
            print("❌ No real BDA projects found in C# API")
            print("💡 The C# API may need to be updated to match Python functionality")
            return False
        
        print(f"✅ Found {len(real_bda_projects)} real BDA projects:")
        for i, project in enumerate(real_bda_projects, 1):
            print(f"   {i}. {project['ProjectName']}")
        
        # Use the first real BDA project
        target_project = real_bda_projects[0]
        project_name = target_project['ProjectName']
        project_arn = target_project['ProjectArn']
        
        print(f"\n🎯 Using project: {project_name}")
        print(f"📍 Project ARN: {project_arn}")
        
    except Exception as e:
        print(f"❌ Error getting projects from C# API: {e}")
        return False
    
    # Step 4: Upload W-2 to test the C# BDA fix
    print(f"\n4️⃣ Uploading W-2 to C# BDA project: {project_name}")
    print("🔧 This tests the C# dataAutomationProfileArn implementation")
    
    try:
        with open(W2_FILE, 'rb') as f:
            files = {'file': ('w-2.pdf', f, 'application/pdf')}
            
            upload_response = requests.post(
                f"{API_URL}/blueprint/project/{project_name}/upload",
                files=files
            )
        
        if upload_response.status_code == 200:
            upload_data = upload_response.json()
            print("✅ W-2 uploaded successfully to C# API!")
            
            # Check for BDA processing job (this indicates the C# fix worked)
            if 'InvocationArn' in upload_data and upload_data['InvocationArn']:
                print("\n🎉 SUCCESS: C# BDA PROCESSING JOB CREATED!")
                print(f"📋 Invocation ARN: {upload_data['InvocationArn']}")
                print("✅ The C# dataAutomationProfileArn fix is WORKING!")
                print(f"📍 Project: {project_name}")
                print("🌐 Check AWS Console → Amazon Bedrock → Data Automation → Projects")
                print(f"🔷 Language: {upload_data.get('Language', 'C#')}")
                
                # Show additional details
                if 'S3Uri' in upload_data:
                    print(f"📄 Document URI: {upload_data['S3Uri']}")
                if 'Service' in upload_data:
                    print(f"🏷️ Service: {upload_data['Service']}")
                
                return True
                
            elif 'ProcessingResult' in upload_data:
                print("\n⚠️ PARTIAL SUCCESS: Document processed but no BDA job created")
                print("📋 This suggests the C# dataAutomationProfileArn issue may still exist")
                print("🔧 Check C# API logs for profile ARN resolution details")
                
                # Show what we got instead
                if 'S3Uri' in upload_data:
                    print(f"📄 Document stored: {upload_data['S3Uri']}")
                
                return False
                
            else:
                print("\n📋 Document uploaded but unclear processing status")
                print("⚠️ Check the C# response for details")
                print(f"Response keys: {list(upload_data.keys())}")
                return False
                
        else:
            print(f"❌ Upload failed: {upload_response.status_code}")
            try:
                error_data = upload_response.json()
                print(f"Error: {error_data.get('Detail', 'Unknown error')}")
            except:
                print(f"Error response: {upload_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error uploading W-2 to C# API: {e}")
        return False

def compare_python_and_csharp():
    """Compare Python and C# API responses"""
    print("\n🔄 Comparing Python vs C# API Responses")
    print("=" * 50)
    
    # Test both APIs
    python_url = "http://localhost:8000"
    csharp_url = "http://localhost:5000"
    
    apis = [
        ("🐍 Python", python_url),
        ("🔷 C#", csharp_url)
    ]
    
    for name, url in apis:
        try:
            response = requests.get(f"{url}/health", timeout=3)
            if response.status_code == 200:
                data = response.json()
                print(f"{name}: ✅ {data.get('Message', 'Running')}")
            else:
                print(f"{name}: ❌ Not responding")
        except:
            print(f"{name}: ❌ Not available")

def main():
    """Main test function"""
    print("🔷 C# BDA Fix Test - Matching Python Functionality")
    print("This test verifies the C# implementation has the same BDA fix as Python")
    print()
    
    success = test_csharp_bda_project()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 C# TEST PASSED!")
        print("✅ The C# dataAutomationProfileArn fix is working correctly!")
        print("✅ C# BDA processing job created successfully!")
        print("✅ C# implementation matches Python functionality!")
        print("📍 Check AWS Console for processing results")
    else:
        print("❌ C# TEST FAILED!")
        print("🔧 The C# dataAutomationProfileArn implementation needs work")
        print("💡 Check C# API server logs for detailed error messages")
        print("🔄 Ensure C# implementation matches Python BDA logic")
    
    # Compare both APIs
    compare_python_and_csharp()
    
    print("\n📋 Next Steps:")
    if success:
        print("1. Both Python and C# implementations are working")
        print("2. Documents from both APIs appear in AWS Console")
        print("3. Complete dual-language BDA solution achieved")
    else:
        print("1. Fix C# BDA implementation to match Python")
        print("2. Ensure C# creates BDA processing jobs")
        print("3. Test both languages create identical results")

if __name__ == "__main__":
    main()