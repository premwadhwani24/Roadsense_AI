"""
Gunicorn Production Server Configuration
RoadSense AI
"""
import os
import multiprocessing

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
backlog = 2048

# Worker processes
workers = int(os.getenv("WEB_CONCURRENCY", 2))
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Security & Process Management
proc_name = "roadsense_ai"
daemon = False
preload_app = True
