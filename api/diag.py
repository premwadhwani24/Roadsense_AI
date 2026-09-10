from http.server import BaseHTTPRequestHandler
import json
import os
import sys

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        results = {}
        for mod in ['flask', 'flask_jwt_extended', 'werkzeug', 'numpy', 'requests', 'pandas', 'openpyxl', 'PIL', 'dotenv']:
            try:
                __import__(mod)
                results[mod] = 'OK'
            except Exception as e:
                results[mod] = f'FAILED: {e}'
        
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if root_dir not in sys.path:
            sys.path.insert(0, root_dir)

        try:
            import app_enhanced
            results['app_enhanced'] = 'OK'
        except Exception as e:
            import traceback
            results['app_enhanced'] = f'FAILED: {e}\\n{traceback.format_exc()}'

        data = {
            'cwd': os.getcwd(),
            'python_version': sys.version,
            'files_in_cwd': os.listdir('.') if os.path.exists('.') else [],
            'files_in_root': os.listdir(root_dir) if os.path.exists(root_dir) else [],
            'results': results
        }
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))
