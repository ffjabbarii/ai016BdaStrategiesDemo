#!/usr/bin/env python3
"""
Check and upgrade AWS CLI to get BDA commands
"""

import subprocess
import sys

def check_aws_cli_version():
    """Check current AWS CLI version"""
    
    print("🔍 CHECKING AWS CLI VERSION")
    print("=" * 40)
    
    try:
        result = subprocess.run(["aws", "--version"], capture_output=True, text=True)
        
        if result.returncode == 0:
            version_info = result.stdout.strip()
            print(f"✅ Current AWS CLI: {version_info}")
            
            # Extract version number
            if "aws-cli/" in version_info:
                version_part = version_info.split("aws-cli/")[1].split()[0]
                print(f"📋 Version: {version_part}")
                
                # Check if it's version 2.x (required for newer services)
                if version_part.startswith("1."):
                    print("⚠️ AWS CLI v1 detected - BDA requires v2")
                    return False, version_part
                elif version_part.startswith("2."):
                    print("✅ AWS CLI v2 detected")
                    return True, version_part
                else:
                    print("❓ Unknown version format")
                    return False, version_part
            else:
                print("❓ Cannot parse version")
                return False, "unknown"
        else:
            print("❌ AWS CLI not found or error")
            return False, None
            
    except Exception as e:
        print(f"❌ Error checking AWS CLI: {str(e)}")
        return False, None

def upgrade_aws_cli():
    """Upgrade AWS CLI to latest version"""
    
    print("\n🔧 UPGRADING AWS CLI")
    print("=" * 30)
    
    # Check if we're on macOS (based on system info)
    try:
        # Try homebrew first (common on macOS)
        print("🍺 Trying Homebrew upgrade...")
        result = subprocess.run(["brew", "upgrade", "awscli"], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ AWS CLI upgraded via Homebrew")
            return True
        else:
            print(f"⚠️ Homebrew upgrade failed: {result.stderr}")
    except:
        print("⚠️ Homebrew not available")
    
    # Try pip upgrade
    try:
        print("🐍 Trying pip upgrade...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "awscli"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ AWS CLI upgraded via pip")
            return True
        else:
            print(f"⚠️ Pip upgrade failed: {result.stderr}")
    except:
        print("⚠️ Pip upgrade failed")
    
    # Manual installation instructions
    print("\n📋 MANUAL UPGRADE INSTRUCTIONS:")
    print("1. Download AWS CLI v2 installer:")
    print("   macOS: https://awscli.amazonaws.com/AWSCLIV2.pkg")
    print("   Linux: https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip")
    print("2. Or use curl:")
    print("   curl 'https://awscli.amazonaws.com/AWSCLIV2.pkg' -o 'AWSCLIV2.pkg'")
    print("   sudo installer -pkg AWSCLIV2.pkg -target /")
    
    return False

def test_bda_commands():
    """Test if BDA commands are available after upgrade"""
    
    print("\n🧪 TESTING BDA COMMANDS")
    print("=" * 30)
    
    bda_commands = [
        ["aws", "bedrock", "help"],
        ["aws", "bedrock-data-automation", "help"],
        ["aws", "bedrock-data-automation-runtime", "help"],
    ]
    
    available_commands = []
    
    for cmd in bda_commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"✅ {' '.join(cmd[:2])} - Available")
                available_commands.append(cmd[1])
            else:
                if "Invalid choice" in result.stderr:
                    print(f"❌ {' '.join(cmd[:2])} - Not available")
                else:
                    print(f"⚠️ {' '.join(cmd[:2])} - Error: {result.stderr[:50]}...")
        except:
            print(f"❌ {' '.join(cmd[:2])} - Failed to test")
    
    return available_commands

def check_bda_profile_commands():
    """Check for BDA profile-related commands"""
    
    print("\n🔍 CHECKING BDA PROFILE COMMANDS")
    print("=" * 40)
    
    if "bedrock-data-automation" in test_bda_commands():
        profile_commands = [
            ["aws", "bedrock-data-automation", "list-data-automation-profiles"],
            ["aws", "bedrock-data-automation", "create-data-automation-profile"],
            ["aws", "bedrock-data-automation", "get-data-automation-profile"],
        ]
        
        for cmd in profile_commands:
            try:
                # Just check if the command exists (don't actually run it)
                result = subprocess.run(cmd + ["--help"], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    print(f"✅ {cmd[2]} - Available")
                else:
                    print(f"❌ {cmd[2]} - Not available")
            except:
                print(f"❌ {cmd[2]} - Failed to check")
    else:
        print("❌ bedrock-data-automation not available")

def main():
    print("🚀 AWS CLI BDA UPGRADE CHECK")
    print("=" * 50)
    
    # Check current version
    is_v2, version = check_aws_cli_version()
    
    if not is_v2:
        print(f"\n🔧 AWS CLI upgrade needed")
        
        # Ask user if they want to upgrade
        print("Do you want to upgrade AWS CLI? (y/n): ", end="")
        response = input().lower().strip()
        
        if response in ['y', 'yes']:
            success = upgrade_aws_cli()
            
            if success:
                # Re-check version after upgrade
                print("\n🔍 Checking version after upgrade...")
                is_v2_new, version_new = check_aws_cli_version()
                
                if is_v2_new:
                    print("✅ AWS CLI successfully upgraded!")
                else:
                    print("⚠️ Upgrade may not have worked, check manually")
            else:
                print("⚠️ Automatic upgrade failed, please upgrade manually")
        else:
            print("⚠️ Skipping upgrade - BDA commands may not be available")
    
    # Test BDA commands
    available = test_bda_commands()
    
    if "bedrock-data-automation" in available:
        print("\n✅ BDA commands are available!")
        check_bda_profile_commands()
        
        print(f"\n🧪 NOW TRY THESE COMMANDS:")
        print(f"aws bedrock-data-automation list-data-automation-profiles")
        print(f"aws bedrock-data-automation-runtime invoke-data-automation-async help")
        
    else:
        print("\n❌ BDA commands still not available")
        print("This might mean:")
        print("1. BDA is not available in your region")
        print("2. Your account doesn't have BDA access")
        print("3. BDA is still in preview/limited availability")
        
        print(f"\n🔧 NEXT STEPS:")
        print(f"1. Check AWS Console → Bedrock → Data Automation")
        print(f"2. Verify your region supports BDA")
        print(f"3. Contact AWS support about BDA availability")

if __name__ == "__main__":
    main()