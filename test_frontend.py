#!/usr/bin/env python3
"""
Test script for the React frontend.

This script tests if the frontend is running and accessible.
"""

import requests
import time
import subprocess
import sys
import os

def test_frontend():
    """Test if the frontend is accessible."""
    print("🧪 Testing Frontend")
    print("=" * 40)
    
    try:
        # Test if frontend is running
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is running on http://localhost:3000")
            return True
        else:
            print(f"❌ Frontend responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Frontend is not running")
        return False
    except Exception as e:
        print(f"❌ Error testing frontend: {e}")
        return False

def start_frontend():
    """Start the frontend development server."""
    print("🚀 Starting Frontend Development Server...")
    print("=" * 50)
    
    frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
    
    try:
        # Change to frontend directory and start server
        process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Frontend server started successfully")
            print("📱 Frontend URL: http://localhost:3000")
            print("🔗 API Proxy: /api -> http://127.0.0.1:8000")
            print()
            print("Press Ctrl+C to stop the server")
            
            try:
                # Keep the process running
                process.wait()
            except KeyboardInterrupt:
                print("\n👋 Stopping frontend server...")
                process.terminate()
                process.wait()
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Frontend server failed to start")
            print(f"Error: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        return False

def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Just test if frontend is running
        test_frontend()
    else:
        # Start the frontend
        start_frontend()

if __name__ == "__main__":
    main()
