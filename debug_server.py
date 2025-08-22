#!/usr/bin/env python3
"""
Debug script to test server startup and identify issues.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test if all imports work."""
    print("Testing imports...")
    try:
        from app.main import app
        print("✅ App imports successfully")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_database():
    """Test database connection."""
    print("Testing database...")
    try:
        from app.models.database import engine
        from app.main import init_db
        init_db()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_health_endpoint():
    """Test health endpoint directly."""
    print("Testing health endpoint...")
    try:
        from app.routers.monitoring import get_system_health
        import asyncio
        
        result = asyncio.run(get_system_health())
        print(f"✅ Health endpoint works: {result}")
        return True
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

def main():
    """Run all tests."""
    print("🔍 Debugging Server Issues")
    print("=" * 40)
    
    if not test_imports():
        return
    
    if not test_database():
        return
    
    if not test_health_endpoint():
        return
    
    print("\n✅ All tests passed! Server should work.")

if __name__ == "__main__":
    main()
