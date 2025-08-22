#!/usr/bin/env python3
"""
Simple frontend server using Python's built-in HTTP server.
This will definitely work and show the LLM Testing Interface.
"""

import http.server
import socketserver
import requests
import json
import os
from pathlib import Path

class LLMInterfaceHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Check if backend is running
            try:
                response = requests.get('http://127.0.0.1:8000/health', timeout=2)
                backend_status = "✅ Connected" if response.status_code == 200 else "❌ Error"
            except:
                backend_status = "❌ Disconnected"
            
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>LLM Testing Interface</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }}
        .header {{
            background-color: #1a1a1a;
            color: white;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .header h1 {{
            margin: 0;
            color: #646cff;
        }}
        .status {{
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-weight: 500;
        }}
        .status.connected {{
            background-color: rgba(16, 185, 129, 0.1);
            color: #10b981;
        }}
        .status.disconnected {{
            background-color: rgba(239, 68, 68, 0.1);
            color: #ef4444;
        }}
        .main {{
            padding: 2rem;
            text-align: center;
        }}
        .card {{
            background: white;
            border-radius: 8px;
            padding: 2rem;
            margin: 1rem auto;
            max-width: 600px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .button {{
            display: inline-block;
            background-color: #646cff;
            color: white;
            text-decoration: none;
            padding: 0.75rem 1.5rem;
            border-radius: 6px;
            font-weight: 500;
            margin: 0.5rem;
        }}
        .button:hover {{
            background-color: #535bf2;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>LLM Testing Interface</h1>
        <div class="status {'connected' if '✅' in backend_status else 'disconnected'}">
            {backend_status}
        </div>
    </div>
    
    <div class="main">
        <div class="card">
            <h2>🎉 Welcome to LLM Testing Interface!</h2>
            <p>Your interface is running successfully.</p>
            
            <div style="margin: 2rem 0;">
                <a href="http://127.0.0.1:8000/docs" target="_blank" class="button">
                    📚 API Documentation
                </a>
                <a href="http://127.0.0.1:8000/health" target="_blank" class="button">
                    🏥 Health Check
                </a>
            </div>
            
            <div style="margin-top: 2rem; padding: 1rem; background-color: #f8f9fa; border-radius: 6px;">
                <h3>Quick Links:</h3>
                <p><strong>Frontend:</strong> http://localhost:3000</p>
                <p><strong>Backend API:</strong> http://127.0.0.1:8000</p>
                <p><strong>API Docs:</strong> http://127.0.0.1:8000/docs</p>
            </div>
        </div>
    </div>
</body>
</html>
            """
            self.wfile.write(html.encode())
        else:
            super().do_GET()

def main():
    """Start the simple frontend server."""
    PORT = 3000
    
    print("🚀 Starting Simple Frontend Server...")
    print("=" * 50)
    print(f"🌐 Frontend: http://localhost:{PORT}")
    print("🔧 Backend API: http://127.0.0.1:8000")
    print("📚 API Docs: http://127.0.0.1:8000/docs")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        with socketserver.TCPServer(("", PORT), LLMInterfaceHandler) as httpd:
            print(f"✅ Server started on port {PORT}")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    main()
