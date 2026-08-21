USE ai_smart_road_monitoring_system_application;

SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE ai_predictions;
TRUNCATE TABLE repair_activity;
TRUNCATE TABLE sensor_data;
TRUNCATE TABLE potholes;
TRUNCATE TABLE roads;
TRUNCATE TABLE users;
TRUNCATE TABLE roles;
TRUNCATE TABLE activity_log;
TRUNCATE TABLE dashboard_district_summary;
TRUNCATE TABLE dashboard_pothole_summary;

SET FOREIGN_KEY_CHECKS = 1;

/* Reload baseline roles */
INSERT INTO roles (id, name, description) VALUES
(1,'ADMIN','System Administrator'),
(2,'COLLECTOR','District Collector'),
(3,'MUNICIPAL','Municipal Officer'),
(4,'PWD','Public Works Department'),
(5,'USER','Citizen User')
ON DUPLICATE KEY UPDATE name = VALUES(name);
