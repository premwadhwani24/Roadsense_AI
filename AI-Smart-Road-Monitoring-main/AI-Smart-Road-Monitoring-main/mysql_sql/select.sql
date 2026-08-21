USE ai_smart_road_monitoring_system_application;

select * from activity_log;
select * from ai_predictions;
select * from dashboard_district_summary;
select * from dashboard_pothole_summary;
select * from potholes;
select * from repair_activity;
select * from roads;
select * from roles;
select * from sensor_data;
select * from users;

USE ai_smart_road_monitoring_system_application;

/* =========================================================
   BASIC ROW COUNTS (HEALTH CHECK)
   ========================================================= */
SELECT 'roles' AS table_name, COUNT(*) AS total FROM roles;
SELECT 'users' AS table_name, COUNT(*) AS total FROM users;
SELECT 'roads' AS table_name, COUNT(*) AS total FROM roads;
SELECT 'potholes' AS table_name, COUNT(*) AS total FROM potholes;
SELECT 'ai_predictions' AS table_name, COUNT(*) AS total FROM ai_predictions;
SELECT 'sensor_data' AS table_name, COUNT(*) AS total FROM sensor_data;
SELECT 'repair_activity' AS table_name, COUNT(*) AS total FROM repair_activity;


/* =========================================================
   USERS WITH ROLES
   ========================================================= */
SELECT
    u.id,
    u.username,
    u.email,
    r.name AS role_name,
    u.active,
    u.created_at
FROM users u
LEFT JOIN roles r ON u.role_id = r.id;


/* =========================================================
   POTHOLE FULL DETAILS (UPDATED FIELDS)
   ========================================================= */
SELECT
    p.id AS pothole_id,
    p.road_id,
    p.gps_location,
    p.gps_pin,
    p.latitude,
    p.longitude,
    p.length,
    p.width,
    p.depth,
    p.severity,
    p.status,
    p.detected_date,
    p.detected_at,
    p.image_path
FROM potholes p;


/* =========================================================
   POTHOLE + ROAD + AI CONFIDENCE
   ========================================================= */
SELECT
    p.id AS pothole_id,
    r.road_name,
    r.district,
    p.severity,
    p.status,
    a.model_name,
    a.confidence
FROM potholes p
JOIN roads r ON p.road_id = r.id
LEFT JOIN ai_predictions a ON p.id = a.pothole_id;


/* =========================================================
   SENSOR DATA AGGREGATION (ROAD LEVEL)
   ========================================================= */
SELECT
    r.road_name,
    AVG(s.vibration) AS avg_vibration,
    AVG(s.speed) AS avg_speed,
    AVG(s.temperature) AS avg_temperature
FROM sensor_data s
JOIN roads r ON s.road_id = r.id
GROUP BY r.road_name;


/* =========================================================
   REPAIR STATUS SUMMARY
   ========================================================= */
SELECT
    status,
    COUNT(*) AS total_repairs
FROM repair_activity
GROUP BY status;


/* =========================================================
   DASHBOARD TABLES
   ========================================================= */
SELECT * FROM dashboard_district_summary;
SELECT * FROM dashboard_pothole_summary;
