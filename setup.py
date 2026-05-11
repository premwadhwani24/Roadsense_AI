"""
Quick setup script for RoadSense AI Enhanced System
Run this to initialize everything needed
"""
import os
import sys
from database import init_database
from auth import DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD

def setup():
    print("=" * 60)
    print("RoadSense AI - Enhanced Setup")
    print("=" * 60)
    
    # Initialize database
    print("\n[1/3] Initializing database...")
    try:
        init_database()
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False
    
    # Create default admin
    print("\n[2/3] Setting up default admin user...")
    print(f"    Username: {DEFAULT_ADMIN_USERNAME}")
    print(f"    Password: {DEFAULT_ADMIN_PASSWORD}")
    print("    (Change these in production!)")
    
    # Verify admin exists
    from database import DatabaseManager
    admin = DatabaseManager.get_user(DEFAULT_ADMIN_USERNAME)
    if admin:
        print("✓ Admin user exists")
    else:
        print("✓ Admin user will be created on first run")
    
    # Check dependencies
    print("\n[3/3] Checking dependencies...")
    required_packages = ['flask', 'pandas', 'numpy', 'requests']
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"    ✓ {package}")
        except ImportError:
            print(f"    ✗ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n⚠  Missing packages: {', '.join(missing)}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    print("\n" + "=" * 60)
    print("✓ Setup complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Set environment variables (optional)")
    print("2. Run: python app_enhanced.py")
    print("3. Open http://localhost:5000 in your browser")
    print("4. Login with admin / admin123")
    print("\nDocumentation: See README_ENHANCED.md")
    
    return True

if __name__ == "__main__":
    success = setup()
    sys.exit(0 if success else 1)
