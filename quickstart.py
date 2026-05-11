#!/usr/bin/env python3
"""
RoadSense AI - Quick Start Script
Run this to start the enhanced system immediately
"""
import os
import sys
import subprocess

def run_quick_start():
    print("\n" + "="*70)
    print(" "*15 + "🛣️  ROADSENSE AI - QUICK START 🛣️")
    print("="*70 + "\n")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    
    print("📋 Step 1: Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Dependencies installed\n")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}\n")
        sys.exit(1)
    
    print("🗄️  Step 2: Initializing database...")
    try:
        from database import init_database
        from auth import DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD
        init_database()
        print("✅ Database initialized\n")
        print(f"   Default Login:")
        print(f"   - Username: {DEFAULT_ADMIN_USERNAME}")
        print(f"   - Password: {DEFAULT_ADMIN_PASSWORD}\n")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}\n")
        sys.exit(1)
    
    print("🚀 Step 3: Starting application...\n")
    print("-" * 70)
    print("   🌐 Open your browser: http://localhost:5000")
    print("   🔐 Login with admin / admin123")
    print("   📖 Full documentation: README_ENHANCED.md")
    print("-" * 70 + "\n")
    
    try:
        from app_enhanced import app
        app.run(host="0.0.0.0", port=5000, debug=True)
    except Exception as e:
        print(f"❌ Failed to start app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        run_quick_start()
    except KeyboardInterrupt:
        print("\n\n👋 Application stopped")
        sys.exit(0)
