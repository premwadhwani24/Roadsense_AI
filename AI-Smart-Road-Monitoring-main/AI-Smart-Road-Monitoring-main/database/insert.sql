USE ai_smart_road_monitoring_system_application;

/* =========================================================
   ROLES (FIXED SMALL SET)
   ========================================================= */
INSERT INTO roles (id, name, description) VALUES
(1, 'ADMIN', 'System Administrator'),
(2, 'COLLECTOR', 'District Collector'),
(3, 'MUNICIPAL', 'Municipal Officer'),
(4, 'PWD', 'Public Works Department'),
(5, 'USER', 'Citizen User')
ON DUPLICATE KEY UPDATE name = VALUES(name);


/* =========================================================
   USERS (1000)
   ========================================================= */
INSERT INTO users (username, password, email, role_id, active)
SELECT
    CONCAT('user_', seq),
    '$2a$10$abcdefghijklmnopqrstuv',   -- dummy bcrypt
    CONCAT('user_', seq, '@example.com'),
    (seq % 5) + 1,
    TRUE
FROM (
    SELECT @u := @u + 1 AS seq
    FROM information_schema.tables t1,
         information_schema.tables t2,
         (SELECT @u := 0) x
    LIMIT 1000
) q
ON DUPLICATE KEY UPDATE email = VALUES(email);


/* =========================================================
   ROADS (1000)
   ========================================================= */
INSERT INTO roads (road_name, district, state, latitude, longitude)
SELECT
    CONCAT('Road-', seq),
    CONCAT('District-', (seq % 50) + 1),
    CASE
        WHEN seq % 5 = 0 THEN 'Madhya Pradesh'
        WHEN seq % 5 = 1 THEN 'Uttar Pradesh'
        WHEN seq % 5 = 2 THEN 'Bihar'
        WHEN seq % 5 = 3 THEN 'Maharashtra'
        ELSE 'Rajasthan'
    END,
    ROUND(20 + (seq * 0.005), 6),
    ROUND(75 + (seq * 0.005), 6)
FROM (
    SELECT @r := @r + 1 AS seq
    FROM information_schema.tables t1,
         information_schema.tables t2,
         (SELECT @r := 0) r
    LIMIT 1000
) q;


/* =========================================================
   POTHOLES (1000)
   ========================================================= */
INSERT INTO potholes (
    road_id, gps_location, gps_pin,
    latitude, longitude,
    length, width, depth,
    severity, status,
    detected_date, image_path
)
SELECT
    (seq % 1000) + 1,
    CONCAT('GPS-', seq),
    CONCAT('PIN-', seq),
    ROUND(20 + (seq * 0.004), 6),
    ROUND(75 + (seq * 0.004), 6),
    ROUND(RAND() * 2, 2),
    ROUND(RAND() * 2, 2),
    ROUND(RAND() * 1, 2),
    ELT((seq % 3) + 1, 'LOW', 'MEDIUM', 'HIGH'),
    ELT((seq % 3) + 1, 'OPEN', 'IN_PROGRESS', 'REPAIRED'),
    NOW(),
    CONCAT('uploads/pothole_', seq, '.jpg')
FROM (
    SELECT @p := @p + 1 AS seq
    FROM information_schema.tables t1,
         information_schema.tables t2,
         (SELECT @p := 0) p
    LIMIT 1000
) q;


/* =========================================================
   AI PREDICTIONS (1000)
   ========================================================= */
INSERT INTO ai_predictions (pothole_id, model_name, confidence, prediction_label)
SELECT
    seq,
    'PotholeCNN-v1',
    ROUND(70 + (RAND() * 30), 2),
    ELT((seq % 3) + 1, 'LOW', 'MEDIUM', 'HIGH')
FROM (
    SELECT @a := @a + 1 AS seq
    FROM information_schema.tables t1,
         information_schema.tables t2,
         (SELECT @a := 0) a
    LIMIT 1000
) q;


/* =========================================================
   SENSOR DATA (1000)
   ========================================================= */
INSERT INTO sensor_data (road_id, vibration, speed, temperature, recorded_at)
SELECT
    (seq % 1000) + 1,
    ROUND(RAND() * 10, 2),
    ROUND(20 + RAND() * 60, 2),
    ROUND(20 + RAND() * 15, 2),
    NOW()
FROM (
    SELECT @s := @s + 1 AS seq
    FROM information_schema.tables t1,
         information_schema.tables t2,
         (SELECT @s := 0) s
    LIMIT 1000
) q;


/* =========================================================
   REPAIR ACTIVITY (1000)
   ========================================================= */
INSERT INTO repair_activity (pothole_id, status, assigned_to, repair_date, remarks)
SELECT
    seq,
    ELT((seq % 3) + 1, 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED'),
    CONCAT('Engineer-', (seq % 50) + 1),
    CURDATE(),
    'Auto-generated repair record'
FROM (
    SELECT @ra := @ra + 1 AS seq
    FROM information_schema.tables t1,
         information_schema.tables t2,
         (SELECT @ra := 0) ra
    LIMIT 1000
) q;


/* =========================================================
   ACTIVITY LOG (1000)
   ========================================================= */
INSERT INTO activity_log (entity, action, message)
SELECT
    ELT((seq % 4) + 1, 'ROAD', 'POTHOLE', 'REPAIR', 'USER'),
    'AUTO_INSERT',
    CONCAT('Activity log entry ', seq)
FROM (
    SELECT @al := @al + 1 AS seq
    FROM information_schema.tables t1,
         information_schema.tables t2,
         (SELECT @al := 0) al
    LIMIT 1000
) q;


/* =========================================================
   DASHBOARD DISTRICT SUMMARY (50)
   ========================================================= */
INSERT INTO dashboard_district_summary (district, total_roads, total_potholes, repaired_potholes)
SELECT
    CONCAT('District-', seq),
    20,
    200,
    120
FROM (
    SELECT @d := @d + 1 AS seq
    FROM information_schema.tables, (SELECT @d := 0) d
    LIMIT 50
) q;


/* =========================================================
   DASHBOARD POTHOLE SUMMARY (PER SEVERITY)
   ========================================================= */
INSERT INTO dashboard_pothole_summary (severity, total_count, district)
VALUES
('LOW', 350, 'ALL'),
('MEDIUM', 400, 'ALL'),
('HIGH', 250, 'ALL');
