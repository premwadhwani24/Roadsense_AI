"""
Waitress Production WSGI Server for Windows / Cross-Platform
RoadSense AI
"""
import os
import sys
import logging
from waitress import serve
from app_enhanced import app

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("waitress_server")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    threads = int(os.environ.get("WAITRESS_THREADS", 6))
    
    logger.info(f"Starting RoadSense AI Production Waitress Server on port {port} with {threads} threads...")
    print(f"============================================================")
    print(f"   RoadSense AI Production Server (Waitress WSGI)")
    print(f"   Listening on: http://0.0.0.0:{port}")
    print(f"   Threads: {threads}")
    print(f"============================================================")
    
    serve(app, host="0.0.0.0", port=port, threads=threads, channel_timeout=120)
