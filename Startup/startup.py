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
    """Kill any process using the specified port - improved version"""
    print(f"🔍 Checking port {port}...")
    
    try:
        # Find process using the port
        result = subprocess.run(['lsof', '-ti', f':{port}'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid_str in pids:
                pid_str = pid_str.strip()
                if pid_str and pid_str.isdigit():
                    pid = int(pid_str)
                    try:
                        # Check if process exists before trying to kill it
                        os.kill(pid, 0)  # This doesn't kill, just checks if process exists
                        
                        print(f"🔄 Found process {pid} on port {port}, stopping...")
                        
                        # Try graceful termination first
                        os.kill(pid, signal.SIGTERM)
                        
                        # Wait up to 3 seconds for graceful shutdown
                        for i in range(3):
                            time.sleep(1)
                            try:
                                os.kill(pid, 0)  # Check if still exists
                            except ProcessLookupError:
                                print(f"✅ Process {pid} terminated gracefully")
                                break
                        else:
                            # Force kill if still running after 3 seconds
                            try:
                                print(f"⚡ Force killing process {pid}...")
                                os.kill(pid, signal.SIGKILL)
                                time.sleep(0.5)
                                print(f"✅ Process {pid} force killed")
                            except ProcessLookupError:
                                print(f"✅ Process {pid} already terminated")
                                
                    except ProcessLookupError:
                        # Process already gone
                        print(f"ℹ️ Process {pid} already terminated")
                    except PermissionError:
                        print(f"❌ Permission denied to kill process {pid} on port {port}")
                        print(f"💡 You may need to run: sudo kill -9 {pid}")
                    except (ValueError, OSError) as e:
                        print(f"❌ Error killing process {pid}: {e}")
        else:
            print(f"✅ Port {port} is free")
                        
    except subprocess.TimeoutExpired:
        print(f"⚠️ Timeout checking port {port} - lsof command took too long")
    except (subprocess.CalledProcessError, FileNotFoundError):
        # lsof not available or other error
        print(f"⚠️ Could not check port {port} (lsof not available or error)")
        # Try alternative method using netstat if available
        try:
            result = subprocess.run(['netstat', '-tulpn'], 
                                  capture_output=True, text=True, timeout=5)
            if f":{port} " in result.stdout:
                print(f"⚠️ Port {port} appears to be in use (detected via netstat)")
            else:
                print(f"✅ Port {port} appears to be free (checked via netstat)")
        except:
            print(f"⚠️ Could not verify port {port} status")
    except Exception as e:
        print(f"❌ Unexpected error checking port {port}: {e}")

def kill_specific_pid(pid):
    """Kill a specific process by PID"""
    try:
        pid = int(pid)
        print(f"🎯 Killing specific process {pid}...")
        
        # Check if process exists
        os.kill(pid, 0)
        
        # Try graceful termination
        os.kill(pid, signal.SIGTERM)
        time.sleep(2)
        
        # Check if still running
        try:
            os.kill(pid, 0)
            # Still running, force kill
            print(f"⚡ Force killing process {pid}...")
            os.kill(pid, signal.SIGKILL)
            time.sleep(0.5)
        except ProcessLookupError:
            pass  # Already terminated
            
        print(f"✅ Process {pid} terminated")
        return True
        
    except ProcessLookupError:
        print(f"ℹ️ Process {pid} not found (already terminated)")
        return True
    except PermissionError:
        print(f"❌ Permission denied to kill process {pid}")
        print(f"💡 Run manually: sudo kill -9 {pid}")
        return False
    except Exception as e:
        print(f"❌ Error killing process {pid}: {e}")
        return False

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
    print("=" * 50)
    
    success_count = 0
    for port in bda_ports:
        try:
            cleanup_port(port)
            success_count += 1
        except Exception as e:
            print(f"❌ Error cleaning port {port}: {e}")
    
    print(f"\n✅ Port cleanup complete! {success_count}/{len(bda_ports)} ports processed")
    print("=" * 50)

def main():
    """Clean up ports and launch the GUI manager"""
    print("🚀 BDA Project Manager Startup")
    print("=" * 40)
    
    startup_dir = Path(__file__).parent
    gui_script = startup_dir / "gui_manager.py"
    
    if not gui_script.exists():
        print("❌ GUI manager not found!")
        print(f"Expected location: {gui_script}")
        return
    
    try:
        # Clean up all BDA ports first
        print("Step 1: Cleaning up ports...")
        cleanup_all_bda_ports()
        
        print("\nStep 2: Starting GUI manager...")
        print("🚀 Launching BDA Project Manager GUI...")
        print("💡 The GUI window should open shortly...")
        
        # Add a small delay to ensure ports are fully cleaned up
        time.sleep(1)
        
        subprocess.run([sys.executable, str(gui_script)], cwd=startup_dir)
        
    except KeyboardInterrupt:
        print("\n👋 BDA Project Manager closed by user.")
    except Exception as e:
        print(f"❌ Error starting GUI: {e}")
        print("💡 Try running the GUI directly: python Startup/gui_manager.py")

if __name__ == "__main__":
    main()