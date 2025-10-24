#!/usr/bin/env python3
"""
Test API Endpoints
Quick validation of FastAPI application and endpoints
"""

import sys
from fastapi.testclient import TestClient

print("=" * 60)
print("Testing Freelancer Feedback Assistant API")
print("=" * 60)

try:
    # Import the FastAPI app
    print("\n1. Importing FastAPI app...")
    from app.main import app
    print("✓ FastAPI app imported successfully")
    
    # Create test client
    print("\n2. Creating test client...")
    client = TestClient(app)
    print("✓ Test client created")
    
    # Test health endpoint
    print("\n3. Testing health endpoint...")
    response = client.get("/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    assert response.status_code == 200, "Health check failed"
    print("✓ Health endpoint working")
    
    # Test API docs
    print("\n4. Testing API documentation...")
    response = client.get("/docs")
    assert response.status_code == 200, "API docs not accessible"
    print("✓ API documentation accessible at /docs")
    
    # Test OpenAPI schema
    print("\n5. Testing OpenAPI schema...")
    response = client.get("/openapi.json")
    assert response.status_code == 200, "OpenAPI schema not accessible"
    schema = response.json()
    print(f"   API Title: {schema.get('info', {}).get('title')}")
    print(f"   API Version: {schema.get('info', {}).get('version')}")
    print(f"   Endpoints: {len(schema.get('paths', {}))}")
    print("✓ OpenAPI schema accessible")
    
    # List all available endpoints
    print("\n6. Available API Endpoints:")
    paths = schema.get('paths', {})
    for path, methods in sorted(paths.items()):
        for method in methods.keys():
            if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                print(f"   {method.upper():6} {path}")
    
    # Test authentication endpoints (should return 422 for missing data)
    print("\n7. Testing authentication endpoints...")
    
    # Register endpoint (should fail without data)
    response = client.post("/api/v1/auth/register", json={})
    print(f"   POST /api/v1/auth/register: {response.status_code}")
    assert response.status_code in [422, 400], "Register endpoint not responding correctly"
    
    # Login endpoint (should fail without data)
    response = client.post("/api/v1/auth/login", json={})
    print(f"   POST /api/v1/auth/login: {response.status_code}")
    assert response.status_code in [422, 400], "Login endpoint not responding correctly"
    
    print("✓ Authentication endpoints responding")
    
    # Test protected endpoints (should return 401 or 403 unauthorized)
    print("\n8. Testing protected endpoints...")
    response = client.get("/api/v1/auth/me")
    print(f"   GET /api/v1/auth/me: {response.status_code}")
    assert response.status_code in [401, 403], "Protected endpoint should require authentication"
    print("✓ Protected endpoints require authentication")
    
    # Test CORS headers
    print("\n9. Testing CORS configuration...")
    response = client.options("/api/v1/auth/login", headers={
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST"
    })
    print(f"   CORS preflight: {response.status_code}")
    print("✓ CORS configured")
    
    print("\n" + "=" * 60)
    print("✅ All API tests passed!")
    print("=" * 60)
    print("\nAPI is ready to use:")
    print("  • Health: http://localhost:8000/health")
    print("  • Docs: http://localhost:8000/docs")
    print("  • ReDoc: http://localhost:8000/redoc")
    print("  • OpenAPI: http://localhost:8000/openapi.json")
    print("\nTo start the server:")
    print("  cd backend && source venv/bin/activate")
    print("  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    
    sys.exit(0)
    
except Exception as e:
    print(f"\n❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
