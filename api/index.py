import os
import sys

# Add root project directory to Python path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app_enhanced import app

class VercelPathMiddleware:
    """WSGI Middleware to restore original request path on Vercel"""
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        matched_path = environ.get('HTTP_X_MATCHED_PATH')
        if matched_path:
            environ['PATH_INFO'] = matched_path
        else:
            path = environ.get('PATH_INFO', '')
            for prefix in ['/api/index.py', '/api/index']:
                if path == prefix:
                    path = '/'
                    break
                elif path.startswith(prefix + '/'):
                    path = path[len(prefix):] or '/'
                    break
            environ['PATH_INFO'] = path
        environ['SCRIPT_NAME'] = ''
        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathMiddleware(app.wsgi_app)
