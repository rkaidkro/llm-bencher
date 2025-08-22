#!/usr/bin/env python3
"""
Simple server script that should work reliably.
"""

import sys
import os
import uvicorn

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def main():
    """Start the server."""
    print("🚀 Starting llm-bencher Server...")
    print("=" * 50)
    
    try:
        # Import and initialize
        from app.main import app, init_db
        
        # Initialize database
        print("📊 Initializing database...")
        init_db()
        print("✅ Database ready")
        
        # Start server
        print("🌐 Starting server on http://127.0.0.1:8000")
        print("📚 API docs: http://127.0.0.1:8000/docs")
        print("🏥 Health check: http://127.0.0.1:8000/health")
        print()
        print("Press Ctrl+C to stop the server")
        print("=" * 50)
        
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            log_level="info",
            reload=False
        )
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
