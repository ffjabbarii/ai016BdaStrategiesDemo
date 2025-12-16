#!/usr/bin/env python3
"""
Restart the API server and test the BDA fix
"""

import subprocess
import time
import requests
import os
import signal

def cleanup_port_8000():
    """Clean up port 8000"""
    try:
        result = subprocess.run(['lsof', '-ti', ':8000'], 
                              capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid_str in pids:
                if pid_str.strip().isdigit():
                    pid = int(pid_str)
                    print(f"🔄 Stopping process {pid} on port 8000...")
                    try:
                        os.kill(pid, signal.SIGTERM)
                        time.sleep(2)
                        os.kill(pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    print(f"✅ Process {pid} stopped")
        else:
            print("✅ Port 8000 is free")
    except Exception as e:
        print(f"⚠️ Error cleaning port: {e}")

def start_api_server():
    """Start the API server"""
    print("🚀 Starting API server with updated code...")
    
    api_dir = "python/BlueprintAPI/src"
    
    # Start the server in background
    process = subprocess.Popen(
        ["python", "api.py"],
        cwd=api_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for startup
    print("⏳ Waiting for API to start...")
    for i in range(10):
        time.sleep(1)
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print("✅ API server started successfully!")
                return process
        except:
            continue
    
    print("❌ API server failed to start")
    return None

def test_bda_upload():
    """Test BDA upload"""
    print("\n🧪 Testing BDA upload...")
    
    try:
        # Test with a simple project list first
        response = requests.get("http://localhost:8000/blueprint/projects")
        if response.status_code == 200:
            print("✅ API responding correctly")
            
            # Now run the actual test
            result = subprocess.run(["python", "test_existing_bda_project.py"], 
                                  capture_output=True, text=True)
            
            print("📋 Test output:")
            print(result.stdout)
            if result.stderr:
                print("❌ Errors:")
                print(result.stderr)
                
            return "SUCCESS" in result.stdout
        else:
            print(f"❌ API not responding: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main function"""
    print("🔄 Restarting API Server and Testing BDA Fix")
    print("=" * 50)
    
    # Step 1: Clean up port
    cleanup_port_8000()
    
    # Step 2: Start API server
    process = start_api_server()
    if not process:
        return
    
    try:
        # Step 3: Test BDA upload
        success = test_bda_upload()
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 BDA FIX TEST PASSED!")
        else:
            print("❌ BDA FIX TEST FAILED!")
            
    finally:
        # Clean up
        print("\n🛑 Stopping API server...")
        try:
            process.terminate()
            time.sleep(2)
            process.kill()
        except:
            pass

if __name__ == "__main__":
    main()