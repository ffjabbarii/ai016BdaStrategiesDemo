#!/usr/bin/env python3
"""
Check YOUR specific BDA project: test-w2-fixed-1765841521
"""

import subprocess
import json

def check_my_project():
    """Check your specific BDA project contents"""
    
    project_name = "test-w2-fixed-1765841521"
    project_id = "a07a2d75b205"
    bucket_name = f"bda-project-storage-{project_id}"
    
    print(f"🎯 YOUR BDA PROJECT: {project_name}")
    print("=" * 60)
    
    # Check your project's S3 bucket
    print(f"\n📁 YOUR PROJECT BUCKET: {bucket_name}")
    try:
        cmd = ['aws', 's3', 'ls', f's3://{bucket_name}/', '--recursive']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if lines and lines[0]:
                print(f"✅ Found {len(lines)} files in your project")
                
                # Show what you have
                documents = []
                results = []
                bda_output = []
                
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 4:
                            key = ' '.join(parts[3:])
                            if key.startswith('documents/'):
                                documents.append(key)
                            elif key.startswith('results/'):
                                results.append(key)
                            elif key.startswith('bda-output/'):
                                bda_output.append(key)
                
                print(f"\n📄 DOCUMENTS UPLOADED ({len(documents)}):")
                for doc in documents:
                    print(f"  • {doc}")
                
                print(f"\n📊 BDA PROCESSING RESULTS ({len(bda_output)}):")
                for output in bda_output:
                    print(f"  • {output}")
                
                if results:
                    print(f"\n📋 OTHER RESULTS ({len(results)}):")
                    for res in results:
                        print(f"  • {res}")
                
                # Show the actual BDA result
                if bda_output:
                    print(f"\n🔍 CHECKING YOUR BDA RESULT:")
                    result_file = None
                    for output in bda_output:
                        if 'result.json' in output:
                            result_file = output
                            break
                    
                    if result_file:
                        print(f"📥 Downloading: {result_file}")
                        cmd = ['aws', 's3', 'cp', f's3://{bucket_name}/{result_file}', '/tmp/bda_result.json']
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                        
                        if result.returncode == 0:
                            try:
                                with open('/tmp/bda_result.json', 'r') as f:
                                    bda_result = json.load(f)
                                
                                print("✅ BDA PROCESSING RESULT:")
                                print(json.dumps(bda_result, indent=2))
                                
                            except Exception as e:
                                print(f"❌ Error reading result: {str(e)}")
                        else:
                            print(f"❌ Error downloading result: {result.stderr}")
            else:
                print("❌ No files found in your project bucket")
        else:
            print(f"❌ Error accessing your bucket: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print(f"\n💡 WHY CONSOLE MIGHT BE EMPTY:")
    print("• AWS Console BDA interface may not show processed results immediately")
    print("• Console might only show 'active' processing jobs, not completed ones")
    print("• Your results are in S3 but Console UI might not display them")
    print("• Try refreshing the Console page or checking the S3 bucket directly")

if __name__ == "__main__":
    check_my_project()