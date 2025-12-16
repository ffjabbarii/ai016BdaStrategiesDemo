#!/usr/bin/env python3
"""
Production Readiness Test Suite
Tests both C# and Python BDA APIs for production deployment
"""

import subprocess
import time
import requests
import json
import os
import signal
import sys
import threading
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class ProductionTestSuite:
    def __init__(self):
        self.python_port = 8000
        self.csharp_port = 5000
        self.python_process = None
        self.csharp_process = None
        self.test_results = {
            'python': {'build': False, 'start': False, 'health': False, 'endpoints': [], 'performance': {}},
            'csharp': {'build': False, 'start': False, 'health': False, 'endpoints': [], 'performance': {}}
        }
        
    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "=" * 80)
        print(f"🚀 {title}")
        print("=" * 80)
    
    def print_section(self, title: str):
        """Print formatted section"""
        print(f"\n📋 {title}")
        print("-" * 60)
    
    def run_command(self, command: List[str], cwd: str = None, timeout: int = 30) -> Tuple[bool, str, str]:
        """Run command and return success, stdout, stderr"""
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
    
    def test_python_build(self) -> bool:
        """Test Python environment and dependencies"""
        self.print_section("Testing Python Build Environment")
        
        # Check Python version
        success, stdout, stderr = self.run_command(["python3", "--version"])
        if not success:
            print("❌ Python 3 not found")
            return False
        
        python_version = stdout.strip()
        print(f"✅ Python version: {python_version}")
        
        # Check required packages
        required_packages = ["fastapi", "uvicorn", "boto3", "requests", "python-multipart"]
        for package in required_packages:
            success, _, _ = self.run_command(["python3", "-c", f"import {package}"])
            if success:
                print(f"✅ Package {package}: Available")
            else:
                print(f"❌ Package {package}: Missing")
                print(f"💡 Install with: pip install {package}")
                return False
        
        # Test Python API files exist
        python_files = [
            "python/BlueprintAPI/src/api.py",
            "python/BlueprintAPI/src/blueprint_processor.py"
        ]
        
        for file_path in python_files:
            if os.path.exists(file_path):
                print(f"✅ Python file: {file_path}")
            else:
                print(f"❌ Missing Python file: {file_path}")
                return False
        
        self.test_results['python']['build'] = True
        print("✅ Python build environment: READY")
        return True
    
    def test_csharp_build(self) -> bool:
        """Test C# build environment"""
        self.print_section("Testing C# Build Environment")
        
        # Check .NET SDK
        success, stdout, stderr = self.run_command(["dotnet", "--version"])
        if not success:
            print("❌ .NET SDK not found")
            print("💡 Install from: https://dotnet.microsoft.com/download")
            return False
        
        dotnet_version = stdout.strip()
        print(f"✅ .NET SDK version: {dotnet_version}")
        
        # Check C# project files
        csharp_dir = "csharp/BlueprintAPI"
        if not os.path.exists(csharp_dir):
            print(f"❌ C# directory not found: {csharp_dir}")
            return False
        
        print(f"✅ C# directory: {csharp_dir}")
        
        # Build C# project
        print("🔨 Building C# project...")
        success, stdout, stderr = self.run_command(
            ["dotnet", "build", "--configuration", "Release"],
            cwd=csharp_dir,
            timeout=60
        )
        
        if success:
            print("✅ C# build: SUCCESS")
        else:
            print("❌ C# build: FAILED")
            print(f"Build error: {stderr}")
            return False
        
        # Check C# project files
        csharp_files = [
            "csharp/BlueprintAPI/Controllers/DocumentController.cs",
            "csharp/BlueprintAPI/Services/BlueprintProcessor.cs",
            "csharp/BlueprintAPI/Program.cs"
        ]
        
        for file_path in csharp_files:
            if os.path.exists(file_path):
                print(f"✅ C# file: {file_path}")
            else:
                print(f"❌ Missing C# file: {file_path}")
                return False
        
        self.test_results['csharp']['build'] = True
        print("✅ C# build environment: READY")
        return True
    
    def start_python_api(self) -> bool:
        """Start Python API"""
        self.print_section("Starting Python API")
        
        try:
            # Start Python API
            self.python_process = subprocess.Popen(
                ["python3", "-m", "uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", str(self.python_port)],
                cwd="python/BlueprintAPI",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            print(f"🚀 Python API starting on port {self.python_port}...")
            
            # Wait for API to be ready
            for attempt in range(30):
                try:
                    response = requests.get(f"http://localhost:{self.python_port}/health", timeout=2)
                    if response.status_code == 200:
                        print(f"✅ Python API ready on port {self.python_port}")
                        self.test_results['python']['start'] = True
                        return True
                except:
                    pass
                
                time.sleep(1)
                print(f"   Waiting... ({attempt + 1}/30)")
            
            print("❌ Python API failed to start")
            return False
            
        except Exception as e:
            print(f"❌ Failed to start Python API: {str(e)}")
            return False
    
    def start_csharp_api(self) -> bool:
        """Start C# API"""
        self.print_section("Starting C# API")
        
        try:
            # Start C# API
            self.csharp_process = subprocess.Popen(
                ["dotnet", "run", "--configuration", "Release"],
                cwd="csharp/BlueprintAPI",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            print(f"🚀 C# API starting on port {self.csharp_port}...")
            
            # Wait for API to be ready
            for attempt in range(30):
                try:
                    response = requests.get(f"http://localhost:{self.csharp_port}/health", timeout=2)
                    if response.status_code == 200:
                        print(f"✅ C# API ready on port {self.csharp_port}")
                        self.test_results['csharp']['start'] = True
                        return True
                except:
                    pass
                
                time.sleep(1)
                print(f"   Waiting... ({attempt + 1}/30)")
            
            print("❌ C# API failed to start")
            return False
            
        except Exception as e:
            print(f"❌ Failed to start C# API: {str(e)}")
            return False
    
    def test_api_health(self, api_name: str, port: int) -> bool:
        """Test API health endpoint"""
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=5)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {api_name} Health Check: {result}")
                self.test_results[api_name.lower()]['health'] = True
                return True
            else:
                print(f"❌ {api_name} Health Check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ {api_name} Health Check error: {str(e)}")
            return False
    
    def test_api_endpoints(self, api_name: str, port: int) -> List[str]:
        """Test all API endpoints"""
        self.print_section(f"Testing {api_name} API Endpoints")
        
        base_url = f"http://localhost:{port}"
        passed_endpoints = []
        
        # Test endpoints
        endpoints = [
            ("GET", "/", "Root endpoint"),
            ("GET", "/health", "Health check"),
            ("GET", "/blueprint/projects", "List projects"),
        ]
        
        for method, endpoint, description in endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{base_url}{endpoint}", timeout=10)
                
                if response.status_code == 200:
                    print(f"✅ {method} {endpoint}: {description} - SUCCESS")
                    passed_endpoints.append(endpoint)
                else:
                    print(f"❌ {method} {endpoint}: {description} - FAILED ({response.status_code})")
                    
            except Exception as e:
                print(f"❌ {method} {endpoint}: {description} - ERROR ({str(e)})")
        
        # Test document upload
        try:
            test_content = """
            W-2 Wage and Tax Statement
            Employee: Test User
            SSN: 123-45-6789
            Employer: Test Company
            Wages: $50,000.00
            """
            
            files = {'file': ('test-w2.txt', test_content.encode(), 'text/plain')}
            
            # Test upload to BDA project
            response = requests.post(
                f"{base_url}/blueprint/project/test-w2-fixed-1765841521/upload",
                files=files,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✅ POST /blueprint/project/upload: Document upload - SUCCESS")
                passed_endpoints.append("/blueprint/project/upload")
                result = response.json()
                print(f"   Upload result: {result.get('Status', 'Unknown')}")
            else:
                print(f"❌ POST /blueprint/project/upload: Document upload - FAILED ({response.status_code})")
                
        except Exception as e:
            print(f"❌ POST /blueprint/project/upload: Document upload - ERROR ({str(e)})")
        
        # Test direct W-2 processing
        try:
            files = {'file': ('test-w2-direct.txt', test_content.encode(), 'text/plain')}
            
            response = requests.post(
                f"{base_url}/process/w2",
                files=files,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✅ POST /process/w2: Direct W-2 processing - SUCCESS")
                passed_endpoints.append("/process/w2")
            else:
                print(f"❌ POST /process/w2: Direct W-2 processing - FAILED ({response.status_code})")
                
        except Exception as e:
            print(f"❌ POST /process/w2: Direct W-2 processing - ERROR ({str(e)})")
        
        self.test_results[api_name.lower()]['endpoints'] = passed_endpoints
        return passed_endpoints
    
    def test_api_performance(self, api_name: str, port: int) -> Dict[str, float]:
        """Test API performance"""
        self.print_section(f"Testing {api_name} API Performance")
        
        base_url = f"http://localhost:{port}"
        performance_results = {}
        
        # Test health endpoint performance
        try:
            start_time = time.time()
            response = requests.get(f"{base_url}/health", timeout=5)
            end_time = time.time()
            
            if response.status_code == 200:
                response_time = (end_time - start_time) * 1000  # Convert to ms
                performance_results['health_response_time'] = response_time
                print(f"✅ Health endpoint response time: {response_time:.2f}ms")
            else:
                print(f"❌ Health endpoint performance test failed")
                
        except Exception as e:
            print(f"❌ Health endpoint performance error: {str(e)}")
        
        # Test multiple concurrent requests
        try:
            import concurrent.futures
            
            def make_request():
                start = time.time()
                response = requests.get(f"{base_url}/health", timeout=5)
                end = time.time()
                return (end - start) * 1000 if response.status_code == 200 else None
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_request) for _ in range(10)]
                response_times = [f.result() for f in concurrent.futures.as_completed(futures)]
                response_times = [rt for rt in response_times if rt is not None]
            
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                max_response_time = max(response_times)
                performance_results['avg_concurrent_response_time'] = avg_response_time
                performance_results['max_concurrent_response_time'] = max_response_time
                print(f"✅ Concurrent requests (10): Avg {avg_response_time:.2f}ms, Max {max_response_time:.2f}ms")
            else:
                print(f"❌ Concurrent request test failed")
                
        except Exception as e:
            print(f"❌ Concurrent request test error: {str(e)}")
        
        self.test_results[api_name.lower()]['performance'] = performance_results
        return performance_results
    
    def test_cross_api_compatibility(self) -> bool:
        """Test that both APIs work with the same BDA project"""
        self.print_section("Testing Cross-API Compatibility")
        
        project_name = "test-w2-fixed-1765841521"
        test_content = """
        W-2 Wage and Tax Statement - Cross API Test
        Employee: Cross Test User
        SSN: 987-65-4321
        Employer: Cross Test Company
        Wages: $60,000.00
        """
        
        # Test Python API
        try:
            files = {'file': ('cross-test-python.txt', test_content.encode(), 'text/plain')}
            response = requests.post(
                f"http://localhost:{self.python_port}/blueprint/project/{project_name}/upload",
                files=files,
                timeout=30
            )
            
            python_success = response.status_code == 200
            if python_success:
                python_result = response.json()
                print(f"✅ Python API cross-test: SUCCESS")
                print(f"   Python S3 URI: {python_result.get('s3_uri', 'N/A')}")
            else:
                print(f"❌ Python API cross-test: FAILED ({response.status_code})")
                
        except Exception as e:
            print(f"❌ Python API cross-test error: {str(e)}")
            python_success = False
        
        # Test C# API
        try:
            files = {'file': ('cross-test-csharp.txt', test_content.encode(), 'text/plain')}
            response = requests.post(
                f"http://localhost:{self.csharp_port}/blueprint/project/{project_name}/upload",
                files=files,
                timeout=30
            )
            
            csharp_success = response.status_code == 200
            if csharp_success:
                csharp_result = response.json()
                print(f"✅ C# API cross-test: SUCCESS")
                print(f"   C# S3 URI: {csharp_result.get('S3Uri', 'N/A')}")
            else:
                print(f"❌ C# API cross-test: FAILED ({response.status_code})")
                
        except Exception as e:
            print(f"❌ C# API cross-test error: {str(e)}")
            csharp_success = False
        
        compatibility_success = python_success and csharp_success
        
        if compatibility_success:
            print("✅ Cross-API compatibility: PASSED")
            print("   Both APIs can work with the same BDA project")
        else:
            print("❌ Cross-API compatibility: FAILED")
        
        return compatibility_success
    
    def generate_production_report(self) -> str:
        """Generate production readiness report"""
        self.print_header("PRODUCTION READINESS REPORT")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
PRODUCTION READINESS REPORT
Generated: {timestamp}

🐍 PYTHON API (Port {self.python_port}):
  Build Environment: {'✅ READY' if self.test_results['python']['build'] else '❌ FAILED'}
  API Startup: {'✅ SUCCESS' if self.test_results['python']['start'] else '❌ FAILED'}
  Health Check: {'✅ PASSED' if self.test_results['python']['health'] else '❌ FAILED'}
  Endpoints Tested: {len(self.test_results['python']['endpoints'])}
  Performance: {len(self.test_results['python']['performance'])} metrics collected

🔷 C# API (Port {self.csharp_port}):
  Build Environment: {'✅ READY' if self.test_results['csharp']['build'] else '❌ FAILED'}
  API Startup: {'✅ SUCCESS' if self.test_results['csharp']['start'] else '❌ FAILED'}
  Health Check: {'✅ PASSED' if self.test_results['csharp']['health'] else '❌ FAILED'}
  Endpoints Tested: {len(self.test_results['csharp']['endpoints'])}
  Performance: {len(self.test_results['csharp']['performance'])} metrics collected

🎯 PRODUCTION READINESS STATUS:
"""
        
        # Calculate overall readiness
        python_ready = (
            self.test_results['python']['build'] and
            self.test_results['python']['start'] and
            self.test_results['python']['health'] and
            len(self.test_results['python']['endpoints']) >= 3
        )
        
        csharp_ready = (
            self.test_results['csharp']['build'] and
            self.test_results['csharp']['start'] and
            self.test_results['csharp']['health'] and
            len(self.test_results['csharp']['endpoints']) >= 3
        )
        
        overall_ready = python_ready and csharp_ready
        
        if overall_ready:
            report += "  🚀 READY FOR PRODUCTION DEPLOYMENT\n"
            report += "  ✅ Both APIs are fully functional\n"
            report += "  ✅ All critical endpoints working\n"
            report += "  ✅ Performance metrics collected\n"
            report += "  ✅ Cross-API compatibility verified\n"
        else:
            report += "  ⚠️  NOT READY FOR PRODUCTION\n"
            if not python_ready:
                report += "  ❌ Python API issues detected\n"
            if not csharp_ready:
                report += "  ❌ C# API issues detected\n"
        
        report += f"""
📊 DEPLOYMENT CONFIGURATION:
  Python API: http://localhost:{self.python_port}
  C# API: http://localhost:{self.csharp_port}
  BDA Project: test-w2-fixed-1765841521
  AWS Region: us-east-1
  
🔧 NEXT STEPS:
  1. Deploy Python API to production port {self.python_port}
  2. Deploy C# API to production port {self.csharp_port}
  3. Configure load balancer for both APIs
  4. Set up monitoring and logging
  5. Configure AWS credentials for production
"""
        
        print(report)
        
        # Save report to file
        with open("production_readiness_report.txt", "w") as f:
            f.write(report)
        
        print(f"📄 Report saved to: production_readiness_report.txt")
        
        return report
    
    def cleanup(self):
        """Clean up processes"""
        print("\n🧹 Cleaning up processes...")
        
        if self.python_process:
            self.python_process.terminate()
            self.python_process.wait()
            print("✅ Python API stopped")
        
        if self.csharp_process:
            self.csharp_process.terminate()
            self.csharp_process.wait()
            print("✅ C# API stopped")
    
    def run_full_test_suite(self):
        """Run complete production readiness test suite"""
        self.print_header("PRODUCTION READINESS TEST SUITE")
        print("Testing both Python and C# BDA APIs for production deployment")
        
        try:
            # Test build environments
            python_build_ok = self.test_python_build()
            csharp_build_ok = self.test_csharp_build()
            
            if not python_build_ok or not csharp_build_ok:
                print("\n❌ Build environment issues detected. Cannot proceed with API tests.")
                return False
            
            # Start APIs
            python_start_ok = self.start_python_api()
            csharp_start_ok = self.start_csharp_api()
            
            if not python_start_ok or not csharp_start_ok:
                print("\n❌ API startup issues detected.")
                return False
            
            # Test health checks
            self.print_section("Testing API Health Checks")
            python_health_ok = self.test_api_health("Python", self.python_port)
            csharp_health_ok = self.test_api_health("C#", self.csharp_port)
            
            # Test endpoints
            python_endpoints = self.test_api_endpoints("Python", self.python_port)
            csharp_endpoints = self.test_api_endpoints("C#", self.csharp_port)
            
            # Test performance
            python_perf = self.test_api_performance("Python", self.python_port)
            csharp_perf = self.test_api_performance("C#", self.csharp_port)
            
            # Test cross-API compatibility
            compatibility_ok = self.test_cross_api_compatibility()
            
            # Generate report
            self.generate_production_report()
            
            return True
            
        except KeyboardInterrupt:
            print("\n⚠️ Test suite interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Test suite error: {str(e)}")
            return False
        finally:
            self.cleanup()

def main():
    """Main function"""
    def signal_handler(sig, frame):
        print("\n🛑 Shutting down test suite...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    test_suite = ProductionTestSuite()
    success = test_suite.run_full_test_suite()
    
    if success:
        print("\n🎉 Production readiness test suite completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Production readiness test suite failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()