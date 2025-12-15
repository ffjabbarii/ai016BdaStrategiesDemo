# BDA Project Startup Manager

This directory contains tools to easily start, stop, and manage all BDA projects from a single interface.

## 🚀 Quick Start

### GUI Manager (Recommended)
```bash
cd Startup
pip install -r requirements.txt
python gui_manager.py
```

### Command Line Manager
```bash
cd Startup
python project_manager.py <project-name> <backend-or-frontend> <start/stop> <port>
```

## 📋 Available Projects

| Project Name | Type | Language | Default Port | Description |
|--------------|------|----------|--------------|-------------|
| `python_blueprint_api` | backend | python | 8000 | FastAPI + Blueprint API |
| `python_textract` | backend | python | 8001 | Lambda simulation server |
| `python_analyze_document` | backend | python | 8002 | Enhanced Textract processing |
| `csharp_blueprint_api` | backend | csharp | 5000 | ASP.NET Core + Blueprint API |
| `csharp_textract` | backend | csharp | 5001 | .NET Lambda function |
| `csharp_analyze_document` | backend | csharp | 5002 | Advanced .NET processing |
| `documentation_portal` | frontend | html | 8080 | Static documentation site |

## 🎯 GUI Features

- **Visual Project Cards**: See all available projects with details
- **One-Click Start/Stop**: Easy project management
- **Running Status**: Real-time status of all projects
- **Clickable Links**: Direct access to running services
- **Health Checks**: Verify service health
- **Custom Ports**: Override default ports as needed
- **Auto-Documentation**: Automatically start docs when needed

## 💻 Command Line Examples

```bash
# List all available projects
python project_manager.py list

# Show status of running projects
python project_manager.py status

# Start Python Blueprint API on default port (8000)
python project_manager.py python_blueprint_api backend start

# Start C# Analyze Document on custom port
python project_manager.py csharp_analyze_document backend start 5555

# Stop a specific project
python project_manager.py python_blueprint_api backend stop 8000

# Start documentation portal
python project_manager.py documentation_portal frontend start 8080
```

## 🔧 Configuration

Projects are configured in `project_config.json`. Each project has:

- **type**: `backend` or `frontend`
- **language**: `python`, `csharp`, or `html`
- **path**: Relative path from project root
- **start_command**: Command to start the project
- **default_port**: Default port number
- **health_endpoint**: Health check URL path

## 📊 Process Management

- Running processes are tracked in `running_processes.json`
- Process IDs (PIDs) are monitored for actual status
- Graceful shutdown with SIGTERM, force kill with SIGKILL if needed
- Automatic cleanup of stale process entries

## 🌐 Service URLs

When projects are running, access them at:

- **Python Blueprint API**: http://localhost:8000
- **Python Textract**: http://localhost:8001  
- **Python Analyze Document**: http://localhost:8002
- **C# Blueprint API**: http://localhost:5000
- **C# Textract**: http://localhost:5001
- **C# Analyze Document**: http://localhost:5002
- **Documentation Portal**: http://localhost:8080

## 🛠️ Development Workflow

1. **Start GUI Manager**: `python gui_manager.py`
2. **Select Projects**: Click start on needed projects
3. **Develop**: Use VS Code/Visual Studio for development
4. **Test**: Click service links to test functionality
5. **Monitor**: Watch status in real-time
6. **Stop**: Clean shutdown when done

## 🔍 Troubleshooting

### Port Already in Use
- Check running projects in GUI
- Use custom port numbers
- Kill conflicting processes

### Project Won't Start
- Check project path exists
- Verify dependencies installed
- Check error messages in terminal

### Health Check Fails
- Ensure service is fully started
- Check network connectivity
- Verify health endpoint path

## 📁 File Structure

```
Startup/
├── gui_manager.py          # GUI application
├── project_manager.py      # Command line manager
├── project_config.json     # Project configurations
├── running_processes.json  # Active process tracking
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🎨 GUI Screenshots

The GUI provides:
- Left panel: Available projects with start buttons
- Right panel: Running projects with stop/open buttons  
- Status indicators: Green (running), Red (stopped)
- Control buttons: Refresh, Stop All, Open Docs
- Real-time updates every 10 seconds