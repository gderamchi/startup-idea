#!/usr/bin/env python3
"""
Debug authentication endpoints to see actual errors
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("Testing authentication endpoints with detailed error info...\n")

# Test registration
print("1. Testing POST /api/v1/auth/register")
register_data = {
    "email": "test@example.com",
    "password": "TestPassword123!",
    "full_name": "Test User"
}

try:
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/register",
        json=register_data,
        timeout=10
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*60 + "\n")

# Test login
print("2. Testing POST /api/v1/auth/login")
login_data = {
    "email": "test@example.com",
    "password": "password123"
}

try:
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json=login_data,
        timeout=10
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
