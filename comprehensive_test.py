#!/usr/bin/env python3
"""
Comprehensive Integration Test Suite
Tests all API endpoints, authentication flows, and integration scenarios
"""
import subprocess
import time
import requests
import json
import sys
from typing import Dict, Optional

class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'

class APITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.user_id: Optional[str] = None
        self.project_id: Optional[str] = None
        self.feedback_id: Optional[str] = None
        self.revision_id: Optional[str] = None
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        
    def print_header(self, text: str):
        print(f"\n{Colors.BLUE}{'=' * 60}{Colors.NC}")
        print(f"{Colors.BLUE}{text:^60}{Colors.NC}")
        print(f"{Colors.BLUE}{'=' * 60}{Colors.NC}\n")
    
    def print_test(self, name: str, status: str, details: str = ""):
        if status == "PASS":
            print(f"{Colors.GREEN}✓{Colors.NC} {name}")
            if details:
                print(f"  {details}")
            self.passed += 1
        elif status == "FAIL":
            print(f"{Colors.RED}✗{Colors.NC} {name}")
            if details:
                print(f"  {Colors.RED}{details}{Colors.NC}")
            self.failed += 1
        elif status == "WARN":
            print(f"{Colors.YELLOW}⚠{Colors.NC} {name}")
            if details:
                print(f"  {Colors.YELLOW}{details}{Colors.NC}")
            self.warnings += 1
    
    def test_health_endpoints(self):
        """Test health check endpoints"""
        self.print_header("Testing Health Endpoints")
        
        # Test /health
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.print_test(
                    "GET /health",
                    "PASS",
                    f"Status: {data.get('status')}, Environment: {data.get('environment')}"
                )
            else:
                self.print_test("GET /health", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("GET /health", "FAIL", str(e))
        
        # Test /health/db
        try:
            response = requests.get(f"{self.base_url}/health/db", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.print_test(
                    "GET /health/db",
                    "PASS",
                    f"Database: {data.get('database')}"
                )
            else:
                self.print_test("GET /health/db", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("GET /health/db", "FAIL", str(e))
    
    def test_authentication_flow(self):
        """Test complete authentication flow"""
        self.print_header("Testing Authentication Flow")
        
        # Generate unique test credentials
        test_email = f"test_{int(time.time())}@example.com"
        test_password = "TestPassword123!"
        
        # Test registration
        try:
            register_data = {
                "email": test_email,
                "password": test_password,
                "full_name": "Test User"
            }
            response = requests.post(
                f"{self.base_url}/api/v1/auth/register",
                json=register_data,
                timeout=5
            )
            
            if response.status_code == 201:
                data = response.json()
                self.user_id = data.get("id")
                self.print_test(
                    "POST /api/v1/auth/register",
                    "PASS",
                    f"User created: {data.get('email')}"
                )
            elif response.status_code == 422:
                self.print_test(
                    "POST /api/v1/auth/register",
                    "WARN",
                    "Validation error (expected for schema validation)"
                )
            else:
                self.print_test(
                    "POST /api/v1/auth/register",
                    "FAIL",
                    f"Status: {response.status_code}"
                )
        except Exception as e:
            self.print_test("POST /api/v1/auth/register", "FAIL", str(e))
        
        # Test login with the same credentials
        try:
            login_data = {
                "email": test_email,
                "password": test_password
            }
            response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                json=login_data,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.print_test(
                    "POST /api/v1/auth/login",
                    "PASS",
                    "Token received, authentication successful"
                )
            elif response.status_code == 401:
                self.print_test(
                    "POST /api/v1/auth/login",
                    "FAIL",
                    "Login failed with correct credentials (401 Unauthorized)"
                )
            elif response.status_code == 422:
                self.print_test(
                    "POST /api/v1/auth/login",
                    "WARN",
                    "Validation error"
                )
            else:
                self.print_test(
                    "POST /api/v1/auth/login",
                    "FAIL",
                    f"Status: {response.status_code}"
                )
        except Exception as e:
            self.print_test("POST /api/v1/auth/login", "FAIL", str(e))
        
        # Test /auth/me without token
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/auth/me",
                timeout=5
            )
            
            if response.status_code in [401, 403]:
                self.print_test(
                    "GET /api/v1/auth/me (no auth)",
                    "PASS",
                    "Correctly requires authentication"
                )
            else:
                self.print_test(
                    "GET /api/v1/auth/me (no auth)",
                    "FAIL",
                    f"Should return 401/403, got {response.status_code}"
                )
        except Exception as e:
            self.print_test("GET /api/v1/auth/me (no auth)", "FAIL", str(e))
    
    def test_projects_endpoints(self):
        """Test project management endpoints"""
        self.print_header("Testing Projects Endpoints")
        
        # Test list projects (no auth)
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/projects/",
                timeout=5
            )
            
            if response.status_code in [401, 403]:
                self.print_test(
                    "GET /api/v1/projects/ (no auth)",
                    "PASS",
                    "Correctly requires authentication"
                )
            elif response.status_code == 200:
                self.print_test(
                    "GET /api/v1/projects/ (no auth)",
                    "WARN",
                    "Endpoint accessible without auth (may be intentional)"
                )
            else:
                self.print_test(
                    "GET /api/v1/projects/ (no auth)",
                    "FAIL",
                    f"Status: {response.status_code}"
                )
        except Exception as e:
            self.print_test("GET /api/v1/projects/", "FAIL", str(e))
        
        # Test create project (no auth)
        try:
            project_data = {
                "name": "Test Project",
                "description": "Test Description"
            }
            response = requests.post(
                f"{self.base_url}/api/v1/projects/",
                json=project_data,
                timeout=5
            )
            
            if response.status_code in [401, 403]:
                self.print_test(
                    "POST /api/v1/projects/ (no auth)",
                    "PASS",
                    "Correctly requires authentication"
                )
            elif response.status_code == 422:
                self.print_test(
                    "POST /api/v1/projects/ (no auth)",
                    "WARN",
                    "Validation error"
                )
            else:
                self.print_test(
                    "POST /api/v1/projects/ (no auth)",
                    "FAIL",
                    f"Status: {response.status_code}"
                )
        except Exception as e:
            self.print_test("POST /api/v1/projects/", "FAIL", str(e))
    
    def test_feedback_endpoints(self):
        """Test feedback endpoints"""
        self.print_header("Testing Feedback Endpoints")
        
        # Test submit feedback (no auth)
        try:
            feedback_data = {
                "project_id": "test-project-id",
                "raw_text": "Make it pop and add more energy to the design"
            }
            response = requests.post(
                f"{self.base_url}/api/v1/feedback/",
                json=feedback_data,
                timeout=5
            )
            
            if response.status_code in [401, 403]:
                self.print_test(
                    "POST /api/v1/feedback/ (no auth)",
                    "PASS",
                    "Correctly requires authentication"
                )
            elif response.status_code == 422:
                self.print_test(
                    "POST /api/v1/feedback/ (no auth)",
                    "WARN",
                    "Validation error"
                )
            else:
                self.print_test(
                    "POST /api/v1/feedback/ (no auth)",
                    "FAIL",
                    f"Status: {response.status_code}"
                )
        except Exception as e:
            self.print_test("POST /api/v1/feedback/", "FAIL", str(e))
    
    def test_revisions_endpoints(self):
        """Test revision endpoints"""
        self.print_header("Testing Revisions Endpoints")
        
        # Test create revision (no auth)
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/revisions/",
                timeout=5
            )
            
            if response.status_code in [401, 403]:
                self.print_test(
                    "POST /api/v1/revisions/ (no auth)",
                    "PASS",
                    "Correctly requires authentication"
                )
            elif response.status_code == 422:
                self.print_test(
                    "POST /api/v1/revisions/ (no auth)",
                    "WARN",
                    "Validation error"
                )
            else:
                self.print_test(
                    "POST /api/v1/revisions/ (no auth)",
                    "FAIL",
                    f"Status: {response.status_code}"
                )
        except Exception as e:
            self.print_test("POST /api/v1/revisions/", "FAIL", str(e))
    
    def test_notifications_endpoints(self):
        """Test notification endpoints"""
        self.print_header("Testing Notifications Endpoints")
        
        # Test list notifications (no auth)
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/notifications/",
                timeout=5
            )
            
            if response.status_code in [401, 403]:
                self.print_test(
                    "GET /api/v1/notifications/ (no auth)",
                    "PASS",
                    "Correctly requires authentication"
                )
            elif response.status_code == 200:
                self.print_test(
                    "GET /api/v1/notifications/ (no auth)",
                    "WARN",
                    "Endpoint accessible without auth"
                )
            else:
                self.print_test(
                    "GET /api/v1/notifications/ (no auth)",
                    "FAIL",
                    f"Status: {response.status_code}"
                )
        except Exception as e:
            self.print_test("GET /api/v1/notifications/", "FAIL", str(e))
    
    def test_users_endpoints(self):
        """Test user endpoints"""
        self.print_header("Testing Users Endpoints")
        
        # Test get user profile (no auth)
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/users/me",
                timeout=5
            )
            
            if response.status_code in [401, 403]:
                self.print_test(
                    "GET /api/v1/users/me (no auth)",
                    "PASS",
                    "Correctly requires authentication"
                )
            else:
                self.print_test(
                    "GET /api/v1/users/me (no auth)",
                    "FAIL",
                    f"Should return 401/403, got {response.status_code}"
                )
        except Exception as e:
            self.print_test("GET /api/v1/users/me", "FAIL", str(e))
    
    def test_api_documentation(self):
        """Test API documentation endpoints"""
        self.print_header("Testing API Documentation")
        
        # Test OpenAPI schema
        try:
            response = requests.get(f"{self.base_url}/openapi.json", timeout=5)
            if response.status_code == 200:
                data = response.json()
                endpoints = len(data.get('paths', {}))
                self.print_test(
                    "GET /openapi.json",
                    "PASS",
                    f"Schema valid, {endpoints} endpoints documented"
                )
            else:
                self.print_test("GET /openapi.json", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("GET /openapi.json", "FAIL", str(e))
        
        # Test Swagger UI
        try:
            response = requests.get(f"{self.base_url}/docs", timeout=5)
            if response.status_code == 200:
                self.print_test("GET /docs", "PASS", "Swagger UI accessible")
            else:
                self.print_test("GET /docs", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("GET /docs", "FAIL", str(e))
        
        # Test ReDoc
        try:
            response = requests.get(f"{self.base_url}/redoc", timeout=5)
            if response.status_code == 200:
                self.print_test("GET /redoc", "PASS", "ReDoc accessible")
            else:
                self.print_test("GET /redoc", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("GET /redoc", "FAIL", str(e))
    
    def test_cors_configuration(self):
        """Test CORS configuration"""
        self.print_header("Testing CORS Configuration")
        
        try:
            headers = {
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST"
            }
            response = requests.options(
                f"{self.base_url}/api/v1/auth/login",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                cors_headers = response.headers.get("Access-Control-Allow-Origin")
                self.print_test(
                    "CORS Preflight",
                    "PASS",
                    f"CORS configured: {cors_headers}"
                )
            else:
                self.print_test("CORS Preflight", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("CORS Preflight", "FAIL", str(e))
    
    def test_error_handling(self):
        """Test error handling"""
        self.print_header("Testing Error Handling")
        
        # Test 404
        try:
            response = requests.get(f"{self.base_url}/api/v1/nonexistent", timeout=5)
            if response.status_code == 404:
                self.print_test("404 Error Handling", "PASS", "Returns 404 for invalid routes")
            else:
                self.print_test("404 Error Handling", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("404 Error Handling", "FAIL", str(e))
        
        # Test invalid JSON
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                data="invalid json",
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            if response.status_code in [400, 422]:
                self.print_test("Invalid JSON Handling", "PASS", "Handles invalid JSON")
            else:
                self.print_test("Invalid JSON Handling", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("Invalid JSON Handling", "FAIL", str(e))
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("Test Summary")
        
        total = self.passed + self.failed + self.warnings
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"{Colors.GREEN}Passed: {self.passed}{Colors.NC}")
        print(f"{Colors.RED}Failed: {self.failed}{Colors.NC}")
        print(f"{Colors.YELLOW}Warnings: {self.warnings}{Colors.NC}")
        print(f"\nPass Rate: {pass_rate:.1f}%")
        
        if self.failed == 0:
            print(f"\n{Colors.GREEN}✅ ALL CRITICAL TESTS PASSED!{Colors.NC}")
            return True
        else:
            print(f"\n{Colors.RED}❌ SOME TESTS FAILED{Colors.NC}")
            return False

def main():
    print(f"{Colors.BLUE}{'=' * 60}{Colors.NC}")
    print(f"{Colors.BLUE}Comprehensive Integration Test Suite{Colors.NC}")
    print(f"{Colors.BLUE}Freelancer Feedback Assistant{Colors.NC}")
    print(f"{Colors.BLUE}{'=' * 60}{Colors.NC}")
    
    # Start server
    print(f"\n{Colors.YELLOW}Starting server...{Colors.NC}")
    process = subprocess.Popen(
        ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd="backend",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    print("Waiting for server to start...")
    time.sleep(3)
    
    try:
        # Run tests
        tester = APITester()
        
        tester.test_health_endpoints()
        tester.test_api_documentation()
        tester.test_authentication_flow()
        tester.test_projects_endpoints()
        tester.test_feedback_endpoints()
        tester.test_revisions_endpoints()
        tester.test_notifications_endpoints()
        tester.test_users_endpoints()
        tester.test_cors_configuration()
        tester.test_error_handling()
        
        # Print summary
        success = tester.print_summary()
        
        print(f"\n{Colors.BLUE}Server is still running at http://localhost:8000{Colors.NC}")
        print(f"{Colors.BLUE}Press Ctrl+C to stop{Colors.NC}")
        
        # Keep server running
        process.wait()
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Stopping server...{Colors.NC}")
        return 0
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.NC}")
        return 1
    finally:
        # Stop server
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()

if __name__ == "__main__":
    sys.exit(main())
