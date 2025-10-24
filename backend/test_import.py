"""Test if we can import the app without errors"""
import sys
import os

# Set minimal environment variables
os.environ['DATABASE_URL'] = 'sqlite:///./test.db'
os.environ['SECRET_KEY'] = 'test-secret-key-min-32-characters-long'
os.environ['OPENAI_API_KEY'] = 'sk-test-key'
os.environ['ALLOWED_ORIGINS'] = 'http://localhost:3000'
os.environ['ENVIRONMENT'] = 'testing'

try:
    from app.core.config import settings
    print("✓ Config loaded successfully")
    print(f"  Database: {settings.DATABASE_URL}")
    print(f"  Environment: {settings.ENVIRONMENT}")
    print(f"  CORS Origins: {settings.ALLOWED_ORIGINS}")
    
    from app.db.session import engine
    print("✓ Database session imported")
    
    from app.models import User, Project, Feedback
    print("✓ Models imported successfully")
    
    from app.main import app
    print("✓ FastAPI app imported successfully")
    
    print("\n✅ All imports successful!")
    sys.exit(0)
    
except Exception as e:
    print(f"\n❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
