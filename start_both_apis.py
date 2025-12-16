#!/usr/bin/env python3
"""
Start Both APIs - Python and C# BDA APIs
Manages both APIs simultaneously for development and testing
"""

import subprocess
import time
import requests
import os
import signal
import sys
import threading
from datetime import datetime

class DualAPIManager:
    def __init__(self):
        self.python_process = None
        self.csharp_process = None
        self.python_port = 8000
        self.csharp_port = 5000
        self.running = True
        
    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "=" * 60)
        print(f"🚀 {title}")
        print("=" * 60)
    
    def start_python_api(self):
        """Start Python API in background"""
        try:
            print("🐍 Starting Python API...")
            
            # Check if Python API directory exists
            python_dir = "python/BlueprintAPI"
            if not os.path.exists(python_dir):
                print(f"❌ Python directory not found: {python_dir}")
                return False
            
            # Start Python API
            self.python_process = subprocess.Popen(
                ["python3", "-m", "uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", str(self.python_port), "--reload"],
                cwd=python_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            print(f"   Process ID: {self.python_process.pid}")
            print(f"   Port: {self.python_port}")
            
            # Wait for startup
            for attempt in range(20):
                try:
                    response = requests.get(f"http://localhost:{self.python_port}/health", timeout=2)
                    if response.status_code == 200:
                        result = response.json()
                        print(f"✅ Python API ready: {result.get('Message', 'OK')}")
                        return True
                except:
                    pass
                
                time.sleep(1)
                if attempt % 5 == 0:
                    print(f"   Waiting for Python API... ({attempt + 1}/20)")
            
            print("❌ Python API failed to start within timeout")
            return False
            
        except Exception as e:
            print(f"❌ Failed to start Python API: {str(e)}")
            return False
    
    def start_csharp_api(self):
        """Start C# API in background"""
        try:
            print("🔷 Starting C# API...")
            
            # Check if C# API directory exists
            csharp_dir = "csharp/BlueprintAPI"
            if not os.path.exists(csharp_dir):
                print(f"❌ C# directory not found: {csharp_dir}")
                return False
            
            # Check .NET SDK
            try:
                subprocess.run(["dotnet", "--version"], capture_output=True, check=True)
            except:
                print("❌ .NET SDK not found. Install from: https://dotnet.microsoft.com/download")
                return False
            
            # Start C# API
            self.csharp_process = subprocess.Popen(
                ["dotnet", "run", "--configuration", "Release"],
                cwd=csharp_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            print(f"   Process ID: {self.csharp_process.pid}")
            print(f"   Port: {self.csharp_port}")
            
            # Wait for startup
            for attempt in range(30):
                try:
                    response = requests.get(f"http://localhost:{self.csharp_port}/health", timeout=2)
                    if response.status_code == 200:
                        result = response.json()
                        print(f"✅ C# API ready: {result.get('Message', 'OK')}")
                        return True
                except:
                    pass
                
                time.sleep(1)
                if attempt % 5 == 0:
                    print(f"   Waiting for C# API... ({attempt + 1}/30)")
            
            print("❌ C# API failed to start within timeout")
            return False
            
        except Exception as e:
            print(f"❌ Failed to start C# API: {str(e)}")
            return False
    
    def monitor_apis(self):
        """Monitor API health in background"""
        while self.running:
            try:
                time.sleep(30)  # Check every 30 seconds
                
                if not self.running:
                    break
                
                # Check Python API
                python_ok = False
                try:
                    response = requests.get(f"http://localhost:{self.python_port}/health", timeout=3)
                    python_ok = response.status_code == 200
                except:
                    pass
                
                # Check C# API
                csharp_ok = False
                try:
                    response = requests.get(f"http://localhost:{self.csharp_port}/health", timeout=3)
                    csharp_ok = response.status_code == 200
                except:
                    pass
                
                # Status update
                timestamp = datetime.now().strftime("%H:%M:%S")
                python_status = "🟢" if python_ok else "🔴"
                csharp_status = "🟢" if csharp_ok else "🔴"
                
                print(f"[{timestamp}] Status: Python {python_status} | C# {csharp_status}")
                
                # Alert if APIs are down
                if not python_ok and self.python_process:
                    print("⚠️ Python API appears to be down!")
                
                if not csharp_ok and self.csharp_process:
                    print("⚠️ C# API appears to be down!")
                    
            except Exception as e:
                if self.running:
                    print(f"Monitor error: {str(e)}")
    
    def run_quick_test(self):
        """Run quick test of both APIs"""
        print("\n🧪 Running quick functionality test...")
        
        # Test Python API
        try:
            response = requests.get(f"http://localhost:{self.python_port}/blueprint/projects", timeout=10)
            if response.status_code == 200:
                projects = response.json()
                project_count = len(projects.get('projects', []))
                print(f"✅ Python API: {project_count} projects found")
            else:
                print(f"❌ Python API projects test failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Python API test error: {str(e)}")
        
        # Test C# API
        try:
            response = requests.get(f"http://localhost:{self.csharp_port}/blueprint/projects", timeout=10)
            if response.status_code == 200:
                projects = response.json()
                project_count = len(projects.get('Projects', []))
                print(f"✅ C# API: {project_count} projects found")
            else:
                print(f"❌ C# API projects test failed: {response.status_code}")
        except Exception as e:
            print(f"❌ C# API test error: {str(e)}")
    
    def show_status(self):
        """Show current status and usage information"""
        self.print_header("DUAL API STATUS")
        
        print(f"🐍 Python API:")
        print(f"   URL: http://localhost:{self.python_port}")
        print(f"   Health: http://localhost:{self.python_port}/health")
        print(f"   Projects: http://localhost:{self.python_port}/blueprint/projects")
        print(f"   Process: {'Running' if self.python_process else 'Not Started'}")
        
        print(f"\n🔷 C# API:")
        print(f"   URL: http://localhost:{self.csharp_port}")
        print(f"   Health: http://localhost:{self.csharp_port}/health")
        print(f"   Projects: http://localhost:{self.csharp_port}/blueprint/projects")
        print(f"   Process: {'Running' if self.csharp_process else 'Not Started'}")
        
        print(f"\n📋 Available Commands:")
        print(f"   Quick Test: python3 quick_dual_api_test.py")
        print(f"   Full Test: python3 production_readiness_test.py")
        print(f"   Stop APIs: Ctrl+C")
        
        print(f"\n🎯 BDA Project: test-w2-fixed-1765841521")
        print(f"   Both APIs use the same BDA project for processing")
    
    def cleanup(self):
        """Clean up processes"""
        print("\n🧹 Shutting down APIs...")
        self.running = False
        
        if self.python_process:
            try:
                self.python_process.terminate()
                self.python_process.wait(timeout=5)
                print("✅ Python API stopped")
            except:
                self.python_process.kill()
                print("🔨 Python API force stopped")
        
        if self.csharp_process:
            try:
                self.csharp_process.terminate()
                self.csharp_process.wait(timeout=5)
                print("✅ C# API stopped")
            except:
                self.csharp_process.kill()
                print("🔨 C# API force stopped")
    
    def start_both_apis(self):
        """Start both APIs and manage them"""
        self.print_header("DUAL BDA API MANAGER")
        print("Starting both Python and C# BDA APIs for development and testing")
        
        # Start APIs concurrently
        python_thread = threading.Thread(target=self.start_python_api)
        csharp_thread = threading.Thread(target=self.start_csharp_api)
        
        python_thread.start()
        csharp_thread.start()
        
        # Wait for both to complete startup
        python_thread.join()
        csharp_thread.join()
        
        # Check if both started successfully
        python_ok = self.python_process is not None
        csharp_ok = self.csharp_process is not None
        
        if not python_ok and not csharp_ok:
            print("\n❌ Both APIs failed to start!")
            return False
        elif not python_ok:
            print("\n⚠️ Only C# API started successfully")
        elif not csharp_ok:
            print("\n⚠️ Only Python API started successfully")
        else:
            print("\n🎉 Both APIs started successfully!")
        
        # Run quick test
        if python_ok or csharp_ok:
            self.run_quick_test()
        
        # Show status
        self.show_status()
        
        # Start monitoring in background
        monitor_thread = threading.Thread(target=self.monitor_apis, daemon=True)
        monitor_thread.start()
        
        return True

def main():
    """Main function"""
    manager = DualAPIManager()
    
    def signal_handler(sig, frame):
        print("\n🛑 Received shutdown signal...")
        manager.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        success = manager.start_both_apis()
        
        if success:
            print("\n⏳ APIs are running. Press Ctrl+C to stop...")
            print("💡 Run 'python3 quick_dual_api_test.py' in another terminal to test")
            
            # Keep running
            while True:
                time.sleep(1)
        else:
            print("\n❌ Failed to start APIs")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
    finally:
        manager.cleanup()

if __name__ == "__main__":
    main()