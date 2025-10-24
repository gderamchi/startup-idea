#!/usr/bin/env python3
"""
Verify Project Setup
Checks that all critical files and dependencies are in place
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def check_file_exists(filepath: str) -> bool:
    """Check if a file exists"""
    return Path(filepath).exists()

def check_directory_exists(dirpath: str) -> bool:
    """Check if a directory exists"""
    return Path(dirpath).is_dir()

def print_status(message: str, status: bool):
    """Print colored status message"""
    symbol = f"{Colors.GREEN}✓{Colors.END}" if status else f"{Colors.RED}✗{Colors.END}"
    print(f"{symbol} {message}")

def main():
    """Run all verification checks"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Freelancer Feedback Assistant - Setup Verification{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    all_checks_passed = True
    
    # Critical Backend Files
    print(f"{Colors.YELLOW}Backend Files:{Colors.END}")
    backend_files = [
        "backend/app/main.py",
        "backend/app/core/config.py",
        "backend/app/core/security.py",
        "backend/app/db/session.py",
        "backend/app/models/user.py",
        "backend/app/models/project.py",
        "backend/app/models/feedback.py",
        "backend/app/api/v1/api.py",
        "backend/app/api/v1/endpoints/auth.py",
        "backend/app/services/ai_service.py",
        "backend/requirements.txt",
        "backend/Dockerfile",
        "backend/alembic.ini",
    ]
    
    for file in backend_files:
        exists = check_file_exists(file)
        print_status(file, exists)
        if not exists:
            all_checks_passed = False
    
    # Critical Frontend Files
    print(f"\n{Colors.YELLOW}Frontend Files:{Colors.END}")
    frontend_files = [
        "frontend/package.json",
        "frontend/vite.config.ts",
        "frontend/tsconfig.json",
        "frontend/src/main.tsx",
        "frontend/src/App.tsx",
        "frontend/src/contexts/AuthContext.tsx",
        "frontend/src/services/api.ts",
        "frontend/src/pages/Login.tsx",
        "frontend/src/pages/Dashboard.tsx",
        "frontend/Dockerfile",
    ]
    
    for file in frontend_files:
        exists = check_file_exists(file)
        print_status(file, exists)
        if not exists:
            all_checks_passed = False
    
    # Configuration Files
    print(f"\n{Colors.YELLOW}Configuration Files:{Colors.END}")
    config_files = [
        ".env.example",
        ".gitignore",
        "docker-compose.yml",
        "Makefile",
        "README.md",
        "IMPLEMENTATION_PLAN.md",
        "TODO.md",
        "PROJECT_SUMMARY.md",
    ]
    
    for file in config_files:
        exists = check_file_exists(file)
        print_status(file, exists)
        if not exists:
            all_checks_passed = False
    
    # Directory Structure
    print(f"\n{Colors.YELLOW}Directory Structure:{Colors.END}")
    directories = [
        "backend/app/api/v1/endpoints",
        "backend/app/core",
        "backend/app/db",
        "backend/app/models",
        "backend/app/schemas",
        "backend/app/services",
        "backend/alembic",
        "frontend/src/components",
        "frontend/src/contexts",
        "frontend/src/pages",
        "frontend/src/services",
        "infra/terraform",
        "infra/docker",
    ]
    
    for directory in directories:
        exists = check_directory_exists(directory)
        print_status(directory, exists)
        if not exists:
            all_checks_passed = False
    
    # Count files
    print(f"\n{Colors.YELLOW}Statistics:{Colors.END}")
    
    backend_py_files = len(list(Path("backend").rglob("*.py")))
    frontend_tsx_files = len(list(Path("frontend/src").rglob("*.tsx"))) if Path("frontend/src").exists() else 0
    frontend_ts_files = len(list(Path("frontend/src").rglob("*.ts"))) if Path("frontend/src").exists() else 0
    
    print(f"  Backend Python files: {backend_py_files}")
    print(f"  Frontend TypeScript files: {frontend_tsx_files + frontend_ts_files}")
    print(f"  Total project files: {backend_py_files + frontend_tsx_files + frontend_ts_files}")
    
    # Final Summary
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    if all_checks_passed:
        print(f"{Colors.GREEN}✓ All checks passed! Project setup is complete.{Colors.END}")
        print(f"\n{Colors.YELLOW}Next Steps:{Colors.END}")
        print("1. Set up environment variables:")
        print("   cp .env.example .env")
        print("   cp backend/.env.example backend/.env")
        print("   cp frontend/.env.example frontend/.env")
        print("\n2. Start with Docker:")
        print("   docker-compose up -d")
        print("\n3. Or use Makefile:")
        print("   make setup")
        print("   make dev")
        print("\n4. Access the application:")
        print("   Frontend: http://localhost:3000")
        print("   Backend: http://localhost:8000")
        print("   API Docs: http://localhost:8000/docs")
    else:
        print(f"{Colors.RED}✗ Some checks failed. Please review the output above.{Colors.END}")
        sys.exit(1)
    
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")

if __name__ == "__main__":
    main()
