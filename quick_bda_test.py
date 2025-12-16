#!/usr/bin/env python3
"""
Quick test to see the exact BDA error
"""

import requests
import json

def quick_bda_test():
    """Quick test of BDA upload to see exact error"""
    
    print("🔍 Quick BDA Test")
    print("=" * 30)
    
    API_URL = "http://localhost:8000"
    
    # Test with the W-2 file
    try:
        with open("test_files/w-2.pdf", 'rb') as f:
            files = {'file': ('w-2.pdf', f, 'application/pdf')}
            
            print("📤 Uploading W-2 to BDA project...")
            response = requests.post(
                f"{API_URL}/blueprint/project/test-w2-fixed-1765841521/upload",
                files=files
            )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS!")
            print(json.dumps(data, indent=2))
        else:
            print("❌ FAILED!")
            try:
                error_data = response.json()
                print("Error details:")
                print(json.dumps(error_data, indent=2))
            except:
                print("Raw error:")
                print(response.text)
                
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    quick_bda_test()