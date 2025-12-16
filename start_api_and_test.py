#!/usr/bin/env python3
"""
Start the API and test BDA upload
"""

import subprocess
import time
import requests
import signal
import os

def start_api_and_test():
    """Start API and test BDA upload"""
    
    print("🚀 STARTING API AND TESTING BDA")
    print("=" * 50)
    
    # Start the API server
    print("🔧 Starting Python API server...")
    
    api_process = subprocess.Popen([
        "python", "-m", "uvicorn", 
        "python.BlueprintAPI.src.api:app", 
        "--host", "0.0.0.0", 
        "--port", "8000"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for API to start
    print("⏳ Waiting for API to start...")
    time.sleep(5)
    
    try:
        # Test API health
        print("🔍 Testing API health...")
        health_response = requests.get("http://localhost:8000/health", timeout=5)
        
        if health_response.status_code == 200:
            print("✅ API is running successfully")
            
            # Test BDA upload
            print("\n🧪 Testing BDA upload...")
            
            try:
                with open("test_files/w-2.pdf", 'rb') as f:
                    files = {'file': ('w-2.pdf', f, 'application/pdf')}
                    
                    upload_response = requests.post(
                        "http://localhost:8000/blueprint/project/test-w2-fixed-1765841521/upload",
                        files=files,
                        timeout=30
                    )
                
                print(f"📊 Upload Response Status: {upload_response.status_code}")
                
                if upload_response.status_code == 200:
                    data = upload_response.json()
                    print("✅ UPLOAD SUCCESSFUL!")
                    
                    # Check what type of processing was used
                    service = data.get('service', 'Unknown')
                    invocation_arn = data.get('invocation_arn')
                    
                    if invocation_arn:
                        print(f"🎯 BDA JOB CREATED: {invocation_arn}")
                        print(f"✅ Service: {service}")
                        print("🎉 BDA IS WORKING!")
                    elif service == 'BDA Project Storage':
                        print(f"⚠️ BDA job failed, but document stored")
                        print(f"   Service: {service}")
                    else:
                        print(f"ℹ️ Processing service: {service}")
                    
                    print(f"\n📋 Full response:")
                    import json
                    print(json.dumps(data, indent=2))
                    
                else:
                    print("❌ UPLOAD FAILED")
                    try:
                        error_data = upload_response.json()
                        print("Error details:")
                        import json
                        print(json.dumps(error_data, indent=2))
                    except:
                        print(f"Raw error: {upload_response.text}")
                        
            except Exception as e:
                print(f"❌ Upload test failed: {str(e)}")
        
        else:
            print(f"❌ API health check failed: {health_response.status_code}")
    
    except Exception as e:
        print(f"❌ API test failed: {str(e)}")
    
    finally:
        # Stop the API server
        print(f"\n🛑 Stopping API server...")
        api_process.terminate()
        
        # Wait a bit for graceful shutdown
        time.sleep(2)
        
        # Force kill if still running
        try:
            api_process.kill()
        except:
            pass
        
        print("✅ API server stopped")

if __name__ == "__main__":
    start_api_and_test()