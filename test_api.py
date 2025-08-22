#!/usr/bin/env python3
"""
Simple test script to verify the llm-bencher API is working.

This script tests the basic endpoints to ensure the backend is functioning correctly.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health_endpoint():
    """Test the health check endpoint."""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_root_endpoint():
    """Test the root endpoint."""
    print("🔍 Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root endpoint: {data}")
            return True
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
        return False

def test_models_endpoint():
    """Test the models endpoint."""
    print("🔍 Testing models endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/models")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Models endpoint: {data}")
            return True
        else:
            print(f"❌ Models endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Models endpoint error: {e}")
        return False

def test_conversations_endpoint():
    """Test the conversations endpoint."""
    print("🔍 Testing conversations endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/conversations")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Conversations endpoint: {data}")
            return True
        else:
            print(f"❌ Conversations endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Conversations endpoint error: {e}")
        return False

def test_create_conversation():
    """Test creating a new conversation."""
    print("🔍 Testing conversation creation...")
    try:
        conversation_data = {"title": "Test Conversation"}
        response = requests.post(
            f"{BASE_URL}/api/v1/conversations",
            json=conversation_data
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Conversation created: {data}")
            return data.get("id")
        else:
            print(f"❌ Conversation creation failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Conversation creation error: {e}")
        return None

def test_llm_services_endpoint():
    """Test the LLM services endpoint."""
    print("🔍 Testing LLM services endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/llm/services")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ LLM services endpoint: {data}")
            return True
        else:
            print(f"❌ LLM services endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ LLM services endpoint error: {e}")
        return False

def test_monitoring_endpoint():
    """Test the monitoring endpoint."""
    print("🔍 Testing monitoring endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/monitoring/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Monitoring endpoint: {data}")
            return True
        else:
            print(f"❌ Monitoring endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Monitoring endpoint error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting llm-bencher API Tests")
    print("=" * 50)
    
    # Wait a moment for server to be ready
    time.sleep(1)
    
    tests = [
        test_health_endpoint,
        test_root_endpoint,
        test_models_endpoint,
        test_conversations_endpoint,
        test_llm_services_endpoint,
        test_monitoring_endpoint,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    # Test conversation creation
    conv_id = test_create_conversation()
    if conv_id:
        passed += 1
    total += 1
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the server logs for details.")
    
    return passed == total

if __name__ == "__main__":
    main()
