#!/usr/bin/env python3
"""
RoadSense AI - Testing Guide
Run this to verify all features are working
"""

import requests
import json
import sys

# Enforce UTF-8 output on standard console streams to prevent crashes on emojis (✅ / ❌) in Windows environments
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

BASE_URL = "http://localhost:5000"
TOKEN = None

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_health():
    """Test 1: Health check"""
    print_section("Test 1: Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print(f"   Make sure app is running: python app_enhanced.py")
        return False

def test_login():
    """Test 2: Login"""
    global TOKEN
    print_section("Test 2: User Authentication")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        if response.status_code == 200:
            data = response.json()
            TOKEN = data['access_token']
            print("✅ Login successful")
            print(f"   Token: {TOKEN[:20]}...")
            return True
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(json.dumps(response.json(), indent=2))
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_get_user():
    """Test 3: Get current user"""
    print_section("Test 3: Get Current User")
    if not TOKEN:
        print("⚠️  Skipped - Not logged in")
        return False
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/auth/user",
            headers={"Authorization": f"Bearer {TOKEN}"}
        )
        if response.status_code == 200:
            print("✅ Get user successful")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_get_locations():
    """Test 4: Get locations"""
    print_section("Test 4: Get Locations")
    if not TOKEN:
        print("⚠️  Skipped - Not logged in")
        return False
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/locations",
            headers={"Authorization": f"Bearer {TOKEN}"}
        )
        if response.status_code == 200:
            print("✅ Get locations successful")
            data = response.json()
            print(f"   States: {len(data['states'])}")
            print(json.dumps(data, indent=2)[:300])
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_get_roads_status():
    """Test 5: Get roads status"""
    print_section("Test 5: Get Roads Status")
    if not TOKEN:
        print("⚠️  Skipped - Not logged in")
        return False
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/roads/status",
            headers={"Authorization": f"Bearer {TOKEN}"}
        )
        if response.status_code == 200:
            print("✅ Get roads status successful")
            data = response.json()
            print(f"   Total Roads: {data['total']}")
            print(f"   Green: {data['summary']['green']}")
            print(f"   Yellow: {data['summary']['yellow']}")
            print(f"   Red: {data['summary']['red']}")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_create_alert():
    """Test 6: Create alert"""
    print_section("Test 6: Create Alert")
    if not TOKEN:
        print("⚠️  Skipped - Not logged in")
        return False
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/alerts",
            headers={"Authorization": f"Bearer {TOKEN}"},
            json={
                "road_id": "R001",
                "road_name": "NH-52 Segment A",
                "severity": "YELLOW",
                "description": "Test alert from automated test"
            }
        )
        if response.status_code == 201:
            print("✅ Create alert successful")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_get_alerts():
    """Test 7: Get alerts"""
    print_section("Test 7: Get Alerts")
    if not TOKEN:
        print("⚠️  Skipped - Not logged in")
        return False
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/alerts",
            headers={"Authorization": f"Bearer {TOKEN}"}
        )
        if response.status_code == 200:
            print("✅ Get alerts successful")
            data = response.json()
            print(f"   Total Alerts: {data['count']}")
            if data['alerts']:
                print(f"   First Alert: {data['alerts'][0]['road_name']}")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_create_work_order():
    """Test 8: Create work order"""
    print_section("Test 8: Create Work Order")
    if not TOKEN:
        print("⚠️  Skipped - Not logged in")
        return False
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/work-orders",
            headers={"Authorization": f"Bearer {TOKEN}"},
            json={
                "road_id": "R002",
                "road_name": "MG Road",
                "work_type": "Pothole Repair",
                "contractor": "Test Contractor",
                "estimated_cost": 50000,
                "notes": "Test work order"
            }
        )
        if response.status_code == 201:
            print("✅ Create work order successful")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_get_work_orders():
    """Test 9: Get work orders"""
    print_section("Test 9: Get Work Orders")
    if not TOKEN:
        print("⚠️  Skipped - Not logged in")
        return False
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/work-orders",
            headers={"Authorization": f"Bearer {TOKEN}"}
        )
        if response.status_code == 200:
            print("✅ Get work orders successful")
            data = response.json()
            print(f"   Total Work Orders: {data['count']}")
            if data['work_orders']:
                print(f"   First WO: {data['work_orders'][0]['road_name']}")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_get_kpis():
    """Test 10: Get KPIs"""
    print_section("Test 10: Get KPIs")
    if not TOKEN:
        print("⚠️  Skipped - Not logged in")
        return False
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/analytics/kpis",
            headers={"Authorization": f"Bearer {TOKEN}"}
        )
        if response.status_code == 200:
            print("✅ Get KPIs successful")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_citizen_report():
    """Test 11: Create citizen report (public)"""
    print_section("Test 11: Create Citizen Report (Public)")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/reports/citizen",
            json={
                "latitude": 28.6139,
                "longitude": 77.2090,
                "issue_type": "pothole",
                "description": "Test pothole report"
            }
        )
        if response.status_code == 201:
            print("✅ Create citizen report successful")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_dashboard_summary():
    """Test 12: Get dashboard summary"""
    print_section("Test 12: Get Dashboard Summary")
    if not TOKEN:
        print("⚠️  Skipped - Not logged in")
        return False
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/dashboard/summary",
            headers={"Authorization": f"Bearer {TOKEN}"}
        )
        if response.status_code == 200:
            print("✅ Get dashboard summary successful")
            data = response.json()
            print(f"   Total Roads: {data['roads_summary']}")
            print(json.dumps(data, indent=2)[:400])
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_voice_report():
    """Test 13: Voice Dispatch Analysis Endpoint"""
    print_section("Test 13: Voice Dispatch Analysis")
    if not TOKEN:
        print("⚠️  Skipped - Not logged in")
        return False
    try:
        response = requests.post(
            f"{BASE_URL}/api/voice/report",
            headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
            json={"road_id": "R001", "transcript": "Critical urgent road collapse reported near main junction"}
        )
        if response.status_code == 201:
            print("✅ Voice report test successful")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_damaged_road_assets():
    """Test 14: Damaged Road Asset Gallery Endpoint"""
    print_section("Test 14: Damaged Road Asset Gallery")
    try:
        response = requests.get(f"{BASE_URL}/api/assets/damaged-roads")
        if response.status_code == 200:
            print("✅ Damaged road assets test successful")
            data = response.json()
            print(f"   Images found: {data.get('count', 0)}")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_adaptive_traffic_signals():
    """Test 15: Adaptive Traffic Light Signal Timing Endpoint"""
    print_section("Test 15: Adaptive Traffic Light Signal Timing")
    try:
        response = requests.get(f"{BASE_URL}/api/v3/traffic/adaptive-signals?city=Delhi")
        if response.status_code == 200:
            print("✅ Adaptive traffic signals test successful")
            data = response.json()
            print(f"   Intersections monitored: {data.get('intersections_monitored')}, Avg Green: {data.get('average_green_duration')}s")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_hazard_reroute():
    """Test 16: Hazard-Avoidance Route Optimization Endpoint"""
    print_section("Test 16: Hazard-Avoidance Route Optimization")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v3/navigation/reroute",
            headers={"Content-Type": "application/json"},
            json={"origin": "Connaught Place", "destination": "Airport Terminal 3"}
        )
        if response.status_code == 200:
            print("✅ Hazard reroute test successful")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_system_integrity():
    """Test 17: System Diagnostic Integrity Endpoint"""
    print_section("Test 17: System Diagnostic Integrity")
    try:
        response = requests.get(f"{BASE_URL}/api/v3/system/integrity")
        if response.status_code == 200:
            print("✅ System integrity test successful")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("  RoadSense AI - Automated Test Suite")
    print("="*60)
    
    results = []
    
    # Test 1: Health
    results.append(("Health Check", test_health()))
    
    if not results[-1][1]:
        print("\n❌ Application not running!")
        print("   Start with: python app_enhanced.py")
        return results
    
    # Test 2: Login
    results.append(("Authentication", test_login()))
    
    if not results[-1][1]:
        print("\n❌ Login failed!")
        return results
    
    # Test remaining
    results.append(("Get User", test_get_user()))
    results.append(("Get Locations", test_get_locations()))
    results.append(("Get Roads Status", test_get_roads_status()))
    results.append(("Create Alert", test_create_alert()))
    results.append(("Get Alerts", test_get_alerts()))
    results.append(("Create Work Order", test_create_work_order()))
    results.append(("Get Work Orders", test_get_work_orders()))
    results.append(("Get KPIs", test_get_kpis()))
    results.append(("Citizen Report", test_citizen_report()))
    results.append(("Dashboard Summary", test_dashboard_summary()))
    results.append(("Voice Report Analysis", test_voice_report()))
    results.append(("Damaged Road Assets", test_damaged_road_assets()))
    results.append(("Adaptive Traffic Signals", test_adaptive_traffic_signals()))
    results.append(("Hazard Rerouting", test_hazard_reroute()))
    results.append(("System Integrity", test_system_integrity()))
    
    # Print summary
    print_section("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check logs above.")
    
    return results

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTests cancelled by user")
        sys.exit(0)
