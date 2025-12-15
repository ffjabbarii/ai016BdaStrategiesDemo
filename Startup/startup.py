#!/usr/bin/env python3
"""
Quick startup script - cleans up ports and launches the GUI manager
"""

import sys
import subprocess
import os
import signal
import time
from pathlib import Path

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
                        print(f"🔄 Stopping existing process {pid} on port {port}...")
                        os.kill(int(pid), signal.SIGTERM)
                        time.sleep(1)
                        # Force kill if still running
                        try:
                            os.kill(int(pid), signal.SIGKILL)
                        except ProcessLookupError:
                            pass  # Process already terminated
                        print(f"✅ Stopped process {pid} on port {port}")
                    except (ProcessLookupError, ValueError):
                        pass  # Process already gone or invalid PID
                        
    except (subprocess.CalledProcessError, FileNotFoundError):
        # lsof not available or other error, continue anyway
        pass

def cleanup_all_bda_ports():
    """Clean up all ports used by BDA system"""
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
    
    print("🧹 Cleaning up BDA system ports...")
    for port in bda_ports:
        cleanup_port(port)
    
    print("✅ Port cleanup complete!")

def main():
    """Clean up ports and launch the GUI manager"""
    startup_dir = Path(__file__).parent
    gui_script = startup_dir / "gui_manager.py"
    
    if not gui_script.exists():
        print("❌ GUI manager not found!")
        return
    
    try:
        # Clean up all BDA ports first
        cleanup_all_bda_ports()
        
        print("🚀 Starting BDA Project Manager GUI...")
        subprocess.run([sys.executable, str(gui_script)], cwd=startup_dir)
    except KeyboardInterrupt:
        print("\n👋 BDA Project Manager closed.")
    except Exception as e:
        print(f"❌ Error starting GUI: {e}")

if __name__ == "__main__":
    main()