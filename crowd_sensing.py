import random
from typing import Dict, Any, List
from database import DatabaseManager

class CrowdSensingEngine:
    """
    Mock engine to simulate vehicle motion data analysis.
    In real scale, this consumes streams of GPS+Accelerometer data from connected cars to detect potholes automatically.
    """
    
    @staticmethod
    def process_vehicle_stream(vehicle_id: str, stream_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Takes a continuous stream of GPS + Z-axis acceleration and extracts anomalies.
        """
        anomalies_detected = []
        for point in stream_data:
            # Mock detection: High z-axis acceleration change indicates a bump/pothole
            z_accel = point.get("z_accel", 1.0)
            if abs(z_accel - 1.0) > 1.5:  # Arbitrary threshold for anomaly
                anomaly_type = "Severe Pothole" if abs(z_accel - 1.0) > 3.0 else "Minor Bump"
                confidence = min(0.99, abs(z_accel - 1.0) * 0.2)
                
                record_id = DatabaseManager.add_vehicle_anomaly(
                    vehicle_id=vehicle_id,
                    road_id=point.get("road_id", "UNKNOWN"),
                    latitude=point.get("latitude", 0.0),
                    longitude=point.get("longitude", 0.0),
                    anomaly_type=anomaly_type,
                    confidence=confidence
                )
                anomalies_detected.append({
                    "id": record_id,
                    "type": anomaly_type,
                    "lat": point.get("latitude"),
                    "lng": point.get("longitude")
                })
                
        return {
            "processed_points": len(stream_data),
            "anomalies_found": len(anomalies_detected),
            "anomalies": anomalies_detected
        }
    
    @staticmethod
    def run_mock_simulation(road_id: str, lat: float, lng: float):
        """Simulate a vehicle hitting a pothole for demo purposes."""
        mock_stream = [
            {"latitude": lat, "longitude": lng, "z_accel": random.uniform(2.5, 4.5), "road_id": road_id}
        ]
        return CrowdSensingEngine.process_vehicle_stream("V-MOCK-001", mock_stream)
