import random
from typing import Dict, Any, List
from database import DatabaseManager

class IoTSensorEngine:
    """
    Mock engine to simulate high-frequency IoT sensor telemetry from smart road infrastructure.
    In a real system, this would subscribe to MQTT brokers from physical sensors.
    """
    
    @staticmethod
    def receive_telemetry(road_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming telemetry payload from an IoT node.
        """
        vibration = data.get("vibration_level", random.uniform(0.1, 5.0))
        temp = data.get("temperature", random.uniform(-10.0, 50.0))
        traffic_load = data.get("traffic_load_index", random.uniform(0.0, 10.0))
        
        record_id = DatabaseManager.add_iot_telemetry(
            road_id=road_id,
            vibration_level=vibration,
            temperature=temp,
            traffic_load_index=traffic_load
        )
        
        # Super simple mock logic for alerting
        status = "NORMAL"
        if vibration > 4.5 or traffic_load > 9.0:
            status = "CRITICAL_STRESS_DETECTED"
            
        return {
            "status": "success",
            "record_id": record_id,
            "analysis": status,
            "message": "Telemetry securely received and logged."
        }
    
    @staticmethod
    def synthesize_road_health(road_id: str) -> Dict[str, Any]:
        """
        Aggregates recent IoT data to determine physical stress.
        """
        logs = DatabaseManager.get_iot_telemetry(road_id, limit=20)
        if not logs:
            return {"status": "NO_DATA", "health_score": 100}
            
        avg_vibration = sum(l['vibration_level'] for l in logs) / len(logs)
        avg_load = sum(l['traffic_load_index'] for l in logs) / len(logs)
        
        health_score = max(0, 100 - (avg_vibration * 10) - (avg_load * 2))
        return {
            "health_score": round(health_score, 2),
            "average_vibration": round(avg_vibration, 2),
            "average_load": round(avg_load, 2)
        }
