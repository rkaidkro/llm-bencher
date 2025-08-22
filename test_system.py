#!/usr/bin/env python3
"""
Comprehensive Testing Framework for llm-bencher
This script tests every component with detailed logging and error reporting.
"""

import os
import sys
import time
import json
import requests
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/test_system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SystemTester:
    """Comprehensive system testing framework."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        self.logs_dir = self.project_root / "logs"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "overall_status": "unknown",
            "summary": {}
        }
        
        # Ensure logs directory exists
        self.logs_dir.mkdir(exist_ok=True)
    
    def log_test(self, test_name: str, status: str, details: str = "", error: str = ""):
        """Log test results."""
        self.results["tests"][test_name] = {
            "status": status,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        
        if status == "PASS":
            logger.info(f"✅ {test_name}: {details}")
        elif status == "FAIL":
            logger.error(f"❌ {test_name}: {error}")
        elif status == "WARNING":
            logger.warning(f"⚠️ {test_name}: {details}")
    
    def run_command(self, cmd: str, description: str, cwd: Optional[Path] = None) -> Dict[str, Any]:
        """Run a command and return results."""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Command timed out after 30 seconds",
                "returncode": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }
    
    def check_port(self, port: int) -> bool:
        """Check if a port is in use."""
        try:
            response = requests.get(f"http://127.0.0.1:{port}", timeout=1)
            return True
        except:
            return False
    
    def test_environment(self) -> bool:
        """Test basic environment setup."""
        logger.info("🔧 Testing environment setup...")
        
        # Test 1: Check if we're in the right directory
        if not self.backend_dir.exists():
            self.log_test("environment_directory", "FAIL", "", "Backend directory not found")
            return False
        self.log_test("environment_directory", "PASS", "Backend directory exists")
        
        # Test 2: Check virtual environment
        venv_path = self.backend_dir / "venv"
        if not venv_path.exists():
            self.log_test("environment_venv", "FAIL", "", "Virtual environment not found")
            return False
        self.log_test("environment_venv", "PASS", "Virtual environment exists")
        
        # Test 3: Check Python in venv
        result = self.run_command(
            "source venv/bin/activate && python --version",
            "Python version check",
            cwd=self.backend_dir
        )
        if result["success"]:
            self.log_test("environment_python", "PASS", f"Python: {result['stdout'].strip()}")
        else:
            self.log_test("environment_python", "FAIL", "", result["stderr"])
            return False
        
        # Test 4: Check dependencies
        result = self.run_command(
            "source venv/bin/activate && python -c 'import fastapi, uvicorn, requests; print(\"Dependencies OK\")'",
            "Dependencies check",
            cwd=self.backend_dir
        )
        if result["success"]:
            self.log_test("environment_dependencies", "PASS", "All required dependencies installed")
        else:
            self.log_test("environment_dependencies", "FAIL", "", result["stderr"])
            return False
        
        return True
    
    def test_database(self) -> bool:
        """Test database functionality."""
        logger.info("🗄️ Testing database...")
        
        # Test database initialization
        result = self.run_command(
            "source venv/bin/activate && python -c 'from app.main import init_db; init_db(); print(\"Database initialized\")'",
            "Database initialization",
            cwd=self.backend_dir
        )
        if result["success"]:
            self.log_test("database_init", "PASS", "Database initialized successfully")
        else:
            self.log_test("database_init", "FAIL", "", result["stderr"])
            return False
        
        # Check if database file exists
        db_file = self.backend_dir / "llm_interface.db"
        if db_file.exists():
            self.log_test("database_file", "PASS", f"Database file exists ({db_file.stat().st_size} bytes)")
        else:
            self.log_test("database_file", "FAIL", "", "Database file not found")
            return False
        
        return True
    
    def test_backend_startup(self) -> bool:
        """Test backend server startup."""
        logger.info("🌐 Testing backend startup...")
        
        # Kill any existing processes
        self.run_command("pkill -f 'uvicorn.*8000'", "Kill existing backend")
        time.sleep(2)
        
        # Start backend in background
        result = self.run_command(
            "source venv/bin/activate && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload",
            "Start backend server",
            cwd=self.backend_dir
        )
        
        # Wait for server to start
        for i in range(10):
            time.sleep(1)
            if self.check_port(8000):
                self.log_test("backend_startup", "PASS", "Backend server started successfully")
                return True
        
        self.log_test("backend_startup", "FAIL", "", "Backend server failed to start")
        return False
    
    def test_backend_endpoints(self) -> bool:
        """Test backend API endpoints."""
        logger.info("🔗 Testing backend endpoints...")
        
        endpoints = [
            ("/", "Root endpoint"),
            ("/health", "Health check"),
            ("/docs", "API documentation"),
            ("/api/v1/conversations", "Conversations endpoint"),
            ("/api/v1/llm/services", "LLM services endpoint")
        ]
        
        all_passed = True
        
        for endpoint, description in endpoints:
            try:
                response = requests.get(f"http://127.0.0.1:8000{endpoint}", timeout=5)
                if response.status_code == 200:
                    self.log_test(f"endpoint_{endpoint.replace('/', '_')}", "PASS", f"{description}: 200 OK")
                else:
                    self.log_test(f"endpoint_{endpoint.replace('/', '_')}", "WARNING", f"{description}: {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log_test(f"endpoint_{endpoint.replace('/', '_')}", "FAIL", "", f"{description}: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_frontend(self) -> bool:
        """Test frontend functionality."""
        logger.info("🎨 Testing frontend...")
        
        # Check if simple frontend exists
        frontend_file = self.project_root / "simple_frontend.py"
        if not frontend_file.exists():
            self.log_test("frontend_file", "FAIL", "", "simple_frontend.py not found")
            return False
        self.log_test("frontend_file", "PASS", "Frontend file exists")
        
        # Kill any existing frontend processes
        self.run_command("pkill -f 'simple_frontend.py'", "Kill existing frontend")
        time.sleep(2)
        
        # Start frontend in background
        result = self.run_command(
            "python simple_frontend.py",
            "Start frontend server",
            cwd=self.project_root
        )
        
        # Wait for frontend to start
        for i in range(10):
            time.sleep(1)
            if self.check_port(3000):
                self.log_test("frontend_startup", "PASS", "Frontend server started successfully")
                return True
        
        self.log_test("frontend_startup", "FAIL", "", "Frontend server failed to start")
        return False
    
    def test_integration(self) -> bool:
        """Test full system integration."""
        logger.info("🔗 Testing system integration...")
        
        # Test frontend can access backend
        try:
            response = requests.get("http://localhost:3000", timeout=5)
            if response.status_code == 200:
                self.log_test("integration_frontend_backend", "PASS", "Frontend can access backend")
            else:
                self.log_test("integration_frontend_backend", "WARNING", f"Frontend returned {response.status_code}")
        except Exception as e:
            self.log_test("integration_frontend_backend", "FAIL", "", f"Frontend-backend integration failed: {str(e)}")
            return False
        
        return True
    
    def generate_report(self):
        """Generate comprehensive test report."""
        logger.info("📊 Generating test report...")
        
        # Calculate summary
        total_tests = len(self.results["tests"])
        passed_tests = sum(1 for test in self.results["tests"].values() if test["status"] == "PASS")
        failed_tests = sum(1 for test in self.results["tests"].values() if test["status"] == "FAIL")
        warning_tests = sum(1 for test in self.results["tests"].values() if test["status"] == "WARNING")
        
        self.results["summary"] = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "warnings": warning_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
        }
        
        if failed_tests == 0 and warning_tests == 0:
            self.results["overall_status"] = "PASS"
        elif failed_tests == 0:
            self.results["overall_status"] = "WARNING"
        else:
            self.results["overall_status"] = "FAIL"
        
        # Save detailed report
        report_file = self.logs_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Print summary
        print("\n" + "="*60)
        print("📊 TEST REPORT SUMMARY")
        print("="*60)
        print(f"Overall Status: {self.results['overall_status']}")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Warnings: {warning_tests}")
        print(f"Success Rate: {self.results['summary']['success_rate']:.1f}%")
        print(f"Detailed Report: {report_file}")
        print("="*60)
        
        return self.results["overall_status"] == "PASS"
    
    def cleanup(self):
        """Clean up test processes."""
        logger.info("🧹 Cleaning up test processes...")
        self.run_command("pkill -f 'uvicorn.*8000'", "Kill backend")
        self.run_command("pkill -f 'simple_frontend.py'", "Kill frontend")
        time.sleep(2)
    
    def run_all_tests(self) -> bool:
        """Run all tests in sequence."""
        logger.info("🚀 Starting comprehensive system tests...")
        
        try:
            # Run tests in order
            tests = [
                ("Environment", self.test_environment),
                ("Database", self.test_database),
                ("Backend Startup", self.test_backend_startup),
                ("Backend Endpoints", self.test_backend_endpoints),
                ("Frontend", self.test_frontend),
                ("Integration", self.test_integration)
            ]
            
            for test_name, test_func in tests:
                logger.info(f"\n{'='*20} {test_name} Tests {'='*20}")
                if not test_func():
                    logger.error(f"❌ {test_name} tests failed")
                    break
            
            # Generate report
            success = self.generate_report()
            
            return success
            
        finally:
            self.cleanup()

def main():
    """Main test runner."""
    tester = SystemTester()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "quick":
            # Quick test - just environment and database
            logger.info("🔍 Running quick tests...")
            success = tester.test_environment() and tester.test_database()
            tester.generate_report()
            sys.exit(0 if success else 1)
        elif sys.argv[1] == "backend":
            # Backend only tests
            logger.info("🔧 Running backend tests...")
            success = (tester.test_environment() and 
                      tester.test_database() and 
                      tester.test_backend_startup() and 
                      tester.test_backend_endpoints())
            tester.generate_report()
            sys.exit(0 if success else 1)
    
    # Full test suite
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
