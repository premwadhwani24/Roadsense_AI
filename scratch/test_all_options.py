"""
Comprehensive Test Suite for All 4 RoadSense AI Enhanced Features
1. Interactive Bounding Box & Heatmap Engine
2. Dashcam Video Clip Analyzer
3. PM Gati Shakti Government Audit Dossier & Export
4. Production Containerization & Deployment Configuration
"""
import os
import sys
import json
import time
import requests
from PIL import Image

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
if sys.stderr.encoding != 'utf-8':
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Ensure project root is in sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if os.path.abspath(".") not in sys.path:
    sys.path.insert(0, os.path.abspath("."))

def run_tests():
    print("=" * 70)
    print("  🚀 ROADSENSE AI - COMPREHENSIVE 4-OPTION VALIDATION SUITE")
    print("=" * 70)
    
    passed = 0
    total = 0
    
    # -------------------------------------------------------------
    # TEST 1: Vision Model & Bounding Box / IRC Metric Generation
    # -------------------------------------------------------------
    total += 1
    print("\n[TEST 1] Vision Service Bounding Box & IRC Metrics Generation...")
    try:
        from vision_service import RoadVisionService
        vs = RoadVisionService()
        test_img_path = "static/assets/damaged_roads/1_XoUpw9FGhfYh6Clpk_Wsbg-2x_jpg.rf.269bea6ceff5505771851fa8242fa6e0.jpg"
        
        # Test direct inference
        res = vs.analyze_image_detailed(test_img_path)
        assert "label" in res, "Missing label in vision output"
        assert "confidence" in res, "Missing confidence"
        assert "bounding_boxes" in res, "Missing bounding_boxes"
        assert "heatmap_points" in res, "Missing heatmap_points"
        assert "metrics_summary" in res, "Missing metrics_summary"
        
        # Test synthetic defect detection geometry
        dummy_img = Image.new("RGB", (640, 480), color=(100, 100, 100))
        pothole_spatial = vs.generate_bounding_boxes_and_metrics(dummy_img, "Pothole", 88.5)
        assert len(pothole_spatial["bounding_boxes"]) > 0, "No bounding boxes proposed for Pothole"
        first_box = pothole_spatial["bounding_boxes"][0]
        assert "measurements" in first_box, "Missing measurements"
        assert first_box["measurements"]["estimated_depth_cm"] > 0, "Invalid depth"
        assert first_box["measurements"]["surface_area_sq_m"] > 0, "Invalid area"
        assert "irc_grade" in first_box, "Missing IRC grade"
        assert len(pothole_spatial["heatmap_points"]) == 49, "Heatmap grid must be 7x7 (49 points)"
        
        print(f"  ✅ Vision Service passed! Defect: {first_box['label']}, Depth: {first_box['measurements']['estimated_depth_cm']}cm, Heatmap points: {len(pothole_spatial['heatmap_points'])}")
        passed += 1
    except Exception as e:
        print(f"  ❌ Vision Service test failed: {e}")

    # -------------------------------------------------------------
    # TEST 2: Dashcam Video Clip Analyzer & Temporal Inference
    # -------------------------------------------------------------
    total += 1
    print("\n[TEST 2] Dashcam Video Analyzer Service...")
    try:
        from video_analyzer_service import VideoAnalyzerService
        vas = VideoAnalyzerService(vision_service=vs)
        
        sim_res = vas.generate_synthetic_dashcam_patrol(duration_seconds=15.0, sample_interval_sec=1.5)
        assert sim_res["status"] == "success", "Video analysis failed"
        assert len(sim_res["timeline"]) == 10, f"Expected 10 frames, got {len(sim_res['timeline'])}"
        assert "summary" in sim_res, "Missing summary"
        assert "overall_condition_score" in sim_res["summary"], "Missing condition score"
        assert "hotspots" in sim_res, "Missing hotspots list"
        
        print(f"  ✅ Dashcam Video Analyzer passed! Frames: {len(sim_res['timeline'])}, Hotspots: {len(sim_res['hotspots'])}, Zone: {sim_res['summary']['overall_zone']}")
        passed += 1
    except Exception as e:
        print(f"  ❌ Dashcam Video test failed: {e}")

    # -------------------------------------------------------------
    # TEST 3: PM Gati Shakti Government Audit Dossier & Provenance
    # -------------------------------------------------------------
    total += 1
    print("\n[TEST 3] PM Gati Shakti Government Audit Dossier Engine...")
    try:
        from dossier_engine import GovernmentDossierEngine
        de = GovernmentDossierEngine()
        
        dossier = de.generate_corridor_dossier("OSM-LIVE-SEGMENT")
        assert "dossier_id" in dossier, "Missing dossier_id"
        assert "provenance_hash" in dossier, "Missing cryptographic provenance hash"
        assert len(dossier["provenance_hash"]) == 64, "SHA-256 hash must be 64 hex characters"
        assert "contractor_sla_audit" in dossier, "Missing contractor SLA audit"
        assert "bill_of_quantities_boq" in dossier, "Missing BOQ calculation"
        assert len(dossier["bill_of_quantities_boq"]["line_items"]) >= 3, "Incomplete BOQ line items"
        
        geojson = de.generate_pm_gati_shakti_geojson("OSM-LIVE-SEGMENT")
        assert geojson["type"] == "FeatureCollection", "Invalid GeoJSON type"
        assert len(geojson["features"]) > 0, "Empty GeoJSON features"
        
        print(f"  ✅ Dossier Engine passed! ID: {dossier['dossier_id']}, Hash: {dossier['provenance_hash'][:16]}..., BOQ Items: {len(dossier['bill_of_quantities_boq']['line_items'])}")
        passed += 1
    except Exception as e:
        print(f"  ❌ Dossier Engine test failed: {e}")

    # -------------------------------------------------------------
    # TEST 4: Production Containerization & WSGI Artifacts
    # -------------------------------------------------------------
    total += 1
    print("\n[TEST 4] Production Containerization & WSGI Configuration Files...")
    try:
        req_files = [
            "Dockerfile",
            "docker-compose.yml",
            "nginx/nginx.conf",
            "wsgi.py",
            "waitress_server.py",
            "gunicorn.conf.py",
            "deploy.sh",
            "deploy.ps1",
            ".dockerignore",
            "templates/dossier_print.html"
        ]
        for f in req_files:
            assert os.path.exists(f), f"Missing required production file: {f}"
            assert os.path.getsize(f) > 0, f"File {f} is empty"
        print(f"  ✅ All {len(req_files)} production deployment configuration files validated!")
        passed += 1
    except Exception as e:
        print(f"  ❌ Containerization files test failed: {e}")

    # -------------------------------------------------------------
    # TEST 5: Live Flask API Endpoints Integration
    # -------------------------------------------------------------
    total += 1
    print("\n[TEST 5] Live Flask Server Endpoints Verification (http://localhost:5000)...")
    try:
        base_url = "http://localhost:5000"
        
        # 1. Health check
        r_health = requests.get(f"{base_url}/health", timeout=5)
        assert r_health.status_code == 200, f"Health check failed: {r_health.status_code}"
        
        # 2. Video sample stream
        r_vid = requests.post(f"{base_url}/api/v3/video/sample-stream", json={"duration_seconds": 15.0}, timeout=10)
        assert r_vid.status_code == 200, f"Video sample stream failed: {r_vid.status_code}"
        assert r_vid.json()["status"] == "success"
        
        # 3. Dossier JSON API
        r_dos = requests.get(f"{base_url}/api/v3/gov/dossier/OSM-LIVE-SEGMENT", timeout=5)
        assert r_dos.status_code == 200, f"Dossier JSON failed: {r_dos.status_code}"
        assert "dossier" in r_dos.json()
        
        # 4. Dossier GeoJSON Export API
        r_geo = requests.get(f"{base_url}/api/v3/gov/dossier/export-geojson/OSM-LIVE-SEGMENT", timeout=5)
        assert r_geo.status_code == 200, f"Dossier GeoJSON failed: {r_geo.status_code}"
        assert r_geo.json()["type"] == "FeatureCollection"
        
        # 5. Printable A4 Dossier HTML Page
        r_print = requests.get(f"{base_url}/gov/dossier/print/OSM-LIVE-SEGMENT", timeout=5)
        assert r_print.status_code == 200, f"Printable Dossier page failed: {r_print.status_code}"
        assert "Ministry of Road Transport and Highways" in r_print.text
        
        # 6. Camera upload inspect with AI bounding boxes
        r_cam = requests.post(f"{base_url}/api/v3/gov/camera/upload-inspect", json={
            "image_url": "/static/assets/damaged_roads/1_XoUpw9FGhfYh6Clpk_Wsbg-2x_jpg.rf.269bea6ceff5505771851fa8242fa6e0.jpg",
            "latitude": 28.5450,
            "longitude": 77.1250
        }, timeout=10)
        assert r_cam.status_code == 200, f"Camera upload inspect failed: {r_cam.status_code}"
        assert "zone" in r_cam.json()
        
        print("  ✅ All 6 live HTTP backend endpoints returned 200 OK with expected payloads!")
        passed += 1
    except Exception as e:
        print(f"  ❌ Live API endpoints test failed: {e}")

    print("\n" + "=" * 70)
    print(f"  🏁 SUITE SUMMARY: {passed} / {total} TEST CATEGORIES PASSED")
    print("=" * 70)

    if passed == total:
        print("🎉 ALL 4 ROAD SENSE ENHANCEMENT OPTIONS FULLY FUNCTIONAL AND VERIFIED!")
        sys.exit(0)
    else:
        print("⚠️ Some tests encountered errors. Please check the logs.")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
