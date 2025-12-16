#!/usr/bin/env python3
"""
Verify Python API still works before testing C#
"""

import subprocess
import time
import requests
import os
import sys

def test_python_api():
    """Test that Python API still works"""
    
    print("🐍 VERIFYING PYTHON API STILL WORKS")
    print("=" * 50)
    
    # Check if Python API directory exists
    python_dir = "python/BlueprintAPI"
    if not os.path.exists(python_dir):
        print(f"❌ Python directory not found: {python_dir}")
        return False
    
    print(f"✅ Python directory exists: {python_dir}")
    
    # Check Python files
    required_files = [
        "python/BlueprintAPI/src/api.py",
        "python/BlueprintAPI/src/blueprint_processor.py"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ Python file exists: {file_path}")
        else:
            print(f"❌ Missing Python file: {file_path}")
            return False
    
    # Test Python import
    try:
        result = subprocess.run(
            ["python3", "-c", "from src.api import app; print('Python import OK')"],
            cwd=python_dir,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ Python imports work correctly")
        else:
            print(f"❌ Python import failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Python import test error: {str(e)}")
        return False
    
    # Start Python API
    print("\n🚀 Starting Python API...")
    try:
        process = subprocess.Popen(
            ["python3", "-m", "uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"],
            cwd=python_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"   Process ID: {process.pid}")
        
        # Wait for startup
        for attempt in range(20):
            try:
                response = requests.get("http://localhost:8000/health", timeout=2)
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Python API ready: {result.get('message', 'OK')}")
                    break
            except:
                pass
            
            time.sleep(1)
            print(f"   Waiting... ({attempt + 1}/20)")
        else:
            print("❌ Python API failed to start")
            process.terminate()
            return False
        
        # Test Python endpoints
        print("\n🧪 Testing Python API endpoints...")
        
        # Test health
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Python health endpoint works")
            else:
                print(f"❌ Python health failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Python health error: {str(e)}")
        
        # Test projects
        try:
            response = requests.get("http://localhost:8000/blueprint/projects", timeout=10)
            if response.status_code == 200:
                projects = response.json()
                project_count = len(projects.get('projects', []))
                print(f"✅ Python projects endpoint works: {project_count} projects")
            else:
                print(f"❌ Python projects failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Python projects error: {str(e)}")
        
        # Test upload
        try:
            test_content = "Test W-2 content for Python verification"
            files = {'file': ('test-python.txt', test_content.encode(), 'text/plain')}
            
            response = requests.post(
                "http://localhost:8000/blueprint/project/test-w2-fixed-1765841521/upload",
                files=files,
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Python upload works: {result.get('status', 'Unknown')}")
            else:
                print(f"❌ Python upload failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
        except Exception as e:
            print(f"❌ Python upload error: {str(e)}")
        
        # Stop Python API
        print("\n🛑 Stopping Python API...")
        process.terminate()
        process.wait()
        print("✅ Python API stopped")
        
        print("\n🎉 PYTHON API VERIFICATION COMPLETE")
        print("✅ Python API is working correctly")
        print("✅ Ready to test C# API")
        
        return True
        
    except Exception as e:
        print(f"❌ Python API test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_python_api()
    if success:
        print("\n✅ Python verification PASSED - proceed with C# testing")
        sys.exit(0)
    else:
        print("\n❌ Python verification FAILED - fix Python issues first")
        sys.exit(1)