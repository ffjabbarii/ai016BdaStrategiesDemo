#!/usr/bin/env python3
"""
BDA Project Manager - Command Line Interface
Usage: python project_manager.py <project-name> <backend-or-frontend> <start/stop> <port1> [port2] [port3]
"""

import sys
import os
import subprocess
import json
import time
import psutil
import signal
from pathlib import Path

class ProjectManager:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.processes_file = self.base_dir / "Startup" / "running_processes.json"
        self.config_file = self.base_dir / "Startup" / "project_config.json"
        self.load_config()
        
    def load_config(self):
        """Load project configuration"""
        default_config = {
            "python_blueprint_api": {
                "type": "backend",
                "language": "python",
                "path": "python/BlueprintAPI",
                "start_command": "python -m uvicorn src.api:app --host 0.0.0.0 --port 8000",
                "default_port": 8000,
                "health_endpoint": "/health"
            },
            "python_textract": {
                "type": "backend", 
                "language": "python",
                "path": "python/Textract",
                "start_command": "python src/lambda_local.py",
                "default_port": 8001,
                "health_endpoint": "/health"
            },
            "python_analyze_document": {
                "type": "backend",
                "language": "python", 
                "path": "python/AnalyzeDocument",
                "start_command": "python src/api.py",
                "default_port": 8002,
                "health_endpoint": "/health"
            },
            "csharp_blueprint_api": {
                "type": "backend",
                "language": "csharp",
                "path": "csharp/BlueprintAPI", 
                "start_command": "dotnet run",
                "default_port": 5000,
                "health_endpoint": "/api/document/health"
            },
            "csharp_textract": {
                "type": "backend",
                "language": "csharp",
                "path": "csharp/Textract",
                "start_command": "dotnet run",
                "default_port": 5001,
                "health_endpoint": "/health"
            },
            "csharp_analyze_document": {
                "type": "backend",
                "language": "csharp",
                "path": "csharp/AnalyzeDocument",
                "start_command": "dotnet run", 
                "default_port": 5002,
                "health_endpoint": "/api/document/health"
            },
            "documentation_portal": {
                "type": "frontend",
                "language": "html",
                "path": "Docs",
                "start_command": "python -m http.server",
                "default_port": 8080,
                "health_endpoint": "/index.html"
            }
        }
        
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """Save project configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def load_processes(self):
        """Load running processes from file"""
        if self.processes_file.exists():
            with open(self.processes_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_processes(self, processes):
        """Save running processes to file"""
        with open(self.processes_file, 'w') as f:
            json.dump(processes, f, indent=2)
    
    def cleanup_port(self, port):
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
                            print(f"✅ Stopped process {pid}")
                        except (ProcessLookupError, ValueError):
                            pass  # Process already gone or invalid PID
                            
        except (subprocess.CalledProcessError, FileNotFoundError):
            # lsof not available or other error, continue anyway
            pass
    
    def start_project(self, project_name, component_type, ports):
        """Start a project component"""
        if project_name not in self.config:
            print(f"❌ Project '{project_name}' not found in configuration")
            return False
        
        project_config = self.config[project_name]
        
        if project_config["type"] != component_type:
            print(f"❌ Project '{project_name}' is not a {component_type}")
            return False
        
        port = ports[0] if ports else project_config["default_port"]
        project_path = self.base_dir / project_config["path"]
        
        if not project_path.exists():
            print(f"❌ Project path does not exist: {project_path}")
            return False
        
        # Clean up any existing process on the target port
        self.cleanup_port(port)
        
        # Check if already running
        processes = self.load_processes()
        process_key = f"{project_name}_{port}"
        
        if process_key in processes:
            pid = processes[process_key]["pid"]
            if psutil.pid_exists(pid):
                print(f"⚠️  Project '{project_name}' is already running on port {port}")
                return False
            else:
                # Clean up stale process entry
                del processes[process_key]
                self.save_processes(processes)
        
        # Prepare environment
        env = os.environ.copy()
        if project_config["language"] == "python":
            env["PORT"] = str(port)
            env["PYTHONPATH"] = str(self.base_dir)
        elif project_config["language"] == "csharp":
            env["ASPNETCORE_URLS"] = f"http://localhost:{port}"
        
        # Install dependencies first if needed
        if project_config["language"] == "python":
            requirements_file = project_path / "requirements.txt"
            if requirements_file.exists():
                print(f"📦 Installing dependencies for {project_name}...")
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)], 
                                 check=True, capture_output=True, text=True)
                    print(f"✅ Dependencies installed for {project_name}")
                except subprocess.CalledProcessError as e:
                    print(f"⚠️  Warning: Could not install dependencies: {e.stderr}")
        
        # Start the process
        try:
            print(f"🚀 Starting {project_name} on port {port}...")
            
            if project_config["language"] == "html":
                # Special handling for static HTML server
                process = subprocess.Popen(
                    [sys.executable, "-m", "http.server", str(port)],
                    cwd=project_path,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            else:
                # Regular project startup
                cmd = project_config["start_command"].split()
                process = subprocess.Popen(
                    cmd,
                    cwd=project_path,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            
            # Wait a moment for startup
            time.sleep(2)
            
            # Check if process is still running
            if process.poll() is None:
                # Save process info
                processes[process_key] = {
                    "pid": process.pid,
                    "project_name": project_name,
                    "port": port,
                    "type": component_type,
                    "language": project_config["language"],
                    "health_endpoint": project_config["health_endpoint"],
                    "started_at": time.time()
                }
                self.save_processes(processes)
                print(f"✅ {project_name} started successfully on port {port}")
                print(f"🌐 Access at: http://localhost:{port}")
                return True
            else:
                # Process failed to start, get error output
                stdout, stderr = process.communicate()
                error_output = stderr.decode() if stderr else stdout.decode()
                print(f"❌ Failed to start {project_name}")
                if error_output:
                    print(f"Error: {error_output}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting {project_name}: {str(e)}")
            return False
    
    def stop_project(self, project_name, component_type, ports):
        """Stop a project component"""
        processes = self.load_processes()
        port = ports[0] if ports else None
        
        # Find matching processes
        to_remove = []
        for process_key, process_info in processes.items():
            if process_info["project_name"] == project_name:
                if port is None or process_info["port"] == port:
                    if process_info["type"] == component_type:
                        to_remove.append((process_key, process_info))
        
        if not to_remove:
            print(f"❌ No running {component_type} found for project '{project_name}'")
            return False
        
        success = True
        for process_key, process_info in to_remove:
            try:
                pid = process_info["pid"]
                if psutil.pid_exists(pid):
                    # Try graceful shutdown first
                    os.kill(pid, signal.SIGTERM)
                    time.sleep(2)
                    
                    # Force kill if still running
                    if psutil.pid_exists(pid):
                        os.kill(pid, signal.SIGKILL)
                        time.sleep(1)
                
                del processes[process_key]
                print(f"🛑 Stopped {project_name} on port {process_info['port']}")
                
            except Exception as e:
                print(f"❌ Error stopping {project_name}: {str(e)}")
                success = False
        
        self.save_processes(processes)
        return success
    
    def list_projects(self):
        """List all available projects"""
        print("\n📋 Available Projects:")
        print("=" * 50)
        
        for project_name, config in self.config.items():
            print(f"🔹 {project_name}")
            print(f"   Type: {config['type']}")
            print(f"   Language: {config['language']}")
            print(f"   Default Port: {config['default_port']}")
            print(f"   Path: {config['path']}")
            print()
    
    def status(self):
        """Show status of all projects"""
        processes = self.load_processes()
        
        print("\n📊 Project Status:")
        print("=" * 50)
        
        if not processes:
            print("No projects currently running.")
            return
        
        for process_key, process_info in processes.items():
            pid = process_info["pid"]
            status = "🟢 Running" if psutil.pid_exists(pid) else "🔴 Stopped"
            
            print(f"{status} {process_info['project_name']}")
            print(f"   Port: {process_info['port']}")
            print(f"   Type: {process_info['type']}")
            print(f"   PID: {pid}")
            print(f"   URL: http://localhost:{process_info['port']}")
            print()

def main():
    if len(sys.argv) < 4:
        print("Usage: python project_manager.py <project-name> <backend-or-frontend> <start/stop> <port1> [port2] [port3]")
        print("\nExamples:")
        print("  python project_manager.py python_blueprint_api backend start 8000")
        print("  python project_manager.py csharp_analyze_document backend stop 5002")
        print("  python project_manager.py documentation_portal frontend start 8080")
        print("\nSpecial commands:")
        print("  python project_manager.py list")
        print("  python project_manager.py status")
        return
    
    manager = ProjectManager()
    
    # Handle special commands
    if sys.argv[1] == "list":
        manager.list_projects()
        return
    elif sys.argv[1] == "status":
        manager.status()
        return
    
    project_name = sys.argv[1]
    component_type = sys.argv[2]  # backend or frontend
    action = sys.argv[3]  # start or stop
    ports = [int(p) for p in sys.argv[4:]] if len(sys.argv) > 4 else []
    
    if action == "start":
        manager.start_project(project_name, component_type, ports)
    elif action == "stop":
        manager.stop_project(project_name, component_type, ports)
    else:
        print(f"❌ Unknown action: {action}. Use 'start' or 'stop'")

if __name__ == "__main__":
    main()