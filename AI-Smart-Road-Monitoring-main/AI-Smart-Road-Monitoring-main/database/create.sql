/* =========================================================
   DATABASE
   ========================================================= */
DROP DATABASE IF EXISTS ai_smart_road_monitoring_system_application;

CREATE DATABASE ai_smart_road_monitoring_system_application
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE ai_smart_road_monitoring_system_application;


/* =========================================================
   ROLES
   ========================================================= */
CREATE TABLE roles (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255)
);


/* =========================================================
   USERS
   ========================================================= */
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(150),
    role_id BIGINT,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_users_role
        FOREIGN KEY (role_id) REFERENCES roles(id)
);


/* =========================================================
   ROADS
   ========================================================= */
CREATE TABLE roads (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    road_name VARCHAR(200) NOT NULL,
    district VARCHAR(100),
    state VARCHAR(100),
    latitude DECIMAL(10,6),
    longitude DECIMAL(10,6)
);


/* =========================================================
   POTHOLES  (MATCHES FINAL Pothole.java)
   ========================================================= */
CREATE TABLE potholes (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    road_id BIGINT NOT NULL,

    gps_location VARCHAR(255),
    gps_pin VARCHAR(255),

    latitude DECIMAL(10,6) NOT NULL,
    longitude DECIMAL(10,6) NOT NULL,

    length DOUBLE,
    width DOUBLE,
    depth DOUBLE,

    severity VARCHAR(50),
    status VARCHAR(50),

    detected_date DATETIME,
    detected_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    image_path VARCHAR(255),

    CONSTRAINT fk_potholes_road
        FOREIGN KEY (road_id) REFERENCES roads(id)
        ON DELETE CASCADE
);


/* =========================================================
   AI PREDICTIONS
   ========================================================= */
CREATE TABLE ai_predictions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    pothole_id BIGINT NOT NULL,
    model_name VARCHAR(100),
    confidence DECIMAL(5,2),
    prediction_label VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_ai_pothole
        FOREIGN KEY (pothole_id) REFERENCES potholes(id)
        ON DELETE CASCADE
);


/* =========================================================
   SENSOR DATA
   ========================================================= */
CREATE TABLE sensor_data (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    road_id BIGINT NOT NULL,
    vibration DECIMAL(6,2),
    speed DECIMAL(6,2),
    temperature DECIMAL(5,2),
    recorded_at TIMESTAMP,
    CONSTRAINT fk_sensor_road
        FOREIGN KEY (road_id) REFERENCES roads(id)
        ON DELETE CASCADE
);


/* =========================================================
   REPAIR ACTIVITY
   ========================================================= */
CREATE TABLE repair_activity (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    pothole_id BIGINT NOT NULL,
    status VARCHAR(50),
    assigned_to VARCHAR(100),
    repair_date DATE,
    remarks VARCHAR(255),
    CONSTRAINT fk_repair_pothole
        FOREIGN KEY (pothole_id) REFERENCES potholes(id)
        ON DELETE CASCADE
);


/* =========================================================
   ACTIVITY LOG
   ========================================================= */
CREATE TABLE activity_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    entity VARCHAR(100),
    action VARCHAR(100),
    message VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


/* =========================================================
   DASHBOARD TABLES
   ========================================================= */
CREATE TABLE dashboard_district_summary (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    district VARCHAR(100),
    total_roads INT DEFAULT 0,
    total_potholes INT DEFAULT 0,
    repaired_potholes INT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE dashboard_pothole_summary (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    severity VARCHAR(50),
    total_count INT DEFAULT 0,
    district VARCHAR(100),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE VIEW road_condition_view AS
SELECT
    r.id AS road_id,
    CASE
        WHEN COUNT(p.id) = 0 THEN 'GOOD'
        WHEN COUNT(p.id) BETWEEN 1 AND 3 THEN 'MODERATE'
        ELSE 'BAD'
    END AS road_condition
FROM roads r
LEFT JOIN potholes p ON r.id = p.road_id
GROUP BY r.id;
