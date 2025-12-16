#!/usr/bin/env python3
"""
Start the C# BDA API and test it
"""

import subprocess
import time
import requests
import os
import signal
import sys

def start_csharp_api():
    """Start the C# BDA API"""
    
    print("🚀 STARTING C# BDA API 🚀")
    print("=" * 50)
    
    # Change to C# directory
    csharp_dir = "csharp/BlueprintAPI"
    
    if not os.path.exists(csharp_dir):
        print(f"❌ C# directory not found: {csharp_dir}")
        return None
    
    print(f"📁 Changing to directory: {csharp_dir}")
    
    try:
        # Start the C# API
        print("🔥 Starting C# .NET API...")
        process = subprocess.Popen(
            ["dotnet", "run"],
            cwd=csharp_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"✅ C# API started with PID: {process.pid}")
        print("⏳ Waiting for API to be ready...")
        
        # Wait for API to start
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                response = requests.get("http://localhost:5000/health", timeout=2)
                if response.status_code == 200:
                    print("✅ C# API is ready!")
                    return process
            except:
                pass
            
            print(f"   Attempt {attempt + 1}/{max_attempts}...")
            time.sleep(2)
        
        print("❌ C# API failed to start within timeout")
        process.terminate()
        return None
        
    except FileNotFoundError:
        print("❌ .NET SDK not found. Please install .NET 8.0 SDK")
        print("💡 Download from: https://dotnet.microsoft.com/download")
        return None
    except Exception as e:
        print(f"❌ Failed to start C# API: {str(e)}")
        return None

def test_and_run():
    """Start C# API and run tests"""
    
    process = None
    
    def signal_handler(sig, frame):
        print("\n🛑 Shutting down C# API...")
        if process:
            process.terminate()
            process.wait()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Start C# API
        process = start_csharp_api()
        
        if not process:
            print("❌ Failed to start C# API")
            return
        
        # Run tests
        print("\n🧪 Running C# API tests...")
        test_result = subprocess.run(["python3", "test_csharp_bda_api.py"], 
                                   capture_output=False, text=True)
        
        if test_result.returncode == 0:
            print("\n✅ All C# API tests passed!")
        else:
            print("\n❌ Some C# API tests failed")
        
        print("\n🔥 C# API is running on http://localhost:5000")
        print("📋 Available endpoints:")
        print("   GET  /health - Health check")
        print("   GET  /blueprint/projects - List projects")
        print("   POST /blueprint/project/{name}/upload - Upload document")
        print("   POST /process/w2 - Process W-2 document")
        print("\n⏳ Press Ctrl+C to stop...")
        
        # Keep running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    finally:
        if process:
            process.terminate()
            process.wait()

if __name__ == "__main__":
    test_and_run()