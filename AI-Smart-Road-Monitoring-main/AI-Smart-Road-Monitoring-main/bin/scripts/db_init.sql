-- Create the database with correct name
CREATE DATABASE IF NOT EXISTS ai_smart_road_monitoring_system_application;
USE ai_smart_road_monitoring_system_application;

-- -------------------------
-- Table structure for pothole
-- -------------------------
CREATE TABLE IF NOT EXISTS pothole (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    length DOUBLE,
    width DOUBLE,
    depth DOUBLE,
    image_path VARCHAR(512),
    gps_coordinates VARCHAR(128),
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
