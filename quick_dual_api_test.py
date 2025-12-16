#!/usr/bin/env python3
"""
Quick Dual API Test - Fast testing of both Python and C# APIs
"""

import subprocess
import time
import requests
import json
import os
import signal
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

def test_api_quick(api_name: str, port: int) -> dict:
    """Quick test of an API"""
    results = {
        'name': api_name,
        'port': port,
        'health': False,
        'projects': False,
        'upload': False,
        'response_time': 0
    }
    
    base_url = f"http://localhost:{port}"
    
    try:
        # Health check with timing
        start_time = time.time()
        response = requests.get(f"{base_url}/health", timeout=5)
        end_time = time.time()
        
        if response.status_code == 200:
            results['health'] = True
            results['response_time'] = round((end_time - start_time) * 1000, 2)
            health_data = response.json()
            print(f"✅ {api_name} Health ({results['response_time']}ms): {health_data.get('Message', 'OK')}")
        else:
            print(f"❌ {api_name} Health: Failed ({response.status_code})")
            return results
    except Exception as e:
        print(f"❌ {api_name} Health: Error - {str(e)}")
        return results
    
    try:
        # Projects list
        response = requests.get(f"{base_url}/blueprint/projects", timeout=10)
        if response.status_code == 200:
            results['projects'] = True
            projects_data = response.json()
            project_count = len(projects_data.get('projects', projects_data.get('Projects', [])))
            print(f"✅ {api_name} Projects: {project_count} found")
        else:
            print(f"❌ {api_name} Projects: Failed ({response.status_code})")
    except Exception as e:
        print(f"❌ {api_name} Projects: Error - {str(e)}")
    
    try:
        # Quick upload test
        test_content = f"Test W-2 from {api_name} API - {time.time()}"
        files = {'file': (f'test-{api_name.lower()}.txt', test_content.encode(), 'text/plain')}
        
        response = requests.post(
            f"{base_url}/blueprint/project/test-w2-fixed-1765841521/upload",
            files=files,
            timeout=20
        )
        
        if response.status_code == 200:
            results['upload'] = True
            upload_data = response.json()
            status = upload_data.get('status', upload_data.get('Status', 'Unknown'))
            print(f"✅ {api_name} Upload: {status}")
        else:
            print(f"❌ {api_name} Upload: Failed ({response.status_code})")
    except Exception as e:
        print(f"❌ {api_name} Upload: Error - {str(e)}")
    
    return results

def check_processes():
    """Check if APIs are running"""
    python_running = False
    csharp_running = False
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        python_running = response.status_code == 200
    except:
        pass
    
    try:
        response = requests.get("http://localhost:5000/health", timeout=2)
        csharp_running = response.status_code == 200
    except:
        pass
    
    return python_running, csharp_running

def main():
    """Main function for quick dual API testing"""
    print("🚀 QUICK DUAL API TEST")
    print("=" * 50)
    
    # Check if APIs are running
    python_running, csharp_running = check_processes()
    
    print(f"🐍 Python API (8000): {'🟢 Running' if python_running else '🔴 Not Running'}")
    print(f"🔷 C# API (5000): {'🟢 Running' if csharp_running else '🔴 Not Running'}")
    
    if not python_running and not csharp_running:
        print("\n❌ No APIs are running!")
        print("💡 Start them with:")
        print("   Python: cd python/BlueprintAPI && python3 -m uvicorn src.api:app --port 8000")
        print("   C#: cd csharp/BlueprintAPI && dotnet run")
        return
    
    print("\n📋 Testing Available APIs...")
    
    # Test APIs concurrently
    results = []
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = []
        
        if python_running:
            futures.append(executor.submit(test_api_quick, "Python", 8000))
        
        if csharp_running:
            futures.append(executor.submit(test_api_quick, "C#", 5000))
        
        for future in as_completed(futures):
            results.append(future.result())
    
    # Summary
    print("\n📊 QUICK TEST SUMMARY")
    print("-" * 30)
    
    for result in results:
        name = result['name']
        port = result['port']
        health = "✅" if result['health'] else "❌"
        projects = "✅" if result['projects'] else "❌"
        upload = "✅" if result['upload'] else "❌"
        response_time = result['response_time']
        
        print(f"{name} API (:{port})")
        print(f"  Health: {health} ({response_time}ms)")
        print(f"  Projects: {projects}")
        print(f"  Upload: {upload}")
    
    # Overall status
    all_healthy = all(r['health'] for r in results)
    all_functional = all(r['health'] and r['projects'] and r['upload'] for r in results)
    
    if all_functional:
        print("\n🎉 ALL APIS FULLY FUNCTIONAL!")
        print("✅ Ready for production use")
    elif all_healthy:
        print("\n⚠️ APIs are healthy but some features failed")
        print("🔧 Check individual test results above")
    else:
        print("\n❌ Some APIs have health issues")
        print("🚨 Not ready for production")
    
    # Performance comparison
    if len(results) == 2:
        python_time = next(r['response_time'] for r in results if r['name'] == 'Python')
        csharp_time = next(r['response_time'] for r in results if r['name'] == 'C#')
        
        print(f"\n⚡ Performance Comparison:")
        if python_time > 0 and csharp_time > 0:
            faster = "C#" if csharp_time < python_time else "Python"
            diff = abs(python_time - csharp_time)
            print(f"   {faster} is {diff:.1f}ms faster")
        print(f"   Python: {python_time}ms")
        print(f"   C#: {csharp_time}ms")

if __name__ == "__main__":
    main()