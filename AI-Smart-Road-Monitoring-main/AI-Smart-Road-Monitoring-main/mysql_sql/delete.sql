USE ai_smart_road_monitoring_system_application;

/* =========================================================
   CLEAN OLD LOG DATA
   ========================================================= */
DELETE FROM activity_log
WHERE created_at < NOW() - INTERVAL 30 DAY;


/* =========================================================
   CLEAN OLD SENSOR DATA
   ========================================================= */
DELETE FROM sensor_data
WHERE recorded_at < NOW() - INTERVAL 90 DAY;


/* =========================================================
   DELETE TEST / DUMMY USER
   ========================================================= */
DELETE FROM users
WHERE username = 'user_1000';


/* =========================================================
   DELETE A POTHOLE SAFELY (WITH DEPENDENCIES)
   ========================================================= */
DELETE FROM ai_predictions WHERE pothole_id = 100;
DELETE FROM repair_activity WHERE pothole_id = 100;
DELETE FROM potholes WHERE id = 100;


/* =========================================================
   CLEAN EMPTY DASHBOARD ROWS
   ========================================================= */
DELETE FROM dashboard_pothole_summary
WHERE total_count = 0;
