#!/usr/bin/env python3
"""
Debug C# build issues with detailed output
"""

import subprocess
import os

def debug_csharp_build():
    """Debug C# build with full output"""
    
    print("🔍 DEBUGGING C# BUILD ISSUES")
    print("=" * 50)
    
    csharp_dir = "csharp/BlueprintAPI"
    
    # Check files exist
    print("📁 Checking C# files...")
    files_to_check = [
        "Program.cs",
        "Controllers/DocumentController.cs", 
        "Services/BlueprintProcessor.cs",
        "Services/IBlueprintProcessor.cs",
        "Models/DocumentModels.cs",
        "BlueprintAPI.csproj"
    ]
    
    for file_path in files_to_check:
        full_path = os.path.join(csharp_dir, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
    
    # Try build with full output
    print("\n🔨 Building with detailed output...")
    try:
        result = subprocess.run(
            ["dotnet", "build", "--verbosity", "detailed"],
            cwd=csharp_dir,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        print(f"Return code: {result.returncode}")
        print(f"\nSTDOUT:\n{result.stdout}")
        print(f"\nSTDERR:\n{result.stderr}")
        
        if result.returncode == 0:
            print("✅ Build successful!")
            return True
        else:
            print("❌ Build failed - see output above")
            return False
            
    except Exception as e:
        print(f"❌ Build error: {str(e)}")
        return False

if __name__ == "__main__":
    debug_csharp_build()