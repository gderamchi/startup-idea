#!/usr/bin/env python3
"""
Quick server test - starts server and tests it
"""
import subprocess
import time
import requests
import sys

def test_server():
    print("=" * 60)
    print("Testing Freelancer Feedback Assistant Server")
    print("=" * 60)
    
    # Start server in background
    print("\n1. Starting server...")
    process = subprocess.Popen(
        ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd="backend",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for server to start
    print("   Waiting for server to start...")
    time.sleep(3)
    
    try:
        # Test health endpoint
        print("\n2. Testing health endpoint...")
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            print("   ✓ Health check passed")
        else:
            print("   ✗ Health check failed")
            return False
        
        # Test API docs
        print("\n3. Testing API documentation...")
        response = requests.get("http://localhost:8000/docs", timeout=5)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✓ API docs accessible")
        else:
            print("   ✗ API docs failed")
            return False
        
        # Test OpenAPI schema
        print("\n4. Testing OpenAPI schema...")
        response = requests.get("http://localhost:8000/openapi.json", timeout=5)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   API Title: {data.get('info', {}).get('title')}")
            print(f"   API Version: {data.get('info', {}).get('version')}")
            print(f"   Endpoints: {len(data.get('paths', {}))}")
            print("   ✓ OpenAPI schema valid")
        else:
            print("   ✗ OpenAPI schema failed")
            return False
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nServer is running at:")
        print("  • API: http://localhost:8000")
        print("  • Docs: http://localhost:8000/docs")
        print("  • Health: http://localhost:8000/health")
        print("\nPress Ctrl+C to stop the server")
        
        # Keep server running
        process.wait()
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("\n✗ Could not connect to server")
        print("   Server may not have started properly")
        return False
    except KeyboardInterrupt:
        print("\n\nStopping server...")
        return True
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        return False
    finally:
        # Stop server
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()

if __name__ == "__main__":
    success = test_server()
    sys.exit(0 if success else 1)
