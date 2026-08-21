USE ai_smart_road_monitoring_system_application;

/* Delete potholes by status */
DELETE FROM potholes WHERE status = 'REPAIRED';

/* Delete inactive users */
DELETE FROM users WHERE active = FALSE;

/* Delete old sensor data (older than 90 days) */
DELETE FROM sensor_data
WHERE recorded_at < NOW() - INTERVAL 90 DAY;

/* Delete orphan dashboard rows (if any) */
DELETE FROM dashboard_pothole_summary WHERE district IS NULL;
