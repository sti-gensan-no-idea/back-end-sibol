#!/usr/bin/env python3
"""
Startup script for Atuna API
This script ensures all dependencies are properly set up before starting the server
"""

import os
import sys
from pathlib import Path

def check_environment():
    """Check if the environment is properly set up"""
    print("🔧 Checking environment...")
    
    # Check if .env file exists
    if not Path('.env').exists():
        print("❌ .env file not found!")
        return False
    
    # Check virtual environment
    if not Path('.venv').exists():
        print("⚠️  Virtual environment not found, but continuing...")
    
    return True

def run_server():
    """Run the FastAPI server"""
    print("🚀 Starting Atuna API server...")
    
    try:
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0", 
            port=8000,
            reload=True,
            log_level="info"
        )
    except ImportError:
        print("❌ uvicorn not installed. Please install dependencies first.")
        print("Run: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("🏠 Atuna API - Real Estate Management System")
    print("="*60)
    
    if not check_environment():
        print("❌ Environment check failed!")
        sys.exit(1)
    
    print("✅ Environment check passed!")
    
    # Try to run the server
    if not run_server():
        sys.exit(1)
