#!/usr/bin/env python3
"""
Simple startup script for llm-bencher.

This script starts the FastAPI server and provides easy access to test the API.
"""

import subprocess
import sys
import os
import time
import requests

def start_server():
    """Start the FastAPI server."""
    print("🚀 Starting llm-bencher Server...")
    print("=" * 50)
    
    # Change to backend directory
    backend_dir = os.path.join(os.path.dirname(__file__), "backend")
    os.chdir(backend_dir)
    
    # Activate virtual environment and start server
    try:
        # Start the server
        print("Starting uvicorn server...")
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "127.0.0.1", 
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

def test_server():
    """Test if the server is running."""
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running!")
            print(f"📊 Health check: {response.json()}")
            return True
        else:
            print(f"❌ Server responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running")
        return False
    except Exception as e:
        print(f"❌ Error testing server: {e}")
        return False

def show_info():
    """Show information about the API."""
    print("\n📚 API Information:")
    print("- Health Check: http://127.0.0.1:8000/health")
    print("- API Docs: http://127.0.0.1:8000/docs")
    print("- Root: http://127.0.0.1:8000/")
    print("\n🔧 Available Endpoints:")
    print("- GET /api/v1/conversations - List conversations")
    print("- POST /api/v1/conversations - Create conversation")
    print("- GET /api/v1/llm/services - List LLM services")
    print("- POST /api/v1/llm/generate - Generate LLM response")
    print("- GET /api/v1/monitoring/health - System health")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Just test if server is running
        test_server()
    else:
        # Start the server
        start_server()
