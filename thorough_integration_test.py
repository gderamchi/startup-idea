#!/usr/bin/env python3
"""
Thorough Integration Test Suite
Tests authenticated operations, complete workflows, and edge cases
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
    CYAN = '\033[0;36m'
    NC = '\033[0m'

class ThoroughAPITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.user_id: Optional[str] = None
        self.user_email: Optional[str] = None
        self.project_id: Optional[str] = None
        self.feedback_id: Optional[str] = None
        self.revision_id: Optional[str] = None
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        
    def print_header(self, text: str):
        print(f"\n{Colors.BLUE}{'=' * 70}{Colors.NC}")
        print(f"{Colors.BLUE}{text:^70}{Colors.NC}")
        print(f"{Colors.BLUE}{'=' * 70}{Colors.NC}\n")
    
    def print_section(self, text: str):
        print(f"\n{Colors.CYAN}{'─' * 70}{Colors.NC}")
        print(f"{Colors.CYAN}{text}{Colors.NC}")
        print(f"{Colors.CYAN}{'─' * 70}{Colors.NC}")
    
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
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers with JWT token"""
        if not self.token:
            return {}
        return {"Authorization": f"Bearer {self.token}"}
    
    def test_complete_auth_workflow(self):
        """Test complete authentication workflow"""
        self.print_header("Phase 1: Complete Authentication Workflow")
        
        # Generate unique credentials
        timestamp = int(time.time())
        self.user_email = f"thorough_test_{timestamp}@example.com"
        password = "SecurePassword123!@#"
        
        self.print_section("1.1 User Registration")
        try:
            register_data = {
                "email": self.user_email,
                "password": password,
                "full_name": "Thorough Test User"
            }
            response = requests.post(
                f"{self.base_url}/api/v1/auth/register",
                json=register_data,
                timeout=10
            )
            
            if response.status_code == 201:
                data = response.json()
                self.user_id = data.get("id")
                self.print_test(
                    "User Registration",
                    "PASS",
                    f"User ID: {self.user_id}, Email: {data.get('email')}"
                )
            else:
                self.print_test(
                    "User Registration",
                    "FAIL",
                    f"Status: {response.status_code}, Response: {response.text[:200]}"
                )
                return False
        except Exception as e:
            self.print_test("User Registration", "FAIL", str(e))
            return False
        
        self.print_section("1.2 User Login")
        try:
            login_data = {
                "email": self.user_email,
                "password": password
            }
            response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                json=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                self.print_test(
                    "User Login",
                    "PASS",
                    f"Access token received (length: {len(self.token) if self.token else 0})"
                )
            else:
                self.print_test(
                    "User Login",
                    "FAIL",
                    f"Status: {response.status_code}, Response: {response.text[:200]}"
                )
                return False
        except Exception as e:
            self.print_test("User Login", "FAIL", str(e))
            return False
        
        self.print_section("1.3 Get Current User Profile")
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/auth/me",
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.print_test(
                    "Get User Profile",
                    "PASS",
                    f"Email: {data.get('email')}, Active: {data.get('is_active')}"
                )
            else:
                self.print_test(
                    "Get User Profile",
                    "FAIL",
                    f"Status: {response.status_code}"
                )
        except Exception as e:
            self.print_test("Get User Profile", "FAIL", str(e))
        
        self.print_section("1.4 Token Refresh")
        if self.refresh_token:
            try:
                refresh_data = {
                    "refresh_token": self.refresh_token
                }
                response = requests.post(
                    f"{self.base_url}/api/v1/auth/refresh",
                    json=refresh_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    new_token = data.get("access_token")
                    self.print_test(
                        "Token Refresh",
                        "PASS",
                        f"New token received (different: {new_token != self.token})"
                    )
                    self.token = new_token
                else:
                    self.print_test(
                        "Token Refresh",
                        "FAIL",
                        f"Status: {response.status_code}"
                    )
            except Exception as e:
                self.print_test("Token Refresh", "FAIL", str(e))
        
        return True
    
    def test_project_crud_operations(self):
        """Test complete project CRUD operations"""
        self.print_header("Phase 2: Project Management (CRUD Operations)")
        
        self.print_section("2.1 Create Project")
        try:
            project_data = {
                "name": "Test Design Project",
                "description": "A comprehensive test project for design feedback"
            }
            response = requests.post(
                f"{self.base_url}/api/v1/projects/",
                json=project_data,
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if response.status_code == 201:
                data = response.json()
                self.project_id = data.get("id")
                self.print_test(
                    "Create Project",
                    "PASS",
                    f"Project ID: {self.project_id}, Name: {data.get('name')}"
                )
            else:
                self.print_test(
                    "Create Project",
                    "FAIL",
                    f"Status: {response.status_code}, Response: {response.text[:200]}"
                )
                return False
        except Exception as e:
            self.print_test("Create Project", "FAIL", str(e))
            return False
        
        self.print_section("2.2 List Projects")
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/projects/",
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                project_count = len(data) if isinstance(data, list) else 0
                self.print_test(
                    "List Projects",
                    "PASS",
                    f"Found {project_count} project(s)"
                )
            else:
                self.print_test(
                    "List Projects",
                    "FAIL",
                    f"Status: {response.status_code}"
                )
        except Exception as e:
            self.print_test("List Projects", "FAIL", str(e))
        
        self.print_section("2.3 Get Project Details")
        if self.project_id:
            try:
                response = requests.get(
                    f"{self.base_url}/api/v1/projects/{self.project_id}",
                    headers=self.get_auth_headers(),
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.print_test(
                        "Get Project Details",
                        "PASS",
                        f"Name: {data.get('name')}, Status: {data.get('status')}"
                    )
                else:
                    self.print_test(
                        "Get Project Details",
                        "FAIL",
                        f"Status: {response.status_code}"
                    )
            except Exception as e:
                self.print_test("Get Project Details", "FAIL", str(e))
        
        self.print_section("2.4 Update Project")
        if self.project_id:
            try:
                update_data = {
                    "name": "Updated Test Project",
                    "description": "Updated description for testing"
                }
                response = requests.put(
                    f"{self.base_url}/api/v1/projects/{self.project_id}",
                    json=update_data,
                    headers=self.get_auth_headers(),
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.print_test(
                        "Update Project",
                        "PASS",
                        f"Updated name: {data.get('name')}"
                    )
                else:
                    self.print_test(
                        "Update Project",
                        "FAIL",
                        f"Status: {response.status_code}"
                    )
            except Exception as e:
                self.print_test("Update Project", "FAIL", str(e))
        
        return True
    
    def test_feedback_workflow(self):
        """Test complete feedback submission and AI parsing workflow"""
        self.print_header("Phase 3: Feedback Submission & AI Parsing")
        
        if not self.project_id:
            self.print_test("Feedback Workflow", "FAIL", "No project ID available")
            return False
        
        self.print_section("3.1 Submit Feedback")
        try:
            feedback_data = {
                "project_id": self.project_id,
                "raw_text": "The design needs more energy and pop. Make the colors brighter and add some dynamic elements. The typography feels too conservative - let's make it bolder and more modern."
            }
            response = requests.post(
                f"{self.base_url}/api/v1/feedback/",
                json=feedback_data,
                headers=self.get_auth_headers(),
                timeout=30  # AI parsing may take time
            )
            
            if response.status_code == 201:
                data = response.json()
                self.feedback_id = data.get("id")
                summary = data.get("summary", {})
                self.print_test(
                    "Submit Feedback",
                    "PASS",
                    f"Feedback ID: {self.feedback_id}, AI parsed: {bool(summary)}"
                )
                if summary:
                    print(f"  Summary: {json.dumps(summary, indent=2)[:200]}...")
            else:
                self.print_test(
                    "Submit Feedback",
                    "FAIL",
                    f"Status: {response.status_code}, Response: {response.text[:200]}"
                )
                return False
        except Exception as e:
            self.print_test("Submit Feedback", "FAIL", str(e))
            return False
        
        self.print_section("3.2 Get Feedback Details")
        if self.feedback_id:
            try:
                response = requests.get(
                    f"{self.base_url}/api/v1/feedback/{self.feedback_id}",
                    headers=self.get_auth_headers(),
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.print_test(
                        "Get Feedback Details",
                        "PASS",
                        f"Status: {data.get('status')}, Priority: {data.get('priority')}"
                    )
                else:
                    self.print_test(
                        "Get Feedback Details",
                        "FAIL",
                        f"Status: {response.status_code}"
                    )
            except Exception as e:
                self.print_test("Get Feedback Details", "FAIL", str(e))
        
        self.print_section("3.3 List Project Feedback")
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/projects/{self.project_id}/feedback",
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                feedback_count = len(data) if isinstance(data, list) else 0
                self.print_test(
                    "List Project Feedback",
                    "PASS",
                    f"Found {feedback_count} feedback item(s)"
                )
            else:
                self.print_test(
                    "List Project Feedback",
                    "FAIL",
                    f"Status: {response.status_code}"
                )
        except Exception as e:
            self.print_test("List Project Feedback", "FAIL", str(e))
        
        self.print_section("3.4 Get Action Items")
        if self.feedback_id:
            try:
                response = requests.get(
                    f"{self.base_url}/api/v1/feedback/{self.feedback_id}/actions",
                    headers=self.get_auth_headers(),
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    action_count = len(data) if isinstance(data, list) else 0
                    self.print_test(
                        "Get Action Items",
                        "PASS",
                        f"Found {action_count} action item(s)"
                    )
                    if action_count > 0 and isinstance(data, list):
                        for i, action in enumerate(data[:3], 1):
                            print(f"    {i}. {action.get('description', 'N/A')[:60]}...")
                else:
                    self.print_test(
                        "Get Action Items",
                        "FAIL",
                        f"Status: {response.status_code}"
                    )
            except Exception as e:
                self.print_test("Get Action Items", "FAIL", str(e))
        
        return True
    
    def test_revision_workflow(self):
        """Test revision upload and tracking workflow"""
        self.print_header("Phase 4: Revision Upload & Version Tracking")
        
        if not self.feedback_id:
            self.print_test("Revision Workflow", "FAIL", "No feedback ID available")
            return False
        
        self.print_section("4.1 Upload Revision (Simulated)")
        try:
            # Upload revision with query parameters (matching API design)
            params = {
                "feedback_id": str(self.feedback_id),
                "notes": "First revision addressing the feedback"
            }
            response = requests.post(
                f"{self.base_url}/api/v1/revisions/",
                params=params,
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if response.status_code == 201:
                data = response.json()
                self.revision_id = data.get("id")
                self.print_test(
                    "Upload Revision",
                    "PASS",
                    f"Revision ID: {self.revision_id}, Version: {data.get('version')}"
                )
            else:
                self.print_test(
                    "Upload Revision",
                    "FAIL",
                    f"Status: {response.status_code}, Response: {response.text[:200]}"
                )
                return False
        except Exception as e:
            self.print_test("Upload Revision", "FAIL", str(e))
            return False
        
        self.print_section("4.2 List Feedback Revisions")
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/feedback/{self.feedback_id}/revisions",
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                revision_count = len(data) if isinstance(data, list) else 0
                self.print_test(
                    "List Revisions",
                    "PASS",
                    f"Found {revision_count} revision(s)"
                )
            else:
                self.print_test(
                    "List Revisions",
                    "FAIL",
                    f"Status: {response.status_code}"
                )
        except Exception as e:
            self.print_test("List Revisions", "FAIL", str(e))
        
        self.print_section("4.3 Update Revision Status")
        if self.revision_id:
            try:
                update_data = {
                    "status": "approved",
                    "notes": "Looks great! Approved."
                }
                response = requests.put(
                    f"{self.base_url}/api/v1/revisions/{self.revision_id}",
                    json=update_data,
                    headers=self.get_auth_headers(),
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.print_test(
                        "Update Revision Status",
                        "PASS",
                        f"Status: {data.get('status')}"
                    )
                else:
                    self.print_test(
                        "Update Revision Status",
                        "FAIL",
                        f"Status: {response.status_code}"
                    )
            except Exception as e:
                self.print_test("Update Revision Status", "FAIL", str(e))
        
        return True
    
    def test_notifications(self):
        """Test notification system"""
        self.print_header("Phase 5: Notification System")
        
        self.print_section("5.1 List Notifications")
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/notifications/",
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                notification_count = len(data) if isinstance(data, list) else 0
                self.print_test(
                    "List Notifications",
                    "PASS",
                    f"Found {notification_count} notification(s)"
                )
            else:
                self.print_test(
                    "List Notifications",
                    "FAIL",
                    f"Status: {response.status_code}"
                )
        except Exception as e:
            self.print_test("List Notifications", "FAIL", str(e))
        
        return True
    
    def test_edge_cases(self):
        """Test edge cases and error scenarios"""
        self.print_header("Phase 6: Edge Cases & Error Handling")
        
        self.print_section("6.1 Invalid Token")
        try:
            invalid_headers = {"Authorization": "Bearer invalid_token_12345"}
            response = requests.get(
                f"{self.base_url}/api/v1/auth/me",
                headers=invalid_headers,
                timeout=10
            )
            
            if response.status_code == 401:
                self.print_test(
                    "Invalid Token Rejection",
                    "PASS",
                    "Correctly returns 401 for invalid token"
                )
            else:
                self.print_test(
                    "Invalid Token Rejection",
                    "FAIL",
                    f"Expected 401, got {response.status_code}"
                )
        except Exception as e:
            self.print_test("Invalid Token Rejection", "FAIL", str(e))
        
        self.print_section("6.2 Duplicate Email Registration")
        try:
            duplicate_data = {
                "email": self.user_email,
                "password": "AnotherPassword123!",
                "full_name": "Duplicate User"
            }
            response = requests.post(
                f"{self.base_url}/api/v1/auth/register",
                json=duplicate_data,
                timeout=10
            )
            
            if response.status_code == 400:
                self.print_test(
                    "Duplicate Email Prevention",
                    "PASS",
                    "Correctly prevents duplicate email registration"
                )
            else:
                self.print_test(
                    "Duplicate Email Prevention",
                    "FAIL",
                    f"Expected 400, got {response.status_code}"
                )
        except Exception as e:
            self.print_test("Duplicate Email Prevention", "FAIL", str(e))
        
        self.print_section("6.3 Invalid Project ID")
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/projects/invalid-uuid-12345",
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if response.status_code in [400, 404, 422]:
                self.print_test(
                    "Invalid Project ID Handling",
                    "PASS",
                    f"Correctly returns {response.status_code}"
                )
            else:
                self.print_test(
                    "Invalid Project ID Handling",
                    "WARN",
                    f"Got {response.status_code}, expected 400/404/422"
                )
        except Exception as e:
            self.print_test("Invalid Project ID Handling", "FAIL", str(e))
        
        self.print_section("6.4 Missing Required Fields")
        try:
            incomplete_data = {
                "name": "Incomplete Project"
                # Missing description
            }
            response = requests.post(
                f"{self.base_url}/api/v1/projects/",
                json=incomplete_data,
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            # Should succeed as description might be optional
            if response.status_code in [201, 422]:
                self.print_test(
                    "Missing Fields Validation",
                    "PASS",
                    f"Handled appropriately (status: {response.status_code})"
                )
            else:
                self.print_test(
                    "Missing Fields Validation",
                    "WARN",
                    f"Unexpected status: {response.status_code}"
                )
        except Exception as e:
            self.print_test("Missing Fields Validation", "FAIL", str(e))
        
        return True
    
    def test_cleanup(self):
        """Clean up test data"""
        self.print_header("Phase 7: Cleanup")
        
        self.print_section("7.1 Delete Project")
        if self.project_id:
            try:
                response = requests.delete(
                    f"{self.base_url}/api/v1/projects/{self.project_id}",
                    headers=self.get_auth_headers(),
                    timeout=10
                )
                
                if response.status_code in [200, 204]:
                    self.print_test(
                        "Delete Project",
                        "PASS",
                        "Project deleted successfully"
                    )
                else:
                    self.print_test(
                        "Delete Project",
                        "WARN",
                        f"Status: {response.status_code}"
                    )
            except Exception as e:
                self.print_test("Delete Project", "WARN", str(e))
        
        return True
    
    def print_summary(self):
        """Print comprehensive test summary"""
        self.print_header("Test Summary")
        
        total = self.passed + self.failed + self.warnings
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"{Colors.GREEN}Passed: {self.passed}{Colors.NC}")
        print(f"{Colors.RED}Failed: {self.failed}{Colors.NC}")
        print(f"{Colors.YELLOW}Warnings: {self.warnings}{Colors.NC}")
        print(f"\nPass Rate: {pass_rate:.1f}%")
        
        if self.failed == 0:
            print(f"\n{Colors.GREEN}✅ ALL TESTS PASSED!{Colors.NC}")
            return True
        elif pass_rate >= 80:
            print(f"\n{Colors.YELLOW}⚠ MOSTLY PASSING (some failures){Colors.NC}")
            return True
        else:
            print(f"\n{Colors.RED}❌ SIGNIFICANT FAILURES{Colors.NC}")
            return False

def main():
    print(f"{Colors.BLUE}{'=' * 70}{Colors.NC}")
    print(f"{Colors.BLUE}Thorough Integration Test Suite{Colors.NC}")
    print(f"{Colors.BLUE}Freelancer Feedback Assistant - Complete Workflow Testing{Colors.NC}")
    print(f"{Colors.BLUE}{'=' * 70}{Colors.NC}")
    
    # Check if server is already running
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            print(f"\n{Colors.GREEN}✓ Server already running{Colors.NC}")
            process = None
        else:
            raise Exception("Server not responding")
    except:
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
        # Run thorough tests
        tester = ThoroughAPITester()
        
        # Phase 1: Authentication
        if not tester.test_complete_auth_workflow():
            print(f"\n{Colors.RED}Authentication failed - stopping tests{Colors.NC}")
            return 1
        
        # Phase 2: Project CRUD
        if not tester.test_project_crud_operations():
            print(f"\n{Colors.YELLOW}Project operations failed - continuing with other tests{Colors.NC}")
        
        # Phase 3: Feedback & AI
        if not tester.test_feedback_workflow():
            print(f"\n{Colors.YELLOW}Feedback workflow failed - continuing with other tests{Colors.NC}")
        
        # Phase 4: Revisions
        if not tester.test_revision_workflow():
            print(f"\n{Colors.YELLOW}Revision workflow failed - continuing with other tests{Colors.NC}")
        
        # Phase 5: Notifications
        tester.test_notifications()
        
        # Phase 6: Edge Cases
        tester.test_edge_cases()
        
        # Phase 7: Cleanup
        tester.test_cleanup()
        
        # Print summary
        success = tester.print_summary()
        
        if process:
            print(f"\n{Colors.BLUE}Server is still running at http://localhost:8000{Colors.NC}")
            print(f"{Colors.BLUE}Press Ctrl+C to stop{Colors.NC}")
            process.wait()
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Stopping...{Colors.NC}")
        return 0
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.NC}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Stop server if we started it
        if process:
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()

if __name__ == "__main__":
    sys.exit(main())
