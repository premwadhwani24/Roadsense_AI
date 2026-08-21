USE ai_smart_road_monitoring_system_application;

/* Update pothole status */
UPDATE potholes
SET status = 'IN_PROGRESS'
WHERE id BETWEEN 1 AND 50;

/* Mark completed repairs */
UPDATE repair_activity
SET status = 'COMPLETED',
    remarks = 'Repair finished successfully'
WHERE status = 'IN_PROGRESS';

/* Disable old users */
UPDATE users
SET active = FALSE
WHERE id > 900;

/* Refresh dashboard summaries */
UPDATE dashboard_district_summary
SET last_updated = NOW();

UPDATE dashboard_pothole_summary
SET last_updated = NOW();
