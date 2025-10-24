#!/usr/bin/env python3
"""
Test password hashing with the fix
"""
import sys
sys.path.insert(0, 'backend')

from app.core.security import get_password_hash, verify_password

# Test password
test_password = "TestPassword123!"

print(f"Testing password: {test_password}")
print(f"Password length: {len(test_password)} characters")
print(f"Password bytes: {len(test_password.encode('utf-8'))} bytes")

try:
    # Hash the password
    hashed = get_password_hash(test_password)
    print(f"✓ Password hashed successfully")
    print(f"Hash: {hashed[:50]}...")
    
    # Verify the password
    is_valid = verify_password(test_password, hashed)
    print(f"✓ Password verification: {is_valid}")
    
    if is_valid:
        print("\n✓ Password hashing and verification working correctly!")
    else:
        print("\n✗ Password verification failed!")
        
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
