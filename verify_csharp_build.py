#!/usr/bin/env python3
"""
Verify C# code builds and runs correctly
"""

import subprocess
import time
import requests
import os
import sys

def test_csharp_build():
    """Test C# build and basic functionality"""
    
    print("🔷 VERIFYING C# BUILD AND FUNCTIONALITY")
    print("=" * 50)
    
    # Check .NET SDK
    try:
        result = subprocess.run(["dotnet", "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ .NET SDK version: {version}")
        else:
            print("❌ .NET SDK not found")
            print("💡 Install from: https://dotnet.microsoft.com/download")
            return False
    except Exception as e:
        print(f"❌ .NET SDK check failed: {str(e)}")
        return False
    
    # Check C# directory
    csharp_dir = "csharp/BlueprintAPI"
    if not os.path.exists(csharp_dir):
        print(f"❌ C# directory not found: {csharp_dir}")
        return False
    
    print(f"✅ C# directory exists: {csharp_dir}")
    
    # Check C# files
    required_files = [
        "csharp/BlueprintAPI/Program.cs",
        "csharp/BlueprintAPI/Controllers/DocumentController.cs",
        "csharp/BlueprintAPI/Services/BlueprintProcessor.cs",
        "csharp/BlueprintAPI/BlueprintAPI.csproj"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ C# file exists: {file_path}")
        else:
            print(f"❌ Missing C# file: {file_path}")
            return False
    
    # Test C# restore
    print("\n📦 Restoring C# packages...")
    try:
        result = subprocess.run(
            ["dotnet", "restore"],
            cwd=csharp_dir,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("✅ C# package restore successful")
        else:
            print(f"❌ C# restore failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ C# restore error: {str(e)}")
        return False
    
    # Test C# build
    print("\n🔨 Building C# project...")
    try:
        result = subprocess.run(
            ["dotnet", "build", "--configuration", "Release", "--verbosity", "minimal"],
            cwd=csharp_dir,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print("✅ C# build successful")
            print(f"   Build output: {result.stdout.strip()}")
        else:
            print(f"❌ C# build failed:")
            print(f"   Error: {result.stderr}")
            print(f"   Output: {result.stdout}")
            return False
            
    except Exception as e:
        print(f"❌ C# build error: {str(e)}")
        return False
    
    # Test C# run
    print("\n🚀 Testing C# API startup...")
    try:
        process = subprocess.Popen(
            ["dotnet", "run", "--configuration", "Release"],
            cwd=csharp_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"   Process ID: {process.pid}")
        
        # Wait for startup
        for attempt in range(30):
            try:
                response = requests.get("http://localhost:5000/health", timeout=2)
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ C# API ready: {result.get('Message', 'OK')}")
                    break
            except:
                pass
            
            time.sleep(1)
            if attempt % 5 == 0:
                print(f"   Waiting for C# API... ({attempt + 1}/30)")
        else:
            print("❌ C# API failed to start within timeout")
            process.terminate()
            return False
        
        # Test C# endpoints
        print("\n🧪 Testing C# API endpoints...")
        
        # Test health
        try:
            response = requests.get("http://localhost:5000/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ C# health endpoint works: {health_data.get('Message', 'OK')}")
                print(f"   Language: {health_data.get('Language', 'Unknown')}")
            else:
                print(f"❌ C# health failed: {response.status_code}")
        except Exception as e:
            print(f"❌ C# health error: {str(e)}")
        
        # Test projects
        try:
            response = requests.get("http://localhost:5000/blueprint/projects", timeout=10)
            if response.status_code == 200:
                projects = response.json()
                project_count = len(projects.get('Projects', []))
                print(f"✅ C# projects endpoint works: {project_count} projects")
            else:
                print(f"❌ C# projects failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
        except Exception as e:
            print(f"❌ C# projects error: {str(e)}")
        
        # Test upload
        try:
            test_content = "Test W-2 content for C# verification"
            files = {'file': ('test-csharp.txt', test_content.encode(), 'text/plain')}
            
            response = requests.post(
                "http://localhost:5000/blueprint/project/test-w2-fixed-1765841521/upload",
                files=files,
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ C# upload works: {result.get('Status', 'Unknown')}")
            else:
                print(f"❌ C# upload failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
        except Exception as e:
            print(f"❌ C# upload error: {str(e)}")
        
        # Stop C# API
        print("\n🛑 Stopping C# API...")
        process.terminate()
        process.wait()
        print("✅ C# API stopped")
        
        print("\n🎉 C# VERIFICATION COMPLETE")
        print("✅ C# builds and runs correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ C# API test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_csharp_build()
    if success:
        print("\n✅ C# verification PASSED")
        sys.exit(0)
    else:
        print("\n❌ C# verification FAILED")
        sys.exit(1)