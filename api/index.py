import os
import sys
import traceback

# Add root project directory to Python path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
    from app_enhanced import app
except Exception as startup_err:
    from flask import Flask, jsonify
    app = Flask(__name__)
    err_msg = str(startup_err)
    err_tb = traceback.format_exc()

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def catch_all_startup_error(path):
        return jsonify({
            "success": False,
            "error": "Serverless Startup Failed",
            "details": err_msg,
            "traceback": err_tb
        }), 200
