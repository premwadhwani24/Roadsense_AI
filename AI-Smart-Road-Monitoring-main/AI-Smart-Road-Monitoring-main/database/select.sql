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

/* Counts */
SELECT COUNT(*) AS total_users FROM users;
SELECT COUNT(*) AS total_roads FROM roads;
SELECT COUNT(*) AS total_potholes FROM potholes;

/* Dashboard – severity summary */
SELECT severity, COUNT(*) AS total
FROM potholes
GROUP BY severity;

/* Dashboard – district summary */
SELECT r.district,
       COUNT(p.id) AS total_potholes
FROM roads r
LEFT JOIN potholes p ON r.id = p.road_id
GROUP BY r.district;

/* Latest AI predictions */
SELECT p.id, a.model_name, a.confidence, a.prediction_label
FROM potholes p
JOIN ai_predictions a ON p.id = a.pothole_id
ORDER BY a.created_at DESC
LIMIT 10;

/* Repair status */
SELECT status, COUNT(*) FROM repair_activity GROUP BY status;
