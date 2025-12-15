#!/usr/bin/env python3
"""
BDA Port Cleanup Utility
Stops all processes running on BDA system ports
"""

import subprocess
import os
import signal
import time
import sys

def cleanup_port(port):
    """Kill any process using the specified port"""
    try:
        # Find process using the port
        result = subprocess.run(['lsof', '-ti', f':{port}'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid.strip():
                    try:
                        print(f"🔄 Stopping process {pid} on port {port}...")
                        os.kill(int(pid), signal.SIGTERM)
                        time.sleep(1)
                        # Force kill if still running
                        try:
                            os.kill(int(pid), signal.SIGKILL)
                        except ProcessLookupError:
                            pass  # Process already terminated
                        print(f"✅ Stopped process {pid} on port {port}")
                        return True
                    except (ProcessLookupError, ValueError):
                        pass  # Process already gone or invalid PID
        else:
            print(f"ℹ️  No process found on port {port}")
            return False
                        
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"⚠️  Could not check port {port} (lsof not available)")
        return False

def main():
    """Clean up all BDA system ports"""
    # All ports used by the BDA system
    bda_ports = [
        8000,  # python_blueprint_api
        8001,  # python_textract
        8002,  # python_analyze_document
        5000,  # csharp_blueprint_api
        5001,  # csharp_textract
        5002,  # csharp_analyze_document
        8080   # documentation_portal
    ]
    
    print("🧹 BDA Port Cleanup Utility")
    print("=" * 50)
    
    stopped_count = 0
    for port in bda_ports:
        if cleanup_port(port):
            stopped_count += 1
    
    print("=" * 50)
    if stopped_count > 0:
        print(f"✅ Cleanup complete! Stopped {stopped_count} processes.")
    else:
        print("✅ All BDA ports are already free!")

if __name__ == "__main__":
    main()