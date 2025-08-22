#!/usr/bin/env python3
"""
Minimal test server to verify basic functionality.
"""

from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Test server working!"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Test server is running"}

if __name__ == "__main__":
    print("🚀 Starting test server on port 8001...")
    uvicorn.run(app, host="127.0.0.1", port=8001)
