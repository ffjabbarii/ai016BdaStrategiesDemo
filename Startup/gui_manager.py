#!/usr/bin/env python3
"""
BDA Project Manager - GUI Application
A visual interface to start, stop, and monitor all BDA projects
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import webbrowser
import requests
from project_manager import ProjectManager
import json
from pathlib import Path

class BDAProjectGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("BDA Project Manager")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")
        
        # Initialize project manager
        self.manager = ProjectManager()
        
        # Create main layout
        self.create_widgets()
        
        # Start status update thread
        self.running = True
        self.update_thread = threading.Thread(target=self.update_status_loop, daemon=True)
        self.update_thread.start()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """Create the main GUI layout"""
        # Title
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        title_frame.pack(fill="x", padx=0, pady=0)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, 
            text="🚀 BDA Project Manager", 
            font=("Arial", 24, "bold"),
            fg="white", 
            bg="#2c3e50"
        )
        title_label.pack(expand=True)
        
        # Main content frame
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Left panel - Available Projects
        left_frame = tk.LabelFrame(
            main_frame, 
            text="📋 Available Projects", 
            font=("Arial", 14, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Projects list with scrollbar
        projects_frame = tk.Frame(left_frame, bg="#f0f0f0")
        projects_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Scrollable frame for projects
        canvas = tk.Canvas(projects_frame, bg="white")
        scrollbar = ttk.Scrollbar(projects_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg="white")
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Right panel - Running Projects
        right_frame = tk.LabelFrame(
            main_frame, 
            text="🟢 Running Projects", 
            font=("Arial", 14, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Running projects list
        self.running_frame = tk.Frame(right_frame, bg="#f0f0f0")
        self.running_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Control buttons frame
        control_frame = tk.Frame(self.root, bg="#f0f0f0")
        control_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Refresh button
        refresh_btn = tk.Button(
            control_frame,
            text="🔄 Refresh Status",
            font=("Arial", 12, "bold"),
            bg="#3498db",
            fg="white",
            command=self.refresh_status,
            padx=20,
            pady=10
        )
        refresh_btn.pack(side="left", padx=(0, 10))
        
        # Stop all button
        stop_all_btn = tk.Button(
            control_frame,
            text="🛑 Stop All Projects",
            font=("Arial", 12, "bold"),
            bg="#e74c3c",
            fg="white",
            command=self.stop_all_projects,
            padx=20,
            pady=10
        )
        stop_all_btn.pack(side="left", padx=(0, 10))
        
        # Open docs button
        docs_btn = tk.Button(
            control_frame,
            text="📚 Open Documentation",
            font=("Arial", 12, "bold"),
            bg="#9b59b6",
            fg="white",
            command=self.open_documentation,
            padx=20,
            pady=10
        )
        docs_btn.pack(side="right")
        
        # Initial load
        self.load_available_projects()
        self.update_running_projects()
        
        # Show beginner's guide
        self.show_beginner_guide()
    
    def load_available_projects(self):
        """Load and display available projects"""
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        for project_name, config in self.manager.config.items():
            self.create_project_card(project_name, config)
    
    def create_project_card(self, project_name, config):
        """Create a project card widget"""
        # Main card frame
        card_frame = tk.Frame(
            self.scrollable_frame, 
            bg="white", 
            relief="raised", 
            bd=2
        )
        card_frame.pack(fill="x", padx=5, pady=5)
        
        # Project info frame
        info_frame = tk.Frame(card_frame, bg="white")
        info_frame.pack(fill="x", padx=10, pady=10)
        
        # Project name with clear description
        display_name = {
            "python_blueprint_api": "🐍 Python W-2 Processor (Blueprint API)",
            "python_textract": "🐍 Python Document Scanner (Textract)",
            "python_analyze_document": "🐍 Python Advanced Analyzer",
            "csharp_blueprint_api": "🔷 C# W-2 Processor (Blueprint API)",
            "csharp_textract": "🔷 C# Document Scanner (Textract)",
            "csharp_analyze_document": "🔷 C# Advanced Analyzer",
            "documentation_portal": "📚 Documentation Website"
        }.get(project_name, project_name.replace("_", " ").title())
        
        name_label = tk.Label(
            info_frame,
            text=display_name,
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#2c3e50"
        )
        name_label.pack(anchor="w")
        
        # What this does
        purpose = {
            "python_blueprint_api": "📄 Processes W-2 forms and extracts tax information",
            "python_textract": "🔍 Scans documents and converts to text",
            "python_analyze_document": "🧠 Advanced document analysis with AI",
            "csharp_blueprint_api": "📄 Same as Python version but in C#",
            "csharp_textract": "🔍 Same as Python version but in C#",
            "csharp_analyze_document": "🧠 Same as Python version but in C#",
            "documentation_portal": "📖 Opens project documentation in browser"
        }.get(project_name, "Document processing service")
        
        purpose_label = tk.Label(
            info_frame,
            text=purpose,
            font=("Arial", 10),
            bg="white",
            fg="#2980b9",
            wraplength=300
        )
        purpose_label.pack(anchor="w", pady=(2, 5))
        
        # Technical details (smaller)
        details = f"Language: {config['language']} | Default Port: {config['default_port']}"
        details_label = tk.Label(
            info_frame,
            text=details,
            font=("Arial", 8),
            bg="white",
            fg="#7f8c8d"
        )
        details_label.pack(anchor="w")
        
        # Buttons frame
        buttons_frame = tk.Frame(card_frame, bg="white")
        buttons_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Start button with clear text
        start_text = {
            "python_blueprint_api": "▶️ Start W-2 Processor",
            "python_textract": "▶️ Start Document Scanner", 
            "python_analyze_document": "▶️ Start Advanced Analyzer",
            "csharp_blueprint_api": "▶️ Start C# W-2 Processor",
            "csharp_textract": "▶️ Start C# Scanner",
            "csharp_analyze_document": "▶️ Start C# Analyzer",
            "documentation_portal": "▶️ Open Documentation"
        }.get(project_name, "▶️ Start Service")
        
        start_btn = tk.Button(
            buttons_frame,
            text=start_text,
            font=("Arial", 10, "bold"),
            bg="#27ae60",
            fg="white",
            command=lambda: self.start_project(project_name, config),
            padx=15,
            pady=5
        )
        start_btn.pack(side="left", padx=(0, 5))
        
        # Custom port entry
        port_frame = tk.Frame(buttons_frame, bg="white")
        port_frame.pack(side="left", padx=(5, 0))
        
        tk.Label(port_frame, text="Port:", bg="white", font=("Arial", 9)).pack(side="left")
        
        port_var = tk.StringVar(value=str(config['default_port']))
        port_entry = tk.Entry(port_frame, textvariable=port_var, width=6, font=("Arial", 9))
        port_entry.pack(side="left", padx=(5, 0))
        
        # Store port variable for access
        setattr(card_frame, 'port_var', port_var)
        setattr(card_frame, 'project_name', project_name)
    
    def update_running_projects(self):
        """Update the running projects panel"""
        # Clear existing widgets
        for widget in self.running_frame.winfo_children():
            widget.destroy()
        
        processes = self.manager.load_processes()
        
        if not processes:
            no_projects_label = tk.Label(
                self.running_frame,
                text="No projects currently running",
                font=("Arial", 12),
                bg="#f0f0f0",
                fg="#7f8c8d"
            )
            no_projects_label.pack(expand=True)
            return
        
        for process_key, process_info in processes.items():
            self.create_running_project_card(process_key, process_info)
    
    def create_running_project_card(self, process_key, process_info):
        """Create a running project card"""
        # Check if process is actually running
        import psutil
        is_running = psutil.pid_exists(process_info['pid'])
        
        # Main card frame
        card_frame = tk.Frame(
            self.running_frame,
            bg="#e8f5e8" if is_running else "#f5e8e8",
            relief="raised",
            bd=2
        )
        card_frame.pack(fill="x", padx=5, pady=5)
        
        # Project info
        info_frame = tk.Frame(card_frame, bg=card_frame['bg'])
        info_frame.pack(fill="x", padx=10, pady=10)
        
        # Status and name
        status_icon = "🟢" if is_running else "🔴"
        name_label = tk.Label(
            info_frame,
            text=f"{status_icon} {process_info['project_name'].replace('_', ' ').title()}",
            font=("Arial", 12, "bold"),
            bg=card_frame['bg'],
            fg="#2c3e50"
        )
        name_label.pack(anchor="w")
        
        # Details
        details = f"Port: {process_info['port']} | PID: {process_info['pid']} | Type: {process_info['type']}"
        details_label = tk.Label(
            info_frame,
            text=details,
            font=("Arial", 9),
            bg=card_frame['bg'],
            fg="#7f8c8d"
        )
        details_label.pack(anchor="w")
        
        # URL
        url = f"http://localhost:{process_info['port']}"
        url_label = tk.Label(
            info_frame,
            text=url,
            font=("Arial", 9, "underline"),
            bg=card_frame['bg'],
            fg="#3498db",
            cursor="hand2"
        )
        url_label.pack(anchor="w")
        url_label.bind("<Button-1>", lambda e: webbrowser.open(url))
        
        # Buttons frame
        buttons_frame = tk.Frame(card_frame, bg=card_frame['bg'])
        buttons_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Open button
        open_btn = tk.Button(
            buttons_frame,
            text="🌐 Open",
            font=("Arial", 10, "bold"),
            bg="#3498db",
            fg="white",
            command=lambda: webbrowser.open(url),
            padx=15,
            pady=5
        )
        open_btn.pack(side="left", padx=(0, 5))
        
        # Stop button
        stop_btn = tk.Button(
            buttons_frame,
            text="⏹️ Stop",
            font=("Arial", 10, "bold"),
            bg="#e74c3c",
            fg="white",
            command=lambda: self.stop_project(process_info['project_name'], process_info['type'], process_info['port']),
            padx=15,
            pady=5
        )
        stop_btn.pack(side="left", padx=(0, 5))
        
        # Health check button
        health_btn = tk.Button(
            buttons_frame,
            text="❤️ Health",
            font=("Arial", 10, "bold"),
            bg="#f39c12",
            fg="white",
            command=lambda: self.check_health(url + process_info['health_endpoint']),
            padx=15,
            pady=5
        )
        health_btn.pack(side="left")
    
    def start_project(self, project_name, config):
        """Start a project"""
        # Find the port from the card
        port = None
        for widget in self.scrollable_frame.winfo_children():
            if hasattr(widget, 'project_name') and widget.project_name == project_name:
                port = int(widget.port_var.get())
                break
        
        if port is None:
            port = config['default_port']
        
        # Start in background thread
        def start_thread():
            success = self.manager.start_project(project_name, config['type'], [port])
            if success:
                self.root.after(1000, self.update_running_projects)  # Update UI after 1 second
            else:
                messagebox.showerror("Error", f"Failed to start {project_name}")
        
        threading.Thread(target=start_thread, daemon=True).start()
        messagebox.showinfo("Starting", f"Starting {project_name} on port {port}...")
    
    def stop_project(self, project_name, component_type, port):
        """Stop a project"""
        def stop_thread():
            success = self.manager.stop_project(project_name, component_type, [port])
            if success:
                self.root.after(500, self.update_running_projects)  # Update UI after 0.5 seconds
            else:
                messagebox.showerror("Error", f"Failed to stop {project_name}")
        
        threading.Thread(target=stop_thread, daemon=True).start()
        messagebox.showinfo("Stopping", f"Stopping {project_name}...")
    
    def stop_all_projects(self):
        """Stop all running projects"""
        if messagebox.askyesno("Confirm", "Are you sure you want to stop all running projects?"):
            def stop_all_thread():
                processes = self.manager.load_processes()
                for process_key, process_info in processes.items():
                    self.manager.stop_project(
                        process_info['project_name'], 
                        process_info['type'], 
                        [process_info['port']]
                    )
                self.root.after(1000, self.update_running_projects)
            
            threading.Thread(target=stop_all_thread, daemon=True).start()
            messagebox.showinfo("Stopping", "Stopping all projects...")
    
    def check_health(self, health_url):
        """Check health of a service"""
        def health_thread():
            try:
                response = requests.get(health_url, timeout=5)
                if response.status_code == 200:
                    messagebox.showinfo("Health Check", "✅ Service is healthy!")
                else:
                    messagebox.showwarning("Health Check", f"⚠️ Service returned status: {response.status_code}")
            except Exception as e:
                messagebox.showerror("Health Check", f"❌ Health check failed: {str(e)}")
        
        threading.Thread(target=health_thread, daemon=True).start()
    
    def refresh_status(self):
        """Refresh the status of all projects"""
        self.update_running_projects()
        messagebox.showinfo("Refresh", "Status refreshed!")
    
    def open_documentation(self):
        """Open the documentation portal"""
        # Check if docs are running, if not start them
        processes = self.manager.load_processes()
        docs_running = False
        docs_port = 8080
        
        for process_info in processes.values():
            if process_info['project_name'] == 'documentation_portal':
                docs_running = True
                docs_port = process_info['port']
                break
        
        if not docs_running:
            # Start documentation server
            success = self.manager.start_project('documentation_portal', 'frontend', [8080])
            if success:
                time.sleep(2)  # Wait for startup
                webbrowser.open("http://localhost:8080")
                self.update_running_projects()
            else:
                messagebox.showerror("Error", "Failed to start documentation server")
        else:
            webbrowser.open(f"http://localhost:{docs_port}")
    
    def update_status_loop(self):
        """Background thread to update status periodically"""
        while self.running:
            time.sleep(10)  # Update every 10 seconds
            if self.running:
                self.root.after(0, self.update_running_projects)
    
    def show_beginner_guide(self):
        """Show the beginner's guide window"""
        try:
            from beginner_guide import show_guide
            show_guide(self.root)
        except ImportError:
            # Fallback if guide module not available
            messagebox.showinfo(
                "Welcome to BDA Project Manager", 
                "🎯 Quick Start:\n\n"
                "1. Click 'Start W-2 Processor' for Python or C#\n"
                "2. Wait for green dot 🟢 on the right\n"
                "3. Click the blue link to open in browser\n"
                "4. Test with /docs endpoint\n"
                "5. Upload test_files/sample_w2.txt\n\n"
                "Need help? Look for the sample file in test_files folder!"
            )
    
    def on_closing(self):
        """Handle window closing"""
        self.running = False
        self.root.destroy()

def main():
    root = tk.Tk()
    app = BDAProjectGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()