#!/usr/bin/env python3
"""
Check what's actually in the BDA project vs what shows in AWS Console
"""

import boto3
import json
from datetime import datetime

def check_bda_project_contents():
    """Check all components of the BDA project using AWS CLI since SDK methods may not be available"""
    
    import subprocess
    import json
    
    project_id = "test-w2-fixed-1765841521"
    
    print("🔍 CHECKING BDA PROJECT CONTENTS vs AWS CONSOLE")
    print("=" * 60)
    
    # First, let's see what AWS CLI commands are available for BDA
    print("\n🔧 CHECKING AVAILABLE BDA COMMANDS:")
    try:
        result = subprocess.run(['aws', 'bedrock-agent', 'help'], 
                              capture_output=True, text=True, timeout=30)
        
        # Look for data-automation commands
        if 'data-automation' in result.stdout:
            print("✅ Data automation commands found in AWS CLI")
        else:
            print("❌ Data automation commands not found - may need CLI update")
            
    except Exception as e:
        print(f"Error checking CLI: {str(e)}")
    
    # Try to list projects to see if our project exists
    print(f"\n📋 CHECKING IF PROJECT EXISTS:")
    try:
        cmd = ['aws', 'bedrock-agent', 'list-data-automation-projects', '--region', 'us-east-1']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            projects = json.loads(result.stdout)
            found_project = False
            
            for project in projects.get('projects', []):
                if project['projectName'] == project_id or project.get('projectId') == project_id:
                    found_project = True
                    print(f"✅ Found project: {project['projectName']}")
                    print(f"   Status: {project.get('status', 'Unknown')}")
                    print(f"   Created: {project.get('createdAt', 'Unknown')}")
                    break
            
            if not found_project:
                print(f"❌ Project '{project_id}' not found in project list")
                print("Available projects:")
                for project in projects.get('projects', []):
                    print(f"  - {project['projectName']} (Status: {project.get('status', 'Unknown')})")
        else:
            print(f"❌ Error listing projects: {result.stderr}")
            
    except Exception as e:
        print(f"Error checking projects: {str(e)}")
    
    # Check S3 bucket
    print(f"\n📁 S3 BUCKET CONTENTS:")
    bucket_name = f"bedrock-data-automation-{project_id}"
    
    try:
        cmd = ['aws', 's3', 'ls', f's3://{bucket_name}/', '--recursive', '--region', 'us-east-1']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if lines and lines[0]:
                print(f"✅ Found {len(lines)} objects in bucket")
                
                # Group by folder
                folders = {}
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 4:
                            key = ' '.join(parts[3:])
                            folder = key.split('/')[0] if '/' in key else 'root'
                            
                            if folder not in folders:
                                folders[folder] = []
                            folders[folder].append(key)
                
                for folder, files in folders.items():
                    print(f"\n  📂 {folder}/ ({len(files)} files)")
                    for file in files[:5]:
                        print(f"    📄 {file}")
                    if len(files) > 5:
                        print(f"    ... and {len(files) - 5} more files")
            else:
                print("No objects found in bucket")
        else:
            print(f"❌ Error accessing bucket: {result.stderr}")
            
    except Exception as e:
        print(f"Error checking S3: {str(e)}")
    
    # Console visibility explanation
    print(f"\n💡 WHY CONSOLE MIGHT NOT SHOW EVERYTHING:")
    print("  • Console UI may have caching delays (refresh the page)")
    print("  • Some operations are async and take time to appear")
    print("  • Console might filter out intermediate/temporary files")
    print("  • Regional differences in UI updates")
    print("  • Blueprint stages affect visibility")
    print("  • Processing status affects what's shown")
    print("  • Project name vs ID confusion")
    
    print(f"\n🔄 TROUBLESHOOTING STEPS:")
    print("  1. Refresh your AWS Console page")
    print("  2. Check you're in the correct region (us-east-1)")
    print("  3. Verify project name/ID in Console matches what we found")
    print("  4. Look for 'Processing' or 'In Progress' indicators")
    print("  5. Check the S3 bucket directly in Console")
    
    return True

if __name__ == "__main__":
    check_bda_project_contents()