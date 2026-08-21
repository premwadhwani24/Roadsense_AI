import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from utils.logger import get_logger

logger = get_logger(__name__)

def get_gps_location():
    lat = 23.17 + random.uniform(-0.01, 0.01)
    lon = 79.94 + random.uniform(-0.01, 0.01)
    logger.info(f"GPS Coordinates: ({lat:.6f}, {lon:.6f})")
    return {"latitude": lat, "longitude": lon}

if __name__ == "__main__":
    print(get_gps_location())
