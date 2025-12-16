#!/usr/bin/env python3
"""
Test C# BDA setup and basic functionality
"""

import subprocess
import time
import requests
import os
import signal

def cleanup_port_5000():
    """Clean up port 5000"""
    try:
        result = subprocess.run(['lsof', '-ti', ':5000'], 
                              capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid_str in pids:
                if pid_str.strip().isdigit():
                    pid = int(pid_str)
                    print(f"🔄 Stopping process {pid} on port 5000...")
                    try:
                        os.kill(pid, signal.SIGTERM)
                        time.sleep(2)
                        os.kill(pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    print(f"✅ Process {pid} stopped")
        else:
            print("✅ Port 5000 is free")
    except Exception as e:
        print(f"⚠️ Error cleaning port: {e}")

def test_csharp_compilation():
    """Test if C# project compiles"""
    print("🔷 Testing C# Project Compilation...")
    
    csharp_dir = "csharp/BlueprintAPI"
    
    try:
        # Try to restore packages
        print("📦 Restoring NuGet packages...")
        restore_result = subprocess.run(
            ["dotnet", "restore"],
            cwd=csharp_dir,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if restore_result.returncode != 0:
            print("❌ Package restore failed:")
            print(restore_result.stderr)
            return False
        
        print("✅ Packages restored successfully")
        
        # Try to build
        print("🔨 Building C# project...")
        build_result = subprocess.run(
            ["dotnet", "build"],
            cwd=csharp_dir,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if build_result.returncode != 0:
            print("❌ Build failed:")
            print(build_result.stderr)
            return False
        
        print("✅ C# project built successfully")
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ Build timed out")
        return False
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

def start_csharp_api():
    """Start the C# API"""
    print("🚀 Starting C# API...")
    
    csharp_dir = "csharp/BlueprintAPI"
    
    try:
        # Start the C# API
        process = subprocess.Popen(
            ["dotnet", "run"],
            cwd=csharp_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for startup
        print("⏳ Waiting for C# API to start...")
        for i in range(15):  # Wait up to 15 seconds
            time.sleep(1)
            try:
                response = requests.get("http://localhost:5000/health", timeout=2)
                if response.status_code == 200:
                    print("✅ C# API started successfully!")
                    return process
            except:
                continue
        
        print("❌ C# API failed to start within 15 seconds")
        process.terminate()
        return None
        
    except Exception as e:
        print(f"❌ Error starting C# API: {e}")
        return None

def test_csharp_api():
    """Test basic C# API functionality"""
    print("\n🧪 Testing C# API endpoints...")
    
    base_url = "http://localhost:5000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check: {data.get('Message', 'OK')}")
            print(f"🔷 Language: {data.get('Language', 'Unknown')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test projects endpoint
    try:
        response = requests.get(f"{base_url}/blueprint/projects")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Projects endpoint: Found {data.get('Count', 0)} projects")
        else:
            print(f"❌ Projects endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Projects endpoint error: {e}")
        return False
    
    print("✅ C# API basic tests passed!")
    return True

def main():
    """Main test function"""
    print("🔷 C# BDA Setup Test")
    print("=" * 40)
    
    # Step 1: Clean up port
    cleanup_port_5000()
    
    # Step 2: Test compilation
    if not test_csharp_compilation():
        print("\n❌ C# compilation failed!")
        print("💡 Check the error messages above")
        return
    
    # Step 3: Start API
    process = start_csharp_api()
    if not process:
        print("\n❌ Failed to start C# API!")
        return
    
    try:
        # Step 4: Test API
        if test_csharp_api():
            print("\n🎉 C# BDA Setup Test PASSED!")
            print("✅ C# project compiles and runs")
            print("✅ BDA packages are working")
            print("✅ API endpoints respond correctly")
            print("\n📋 Next: Test BDA functionality with:")
            print("python test_csharp_bda_project.py")
        else:
            print("\n❌ C# API tests failed!")
            
    finally:
        # Clean up
        print("\n🛑 Stopping C# API...")
        try:
            process.terminate()
            time.sleep(2)
            process.kill()
        except:
            pass

if __name__ == "__main__":
    main()