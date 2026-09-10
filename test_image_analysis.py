#!/usr/bin/env python3
"""
Quick Test Script for Real-Time Image Analysis System
Tests the new CNN-based defect detection without hardcoding
"""
import requests
import json
import time
import sys
from pathlib import Path

BASE_URL = "http://localhost:5000"

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_analyze_dataset():
    """Test 1: Analyze entire dataset"""
    print_header("TEST 1: Analyze All Road Images")
    print("📊 Triggering dataset analysis...")
    print("⏳ This may take 2-5 minutes depending on image count...\n")
    
    try:
        response = requests.post(f"{BASE_URL}/api/image/analyze_dataset", timeout=600)
        if response.status_code == 200:
            data = response.json()
            stats = data.get("statistics", {})
            
            print(f"✅ Analysis Complete!")
            print(f"\n📈 Statistics:")
            print(f"   Total Images Processed: {stats.get('total_images', 0)}")
            print(f"   Defects Found: {stats.get('defects_found', 0)}")
            print(f"   Critical Roads: {stats.get('critical_roads', 0)}")
            print(f"   High Priority Roads: {stats.get('high_priority', 0)}")
            
            roads_by_severity = data.get("roads_by_severity", {})
            print(f"\n🚨 Road Breakdown:")
            for severity, roads in roads_by_severity.items():
                print(f"   {severity}: {len(roads)} roads")
            
            return True
        else:
            print(f"❌ Analysis Failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_road_status(road_id="ROAD_10075"):
    """Test 2: Get specific road condition"""
    print_header("TEST 2: Get Specific Road Condition")
    print(f"🔍 Querying status for road: {road_id}\n")
    
    try:
        response = requests.get(f"{BASE_URL}/api/image/road_status/{road_id}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            condition = data.get("condition", {})
            
            print(f"✅ Road Found!")
            print(f"\n📍 Road ID: {road_id}")
            print(f"🎯 Condition:")
            print(f"   Zone: {condition.get('zone', 'N/A')}")
            print(f"   Severity: {condition.get('severity', 'N/A')}")
            print(f"   Confidence: {condition.get('confidence', 0):.1f}%")
            print(f"   Total Defects: {condition.get('defect_count', 0)}")
            
            breakdown = condition.get('breakdown', {})
            print(f"\n🔎 Defect Breakdown:")
            print(f"   Potholes: {breakdown.get('potholes', 0)}")
            print(f"   Cracks: {breakdown.get('cracks', 0)}")
            print(f"   Normal Areas: {breakdown.get('normal', 0)}")
            
            proof_images = condition.get('proof_images', [])
            if proof_images:
                print(f"\n📸 Proof Images ({len(proof_images)} available):")
                for i, img in enumerate(proof_images[:3], 1):
                    print(f"   {i}. {img.get('label')} - Confidence: {img.get('confidence', 0):.1f}%")
            
            return True
        else:
            print(f"⚠️  Road not analyzed yet: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_single_image(image_path=None):
    """Test 3: Analyze single image"""
    print_header("TEST 3: Analyze Single Image")
    
    # Find test image
    if not image_path:
        dataset_path = Path("Dataset")
        raw_images = list(dataset_path.glob("*/*_RAW.*"))[:1]
        if raw_images:
            image_path = raw_images[0]
            print(f"📷 Using test image: {image_path}\n")
        else:
            print("❌ No test images found in Dataset/")
            return False
    
    try:
        with open(image_path, 'rb') as f:
            files = {'image': f}
            response = requests.post(
                f"{BASE_URL}/api/image/analyze_single",
                files=files,
                timeout=30
            )
        
        if response.status_code == 200:
            data = response.json()
            analysis = data.get("analysis", {})
            
            print(f"✅ Image Analyzed!")
            print(f"\n🖼️  Image: {image_path.name}")
            print(f"🏷️  Label: {analysis.get('label', 'Unknown')}")
            print(f"📊 Confidence: {analysis.get('confidence', 0):.1f}%")
            print(f"⚠️  Severity: {analysis.get('severity', 'N/A')}")
            print(f"✓  Status: {analysis.get('status', 'N/A')}")
            
            probs = analysis.get('probabilities', {})
            print(f"\n📈 Class Probabilities:")
            for label, prob in sorted(probs.items(), key=lambda x: x[1], reverse=True):
                print(f"   {label}: {prob:.1f}%")
            
            return True
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_connectivity():
    """Test 0: Check if server is running"""
    print_header("TEST 0: Server Connectivity")
    print(f"🔗 Checking connection to {BASE_URL}...\n")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"✅ Server is running!")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Size: {len(response.text)} bytes")
        return True
    except Exception as e:
        print(f"❌ Server not responding: {e}")
        print(f"\n💡 Make sure to start the Flask app first:")
        print(f"   python app_enhanced.py")
        return False

def main():
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  RoadSense AI - Real-Time Image Analysis Test Suite  ".center(58) + "║")
    print("║" + "  Real Defect Detection (No More Hardcoded Marks!)  ".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    # Test connectivity first
    if not test_connectivity():
        print("\n❌ Cannot proceed - server not running")
        sys.exit(1)
    
    time.sleep(1)
    
    # Run tests
    tests = [
        ("Analyze Dataset", test_analyze_dataset),
        ("Check Road Status", lambda: test_road_status("ROAD_10075")),
        ("Analyze Single Image", test_single_image)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
            time.sleep(1)  # Rate limiting
        except KeyboardInterrupt:
            print("\n\n⚠️  Tests interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Test error: {e}")
            results[test_name] = False
    
    # Summary
    print_header("TEST SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your system is working perfectly.")
        print("\n💡 Next steps:")
        print("   1. Integration with your frontend dashboard")
        print("   2. Enable real-time photo uploads from mobile")
        print("   3. Set up automated analysis scheduling")
        print("   4. Deploy to production")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
