import os
import sys

# Add root project directory to Python path so app_enhanced and modules can be imported
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app_enhanced import app

# Export WSGI application for Vercel Serverless Functions
app = app
