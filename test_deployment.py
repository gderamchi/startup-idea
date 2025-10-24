#!/usr/bin/env python3
"""
Deployment Readiness Test Script
Tests all critical components before deployment
"""

import os
import sys
import json
from pathlib import Path

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text:^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    print(f"{RED}✗ {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}⚠ {text}{RESET}")

def print_info(text):
    print(f"{BLUE}ℹ {text}{RESET}")

class DeploymentTester:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.errors = []
        self.warnings = []
        self.passed = []

    def test_file_structure(self):
        """Test that all required files exist"""
        print_header("Testing File Structure")
        
        required_files = [
            # Root files
            "README.md",
            "docker-compose.yml",
            "Makefile",
            ".gitignore",
            
            # Backend files
            "backend/Dockerfile",
            "backend/requirements.txt",
            "backend/requirements-dev.txt",
            "backend/alembic.ini",
            "backend/app/main.py",
            "backend/app/core/config.py",
            "backend/app/core/security.py",
            "backend/app/services/ai_service.py",
            "backend/app/db/session.py",
            
            # Frontend files
            "frontend/package.json",
            "frontend/vite.config.ts",
            "frontend/tsconfig.json",
            "frontend/Dockerfile",
            "frontend/src/main.tsx",
            
            # Infrastructure
            "infra/terraform",
            ".github/workflows",
            
            # Documentation
            "BLACKBOX_API_SETUP.md",
            "QUICK_START_BLACKBOX.md",
            "IMPLEMENTATION_PLAN.md",
        ]
        
        for file_path in required_files:
            full_path = self.root_dir / file_path
            if full_path.exists():
                print_success(f"Found: {file_path}")
                self.passed.append(f"File exists: {file_path}")
            else:
                print_error(f"Missing: {file_path}")
                self.errors.append(f"Missing file: {file_path}")

    def test_backend_config(self):
        """Test backend configuration"""
        print_header("Testing Backend Configuration")
        
        # Check if config.py has BLACKBOX_API_KEY
        config_path = self.root_dir / "backend/app/core/config.py"
        if config_path.exists():
            content = config_path.read_text()
            
            if "BLACKBOX_API_KEY" in content:
                print_success("BLACKBOX_API_KEY configured in settings")
                self.passed.append("BLACKBOX_API_KEY in config")
            else:
                print_error("BLACKBOX_API_KEY not found in config")
                self.errors.append("BLACKBOX_API_KEY missing from config")
            
            if "https://api.blackbox.ai/v1" in content:
                print_success("Blackbox API endpoint configured")
                self.passed.append("Blackbox API endpoint set")
            else:
                print_error("Blackbox API endpoint not configured")
                self.errors.append("Blackbox API endpoint missing")
            
            if "blackboxai-pro" in content:
                print_success("Blackbox AI model configured")
                self.passed.append("Blackbox AI model set")
            else:
                print_warning("Default model might not be blackboxai-pro")
                self.warnings.append("Check model configuration")
        else:
            print_error("config.py not found")
            self.errors.append("config.py missing")

    def test_ai_service(self):
        """Test AI service configuration"""
        print_header("Testing AI Service")
        
        ai_service_path = self.root_dir / "backend/app/services/ai_service.py"
        if ai_service_path.exists():
            content = ai_service_path.read_text()
            
            if "BLACKBOX_API_KEY" in content:
                print_success("AI service uses BLACKBOX_API_KEY")
                self.passed.append("AI service configured for Blackbox")
            else:
                print_error("AI service not using BLACKBOX_API_KEY")
                self.errors.append("AI service config incorrect")
            
            if "base_url" in content and "blackbox.ai" in content:
                print_success("AI service points to Blackbox endpoint")
                self.passed.append("AI service endpoint correct")
            else:
                print_error("AI service endpoint not configured")
                self.errors.append("AI service endpoint missing")
        else:
            print_error("ai_service.py not found")
            self.errors.append("ai_service.py missing")

    def test_docker_config(self):
        """Test Docker configuration"""
        print_header("Testing Docker Configuration")
        
        # Check docker-compose.yml
        compose_path = self.root_dir / "docker-compose.yml"
        if compose_path.exists():
            content = compose_path.read_text()
            
            services = ["postgres", "redis", "backend", "frontend", "celery-worker"]
            for service in services:
                if f"{service}:" in content:
                    print_success(f"Service defined: {service}")
                    self.passed.append(f"Docker service: {service}")
                else:
                    print_warning(f"Service might be missing: {service}")
                    self.warnings.append(f"Check service: {service}")
        else:
            print_error("docker-compose.yml not found")
            self.errors.append("docker-compose.yml missing")
        
        # Check Dockerfiles
        backend_dockerfile = self.root_dir / "backend/Dockerfile"
        frontend_dockerfile = self.root_dir / "frontend/Dockerfile"
        
        if backend_dockerfile.exists():
            print_success("Backend Dockerfile exists")
            self.passed.append("Backend Dockerfile present")
        else:
            print_error("Backend Dockerfile missing")
            self.errors.append("Backend Dockerfile missing")
        
        if frontend_dockerfile.exists():
            print_success("Frontend Dockerfile exists")
            self.passed.append("Frontend Dockerfile present")
        else:
            print_error("Frontend Dockerfile missing")
            self.errors.append("Frontend Dockerfile missing")

    def test_dependencies(self):
        """Test dependency files"""
        print_header("Testing Dependencies")
        
        # Backend dependencies
        req_path = self.root_dir / "backend/requirements.txt"
        if req_path.exists():
            content = req_path.read_text()
            required_packages = [
                "fastapi",
                "sqlalchemy",
                "alembic",
                "pydantic",
                "openai",
                "celery",
                "redis"
            ]
            
            for package in required_packages:
                if package in content.lower():
                    print_success(f"Backend dependency: {package}")
                    self.passed.append(f"Dependency: {package}")
                else:
                    print_warning(f"Might be missing: {package}")
                    self.warnings.append(f"Check dependency: {package}")
        else:
            print_error("requirements.txt not found")
            self.errors.append("requirements.txt missing")
        
        # Frontend dependencies
        package_path = self.root_dir / "frontend/package.json"
        if package_path.exists():
            try:
                with open(package_path) as f:
                    package_data = json.load(f)
                
                deps = package_data.get("dependencies", {})
                required_deps = ["react", "react-dom", "react-router-dom", "axios"]
                
                for dep in required_deps:
                    if dep in deps:
                        print_success(f"Frontend dependency: {dep}")
                        self.passed.append(f"Frontend dep: {dep}")
                    else:
                        print_warning(f"Might be missing: {dep}")
                        self.warnings.append(f"Check frontend dep: {dep}")
            except json.JSONDecodeError:
                print_error("Invalid package.json")
                self.errors.append("Invalid package.json")
        else:
            print_error("package.json not found")
            self.errors.append("package.json missing")

    def test_documentation(self):
        """Test documentation completeness"""
        print_header("Testing Documentation")
        
        docs = [
            "README.md",
            "BLACKBOX_API_SETUP.md",
            "QUICK_START_BLACKBOX.md",
            "IMPLEMENTATION_PLAN.md",
        ]
        
        for doc in docs:
            doc_path = self.root_dir / doc
            if doc_path.exists():
                size = doc_path.stat().st_size
                if size > 1000:  # At least 1KB
                    print_success(f"Documentation: {doc} ({size} bytes)")
                    self.passed.append(f"Doc complete: {doc}")
                else:
                    print_warning(f"Documentation might be incomplete: {doc}")
                    self.warnings.append(f"Check doc: {doc}")
            else:
                print_error(f"Documentation missing: {doc}")
                self.errors.append(f"Missing doc: {doc}")

    def test_api_structure(self):
        """Test API endpoint structure"""
        print_header("Testing API Structure")
        
        endpoints_dir = self.root_dir / "backend/app/api/v1/endpoints"
        if endpoints_dir.exists():
            endpoint_files = [
                "auth.py",
                "projects.py",
                "feedback.py",
                "revisions.py",
                "users.py",
                "notifications.py"
            ]
            
            for endpoint in endpoint_files:
                endpoint_path = endpoints_dir / endpoint
                if endpoint_path.exists():
                    print_success(f"Endpoint module: {endpoint}")
                    self.passed.append(f"Endpoint: {endpoint}")
                else:
                    print_error(f"Endpoint missing: {endpoint}")
                    self.errors.append(f"Missing endpoint: {endpoint}")
        else:
            print_error("Endpoints directory not found")
            self.errors.append("Endpoints directory missing")

    def test_database_models(self):
        """Test database models"""
        print_header("Testing Database Models")
        
        models_dir = self.root_dir / "backend/app/models"
        if models_dir.exists():
            model_files = [
                "user.py",
                "project.py",
                "feedback.py",
                "revision.py",
                "action_item.py",
                "notification.py"
            ]
            
            for model in model_files:
                model_path = models_dir / model
                if model_path.exists():
                    print_success(f"Model: {model}")
                    self.passed.append(f"Model: {model}")
                else:
                    print_error(f"Model missing: {model}")
                    self.errors.append(f"Missing model: {model}")
        else:
            print_error("Models directory not found")
            self.errors.append("Models directory missing")

    def generate_report(self):
        """Generate final report"""
        print_header("Deployment Readiness Report")
        
        total_tests = len(self.passed) + len(self.errors) + len(self.warnings)
        
        print(f"\n{BLUE}Summary:{RESET}")
        print(f"  {GREEN}Passed: {len(self.passed)}{RESET}")
        print(f"  {RED}Errors: {len(self.errors)}{RESET}")
        print(f"  {YELLOW}Warnings: {len(self.warnings)}{RESET}")
        print(f"  Total Checks: {total_tests}")
        
        if self.errors:
            print(f"\n{RED}Critical Issues:{RESET}")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print(f"\n{YELLOW}Warnings:{RESET}")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        # Calculate readiness score
        if total_tests > 0:
            score = (len(self.passed) / total_tests) * 100
            print(f"\n{BLUE}Deployment Readiness Score: {score:.1f}%{RESET}")
            
            if score >= 90:
                print(f"\n{GREEN}✓ READY FOR DEPLOYMENT{RESET}")
                return True
            elif score >= 70:
                print(f"\n{YELLOW}⚠ MOSTLY READY - Review warnings{RESET}")
                return True
            else:
                print(f"\n{RED}✗ NOT READY - Fix critical issues{RESET}")
                return False
        
        return False

    def run_all_tests(self):
        """Run all deployment tests"""
        print_header("Freelancer Feedback Assistant - Deployment Test")
        print_info("Testing deployment readiness...")
        
        self.test_file_structure()
        self.test_backend_config()
        self.test_ai_service()
        self.test_docker_config()
        self.test_dependencies()
        self.test_documentation()
        self.test_api_structure()
        self.test_database_models()
        
        ready = self.generate_report()
        
        return 0 if ready else 1

def main():
    tester = DeploymentTester()
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
