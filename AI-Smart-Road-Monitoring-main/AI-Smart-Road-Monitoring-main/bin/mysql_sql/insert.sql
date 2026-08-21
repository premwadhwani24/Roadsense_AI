USE ai_smart_road_monitoring_system_application;

/* =========================================================
   TEMP SEQUENCE (1–1000)
   ========================================================= */
DROP TEMPORARY TABLE IF EXISTS seq_numbers;

CREATE TEMPORARY TABLE seq_numbers (n INT PRIMARY KEY);

INSERT INTO seq_numbers (n)
SELECT a.n + b.n * 10 + c.n * 100 + 1
FROM
 (SELECT 0 n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4
  UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) a,
 (SELECT 0 n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4
  UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) b,
 (SELECT 0 n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4
  UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) c
LIMIT 1000;


/* ================= ROLES ================= */
INSERT INTO roles (name, description)
SELECT CONCAT('ROLE_', n), CONCAT('Role ', n) FROM seq_numbers;


/* ================= USERS ================= */
INSERT INTO users (username, password, email, role_id, active)
SELECT
    CONCAT('user_', n),
    CONCAT('$2a$10$password_', n),
    CONCAT('user_', n, '@mail.com'),
    n,
    TRUE
FROM seq_numbers;


/* ================= ROADS ================= */
INSERT INTO roads (road_name, district, state, latitude, longitude)
SELECT
    CONCAT('Road_', n),
    CONCAT('District_', n % 20),
    CONCAT('State_', n % 10),
    23.50 + n * 0.001,
    77.30 + n * 0.001
FROM seq_numbers;


/* ================= POTHOLES (UPDATED) ================= */
INSERT INTO potholes (
    road_id, gps_location, gps_pin,
    latitude, longitude,
    length, width, depth,
    severity, status,
    detected_date, image_path
)
SELECT
    n,
    CONCAT('GPS-', n),
    CONCAT('PIN-', n),
    23.40 + n * 0.001,
    77.20 + n * 0.001,
    ROUND(0.5 + (n % 3), 2),
    ROUND(0.4 + (n % 2), 2),
    ROUND(0.2 + (n % 2), 2),
    ELT((n % 4) + 1, 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'),
    ELT((n % 3) + 1, 'OPEN', 'IN_PROGRESS', 'CLOSED'),
    NOW() - INTERVAL (n % 30) DAY,
    CONCAT('/images/pothole_', n, '.jpg')
FROM seq_numbers;


/* ================= AI PREDICTIONS ================= */
INSERT INTO ai_predictions (pothole_id, model_name, confidence, prediction_label)
SELECT
    n,
    'YOLOv8',
    70 + (n % 30),
    ELT((n % 4) + 1, 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL')
FROM seq_numbers;


/* ================= SENSOR DATA ================= */
INSERT INTO sensor_data (road_id, vibration, speed, temperature, recorded_at)
SELECT
    n,
    1 + (n % 5),
    30 + (n % 70),
    20 + (n % 15),
    NOW() - INTERVAL n MINUTE
FROM seq_numbers;


/* ================= REPAIR ACTIVITY ================= */
INSERT INTO repair_activity (pothole_id, status, assigned_to, repair_date, remarks)
SELECT
    n,
    ELT((n % 3) + 1, 'PENDING', 'IN_PROGRESS', 'COMPLETED'),
    CONCAT('Worker_', n % 50),
    CURDATE() - INTERVAL (n % 30) DAY,
    CONCAT('Repair done for pothole ', n)
FROM seq_numbers;


/* ================= ACTIVITY LOG ================= */
INSERT INTO activity_log (entity, action, message)
SELECT
    'SYSTEM',
    'AUTO_INSERT',
    CONCAT('Log entry ', n)
FROM seq_numbers;


/* ================= DASHBOARD ================= */
INSERT INTO dashboard_district_summary
(district, total_roads, total_potholes, repaired_potholes)
SELECT
    CONCAT('District_', n),
    50 + (n % 50),
    100 + (n % 200),
    40 + (n % 40)
FROM seq_numbers;

INSERT INTO dashboard_pothole_summary
(severity, total_count, district)
SELECT
    ELT((n % 4) + 1, 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'),
    10 + (n % 90),
    CONCAT('District_', n % 20)
FROM seq_numbers;


/* ================= CLEANUP ================= */
DROP TEMPORARY TABLE seq_numbers;
