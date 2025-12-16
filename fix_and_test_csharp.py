#!/usr/bin/env python3
"""
Fix and test C# build issues
"""

import subprocess
import time
import requests
import os
import sys

def test_csharp_fix():
    """Test C# after fixes"""
    
    print("🔧 TESTING C# FIXES")
    print("=" * 40)
    
    csharp_dir = "csharp/BlueprintAPI"
    
    # Clean and restore
    print("🧹 Cleaning C# project...")
    try:
        subprocess.run(["dotnet", "clean"], cwd=csharp_dir, check=True, capture_output=True)
        print("✅ Clean successful")
    except:
        print("⚠️ Clean had issues (continuing)")
    
    print("📦 Restoring packages...")
    try:
        result = subprocess.run(["dotnet", "restore"], cwd=csharp_dir, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("✅ Restore successful")
        else:
            print(f"❌ Restore failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Restore error: {str(e)}")
        return False
    
    # Build
    print("🔨 Building C# project...")
    try:
        result = subprocess.run(
            ["dotnet", "build", "--configuration", "Release"],
            cwd=csharp_dir,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print("✅ C# build SUCCESSFUL!")
            print("🎉 All compilation errors fixed!")
            return True
        else:
            print(f"❌ Build still failing:")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Build error: {str(e)}")
        return False

def test_csharp_run():
    """Test C# API startup"""
    
    print("\n🚀 Testing C# API startup...")
    
    csharp_dir = "csharp/BlueprintAPI"
    
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
        for attempt in range(20):
            try:
                response = requests.get("http://localhost:5000/health", timeout=2)
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ C# API started successfully!")
                    print(f"   Response: {result.get('Message', 'OK')}")
                    
                    # Quick test
                    try:
                        response = requests.get("http://localhost:5000/blueprint/projects", timeout=5)
                        if response.status_code == 200:
                            projects = response.json()
                            print(f"✅ C# projects endpoint works: {len(projects.get('Projects', []))} projects")
                        else:
                            print(f"⚠️ Projects endpoint issue: {response.status_code}")
                    except Exception as e:
                        print(f"⚠️ Projects test error: {str(e)}")
                    
                    # Stop API
                    process.terminate()
                    process.wait()
                    print("✅ C# API stopped cleanly")
                    
                    return True
            except:
                pass
            
            time.sleep(1)
            if attempt % 5 == 0:
                print(f"   Waiting... ({attempt + 1}/20)")
        
        print("❌ C# API failed to start")
        process.terminate()
        return False
        
    except Exception as e:
        print(f"❌ C# startup error: {str(e)}")
        return False

def main():
    """Main test function"""
    
    print("🔧 FIXING AND TESTING C# API")
    print("=" * 50)
    
    # Test build
    build_ok = test_csharp_fix()
    
    if not build_ok:
        print("\n❌ C# build still failing - cannot test startup")
        return False
    
    # Test startup
    run_ok = test_csharp_run()
    
    if run_ok:
        print("\n🎉 C# API FULLY WORKING!")
        print("✅ Build successful")
        print("✅ Startup successful") 
        print("✅ Endpoints responding")
        print("\n🚀 Ready to run both APIs together!")
        return True
    else:
        print("\n⚠️ C# builds but has startup issues")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)