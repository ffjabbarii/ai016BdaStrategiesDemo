#!/usr/bin/env python3
"""
Quick setup verification script for BDA testing
Run this first to make sure everything is ready
"""

import sys
import subprocess
import os
from pathlib import Path

def check_python():
    """Check Python version"""
    version = sys.version_info
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Need Python 3.8 or higher")
        return False
    return True

def check_dependencies():
    """Check if required packages are available"""
    required = ['tkinter', 'requests', 'psutil']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"✅ {package} available")
        except ImportError:
            print(f"❌ {package} missing")
            missing.append(package)
    
    return len(missing) == 0

def install_dependencies():
    """Install missing dependencies"""
    startup_dir = Path(__file__).parent / "Startup"
    requirements_file = startup_dir / "requirements.txt"
    
    if requirements_file.exists():
        print("📦 Installing dependencies...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)], 
                         check=True, capture_output=True)
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    else:
        print("❌ Requirements file not found")
        return False

def create_sample_w2():
    """Create a sample W-2 file for testing"""
    sample_dir = Path(__file__).parent / "test_files"
    sample_dir.mkdir(exist_ok=True)
    
    # Create a simple text file that simulates a W-2 (for testing without real documents)
    sample_w2 = sample_dir / "sample_w2.txt"
    
    w2_content = """
W-2 Wage and Tax Statement

Employee Information:
Name: John Doe
SSN: 123-45-6789
Address: 123 Main St, Anytown, ST 12345

Employer Information:
Name: Sample Corporation
EIN: 12-3456789
Address: 456 Business Ave, Corporate City, ST 67890

Tax Information:
Box 1 - Wages: $75,000.00
Box 2 - Federal Tax Withheld: $12,500.00
Box 3 - Social Security Wages: $75,000.00
Box 4 - Social Security Tax: $4,650.00
Box 5 - Medicare Wages: $75,000.00
Box 6 - Medicare Tax: $1,087.50
"""
    
    with open(sample_w2, 'w') as f:
        f.write(w2_content)
    
    print(f"✅ Sample W-2 created: {sample_w2}")
    return sample_w2

def main():
    print("🔍 BDA System Setup Check")
    print("=" * 40)
    
    # Check Python
    if not check_python():
        print("\n❌ Please install Python 3.8 or higher")
        return
    
    # Check dependencies
    if not check_dependencies():
        print("\n📦 Installing missing dependencies...")
        if not install_dependencies():
            print("\n❌ Setup failed. Please install dependencies manually:")
            print("pip install tkinter requests psutil")
            return
    
    # Create sample files
    sample_file = create_sample_w2()
    
    print("\n🎉 Setup Complete!")
    print("\nNext steps:")
    print("1. Run: python Startup/startup.py")
    print("2. Start a project (try Python Blueprint API)")
    print(f"3. Test with sample file: {sample_file}")
    print("\n💡 Tip: Keep this terminal open to see any error messages")

if __name__ == "__main__":
    main()