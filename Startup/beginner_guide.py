#!/usr/bin/env python3
"""
Beginner's Guide Window - Shows simple instructions
"""

import tkinter as tk
from tkinter import ttk

class BeginnerGuide:
    def __init__(self, parent=None):
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("🚀 How to Use BDA Project Manager")
        self.window.geometry("800x600")
        self.window.configure(bg="#f8f9fa")
        
        # Make it stay on top initially
        self.window.lift()
        self.window.attributes('-topmost', True)
        self.window.after(2000, lambda: self.window.attributes('-topmost', False))
        
        self.create_guide()
    
    def create_guide(self):
        """Create the beginner's guide content"""
        
        # Title
        title_frame = tk.Frame(self.window, bg="#2c3e50", height=60)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="🎯 Quick Start Guide - Testing W-2 Processing",
            font=("Arial", 18, "bold"),
            fg="white",
            bg="#2c3e50"
        )
        title_label.pack(expand=True)
        
        # Main content with scrollbar
        main_frame = tk.Frame(self.window, bg="#f8f9fa")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Scrollable text
        canvas = tk.Canvas(main_frame, bg="white")
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Guide content
        self.add_guide_content(scrollable_frame)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Close button
        close_btn = tk.Button(
            self.window,
            text="✅ Got It! Let's Start Testing",
            font=("Arial", 14, "bold"),
            bg="#27ae60",
            fg="white",
            command=self.window.destroy,
            padx=30,
            pady=10
        )
        close_btn.pack(pady=20)
    
    def add_guide_content(self, parent):
        """Add the step-by-step guide content"""
        
        steps = [
            {
                "title": "🎯 What This System Does",
                "content": "This system processes W-2 tax forms and bank statements using AWS-style document analysis. You can test both Python and C# versions to see how they work."
            },
            {
                "title": "📋 Step 1: Choose What to Test",
                "content": """Pick ONE of these to start with:

🐍 Python W-2 Processor (Blueprint API)
   → Best for beginners
   → Processes W-2 forms and extracts tax info
   → Click 'Start W-2 Processor' button

🔷 C# W-2 Processor (Blueprint API)  
   → Same functionality as Python version
   → Good for comparing languages
   → Click 'Start C# W-2 Processor' button"""
            },
            {
                "title": "⚡ Step 2: Start the Service",
                "content": """1. Click the green 'Start' button for your chosen processor
2. Wait 5-10 seconds for it to start up
3. Look for it to appear on the RIGHT side with a green dot 🟢
4. You'll see a blue clickable link like 'http://localhost:8000'"""
            },
            {
                "title": "🌐 Step 3: Open in Browser",
                "content": """1. Click the blue link (or the '🌐 Open' button)
2. Your browser will open to the service
3. You should see either:
   - A Swagger API documentation page, OR
   - A JSON response with service info
4. Add '/docs' to the URL if you don't see Swagger automatically"""
            },
            {
                "title": "📄 Step 4: Test W-2 Processing",
                "content": """1. In the browser, look for 'POST /process/w2' endpoint
2. Click 'Try it out' 
3. Click 'Choose File' and select: test_files/sample_w2.txt
4. Click 'Execute'
5. You should get a JSON response with extracted W-2 data like:
   - Employee name and SSN
   - Employer information  
   - Tax amounts (wages, withholdings, etc.)"""
            },
            {
                "title": "🔍 Step 5: Understanding Results",
                "content": """A successful test shows:
✅ Status: 'success'
✅ Document type: 'w2'  
✅ Extracted data with employee info, employer info, tax info
✅ Confidence scores

If you see this, congratulations! The system is working."""
            },
            {
                "title": "🆚 Step 6: Compare Python vs C#",
                "content": """Try the same test with both versions:
1. Start both Python and C# W-2 processors
2. Test the same W-2 file on both
3. Compare the results - they should be very similar
4. Notice any differences in response format or processing speed"""
            },
            {
                "title": "🛑 Step 7: Stop Services When Done",
                "content": """1. In the main window, click the red '⏹️ Stop' button for each running service
2. OR click 'Stop All Projects' to stop everything at once
3. Services will disappear from the right panel when stopped"""
            },
            {
                "title": "🆘 If Something Goes Wrong",
                "content": """Common issues:
❌ 'Connection refused' → Wait longer for startup (10-15 seconds)
❌ 'Port already in use' → Change the port number before starting
❌ 'File not found' → Make sure test_files/sample_w2.txt exists
❌ Service won't start → Check the terminal for error messages"""
            }
        ]
        
        for i, step in enumerate(steps):
            # Step frame
            step_frame = tk.Frame(parent, bg="white", relief="raised", bd=1)
            step_frame.pack(fill="x", padx=10, pady=5)
            
            # Step title
            title_label = tk.Label(
                step_frame,
                text=step["title"],
                font=("Arial", 12, "bold"),
                bg="white",
                fg="#2c3e50",
                anchor="w"
            )
            title_label.pack(fill="x", padx=15, pady=(10, 5))
            
            # Step content
            content_label = tk.Label(
                step_frame,
                text=step["content"],
                font=("Arial", 10),
                bg="white",
                fg="#34495e",
                anchor="w",
                justify="left",
                wraplength=700
            )
            content_label.pack(fill="x", padx=15, pady=(0, 10))

def show_guide(parent=None):
    """Show the beginner's guide"""
    guide = BeginnerGuide(parent)
    return guide.window

if __name__ == "__main__":
    guide = BeginnerGuide()
    guide.window.mainloop()