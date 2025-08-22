#!/usr/bin/env python3
"""
Configuration helper for setting up remote LLM servers.

This script helps you configure the LLM Testing Interface to connect to
remote Ollama and LM Studio servers on your network.
"""

import os
import re

def get_server_config():
    """Get server configuration from user."""
    print("🔧 LLM Server Configuration")
    print("=" * 40)
    print("Enter the IP addresses of your remote LLM servers:")
    print()
    
    ollama_ip = input("Ollama server IP (e.g., 192.168.1.100): ").strip()
    if not ollama_ip:
        ollama_ip = "192.168.1.100"
    
    lm_studio_ip = input("LM Studio server IP (e.g., 192.168.1.101): ").strip()
    if not lm_studio_ip:
        lm_studio_ip = "192.168.1.101"
    
    return ollama_ip, lm_studio_ip

def update_env_file(ollama_ip, lm_studio_ip):
    """Update the .env file with server IPs."""
    env_path = "backend/.env"
    
    if not os.path.exists(env_path):
        print(f"❌ {env_path} not found. Please run the setup first.")
        return False
    
    # Read current .env file
    with open(env_path, 'r') as f:
        content = f.read()
    
    # Update the URLs
    content = re.sub(
        r'OLLAMA_BASE_URL=.*',
        f'OLLAMA_BASE_URL=http://{ollama_ip}:11434',
        content
    )
    content = re.sub(
        r'LM_STUDIO_BASE_URL=.*',
        f'LM_STUDIO_BASE_URL=http://{lm_studio_ip}:1234/v1',
        content
    )
    
    # Write updated content
    with open(env_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated {env_path} with server IPs:")
    print(f"   Ollama: http://{ollama_ip}:11434")
    print(f"   LM Studio: http://{lm_studio_ip}:1234/v1")
    return True

def test_connection(ip, port, service_name):
    """Test connection to a server."""
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((ip, port))
        sock.close()
        
        if result == 0:
            print(f"✅ {service_name} server at {ip}:{port} is reachable")
            return True
        else:
            print(f"❌ {service_name} server at {ip}:{port} is not reachable")
            return False
    except Exception as e:
        print(f"❌ Error testing {service_name} connection: {e}")
        return False

def main():
    """Main configuration function."""
    print("🚀 LLM Testing Interface - Server Configuration")
    print("=" * 50)
    print()
    
    # Get server IPs
    ollama_ip, lm_studio_ip = get_server_config()
    
    print()
    print("Testing connections...")
    
    # Test connections
    ollama_ok = test_connection(ollama_ip, 11434, "Ollama")
    lm_studio_ok = test_connection(lm_studio_ip, 1234, "LM Studio")
    
    print()
    if ollama_ok or lm_studio_ok:
        print("✅ At least one server is reachable. Updating configuration...")
        if update_env_file(ollama_ip, lm_studio_ip):
            print()
            print("🎉 Configuration updated successfully!")
            print("You can now start the server with: python start_server.py")
        else:
            print("❌ Failed to update configuration")
    else:
        print("❌ No servers are reachable. Please check:")
        print("   - Server IP addresses are correct")
        print("   - Servers are running and accessible")
        print("   - Firewall settings allow connections")
        print("   - Network connectivity")

if __name__ == "__main__":
    main()
