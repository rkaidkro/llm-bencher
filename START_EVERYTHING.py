#!/usr/bin/env python3
"""
Comprehensive startup script for the LLM Testing Interface.
This script handles all the setup and provides clear feedback.
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def run_command(cmd, description, cwd=None):
    """Run a command and provide feedback."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def check_port(port):
    """Check if a port is available."""
    try:
        response = requests.get(f"http://127.0.0.1:{port}", timeout=1)
        return True
    except:
        return False

def main():
    """Main startup function."""
    print("🚀 LLM Testing Interface - Complete Startup")
    print("=" * 50)
    
    # Get project root
    project_root = Path(__file__).parent
    backend_dir = project_root / "backend"
    frontend_dir = project_root / "frontend"
    
    print(f"📁 Project root: {project_root}")
    print(f"📁 Backend dir: {backend_dir}")
    print(f"📁 Frontend dir: {frontend_dir}")
    print()
    
    # Step 1: Check if we're in the right place
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        print("Make sure you're in the llm-testing-interface directory")
        return
    
    # Step 2: Activate virtual environment
    print("🔧 Step 1: Setting up Python environment...")
    if not run_command("source venv/bin/activate && python --version", "Activating virtual environment", cwd=backend_dir):
        print("❌ Virtual environment not found!")
        print("Run: cd backend && python3 -m venv venv && source venv/bin/activate")
        return
    
    # Step 3: Initialize database
    print("\n🗄️ Step 2: Setting up database...")
    if not run_command("source venv/bin/activate && python -c 'from app.main import init_db; init_db(); print(\"Database ready\")'", "Initializing database", cwd=backend_dir):
        print("❌ Database initialization failed!")
        return
    
    # Step 4: Start backend server
    print("\n🌐 Step 3: Starting backend server...")
    if check_port(8000):
        print("⚠️ Port 8000 is already in use!")
        print("Stopping existing processes...")
        run_command("pkill -f 'uvicorn.*8000'", "Stopping existing processes")
        time.sleep(2)
    
    # Start backend in background
    backend_cmd = "source venv/bin/activate && python -c 'from app.main import app; import uvicorn; uvicorn.run(app, host=\"127.0.0.1\", port=8000)'"
    backend_process = subprocess.Popen(
        backend_cmd,
        shell=True,
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for backend to start
    print("⏳ Waiting for backend to start...")
    for i in range(10):
        time.sleep(1)
        if check_port(8000):
            print("✅ Backend server is running on http://127.0.0.1:8000")
            break
    else:
        print("❌ Backend server failed to start!")
        backend_process.terminate()
        return
    
    # Step 5: Test backend
    print("\n🧪 Step 4: Testing backend...")
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend health check passed")
        else:
            print(f"⚠️ Backend health check returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Backend health check failed: {e}")
    
    # Step 6: Start frontend
    print("\n🎨 Step 5: Starting frontend...")
    if check_port(3000):
        print("⚠️ Port 3000 is already in use!")
        run_command("pkill -f 'vite.*3000'", "Stopping existing frontend")
        time.sleep(2)
    
    # Check if frontend dependencies are installed
    if not (frontend_dir / "node_modules").exists():
        print("📦 Installing frontend dependencies...")
        if not run_command("npm install", "Installing frontend dependencies", cwd=frontend_dir):
            print("❌ Frontend dependencies installation failed!")
            return
    
    # Start frontend in background
    frontend_cmd = "npm run dev"
    frontend_process = subprocess.Popen(
        frontend_cmd,
        shell=True,
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for frontend to start
    print("⏳ Waiting for frontend to start...")
    for i in range(15):
        time.sleep(1)
        if check_port(3000):
            print("✅ Frontend server is running on http://localhost:3000")
            break
    else:
        print("❌ Frontend server failed to start!")
        frontend_process.terminate()
        backend_process.terminate()
        return
    
    # Success!
    print("\n🎉 SUCCESS! Everything is running!")
    print("=" * 50)
    print("🌐 Frontend: http://localhost:3000")
    print("🔧 Backend API: http://127.0.0.1:8000")
    print("📚 API Docs: http://127.0.0.1:8000/docs")
    print("🏥 Health Check: http://127.0.0.1:8000/health")
    print()
    print("Press Ctrl+C to stop all servers")
    print("=" * 50)
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Stopping servers...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✅ Servers stopped")

if __name__ == "__main__":
    main()
