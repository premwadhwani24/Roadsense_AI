import sqlite3
import random
from typing import Dict, Any

from database import DB_PATH

class DigitalTwinEngine:
    """
    Manages the Digital Twin states for roads: simulating real-world degradation patterns
    virtually inside the system.
    """
    
    @staticmethod
    def sync_digital_twin_state(road_id: str) -> Dict[str, Any]:
        """
        Syncs real-world parameters (IoT, Age) to update the virtual twin's mathematical state.
        Realistically this would involve massive physical simulation compute.
        """
        # Mock physics recalculation
        physics_age = random.randint(100, 3600)  # days modeled
        weather_stress = random.uniform(0.1, 10.0)
        overall_health = max(0, 100 - (weather_stress * 2) - (physics_age * 0.01))
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO digital_twin_states (road_id, simulated_age_days, stress_level, weather_impact_factor, overall_health_score) VALUES (?, ?, ?, ?, ?)',
            (road_id, physics_age, weather_stress * 1.5, weather_stress, overall_health)
        )
        conn.commit()
        conn.close()
        
        return {
            "road_id": road_id,
            "status": "Digital Twin Synchronized",
            "computed_health_score": round(overall_health, 2),
            "simulated_structural_stress": round(weather_stress * 1.5, 2)
        }
