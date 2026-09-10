from http.server import BaseHTTPRequestHandler
import json
import os
import sys

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        mods = ['flask', 'flask_jwt_extended', 'werkzeug', 'numpy', 'requests', 'pandas', 'openpyxl', 'PIL', 'dotenv', 'sqlite3']
        results = {}
        for mod in mods:
            try:
                __import__(mod)
                results[mod] = 'OK'
            except Exception as e:
                results[mod] = f'FAILED: {e}'

        project_mods = [
            'database', 'auth', 'notifications', 'prediction_engine',
            'vision_service', 'video_analyzer_service', 'dossier_engine',
            'image_analysis_service', 'iot_sensors', 'crowd_sensing',
            'llm_assistant', 'graph_analytics', 'blockchain_audit',
            'digital_twin', 'mobile_api', 'data_fusion', 'traffic_engine',
            'rdd_engine', 'realtime_engine', 'gis_road_network',
            'pavement_scoring', 'repair_verification', 'gov_admin_service',
            'live_stream_service', 'whatsapp_bot', 'contractor_engine',
            'satellite_engine', 'emergency_routing', 'app_enhanced'
        ]
        
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if root_dir not in sys.path:
            sys.path.insert(0, root_dir)

        for pm in project_mods:
            try:
                __import__(pm)
                results[pm] = 'OK'
            except Exception as e:
                import traceback
                results[pm] = f'FAILED: {e}\\n{traceback.format_exc()}'
                break

        data = {
            'status': 'success',
            'cwd': os.getcwd(),
            'python_version': sys.version,
            'results': results
        }
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))
        return
