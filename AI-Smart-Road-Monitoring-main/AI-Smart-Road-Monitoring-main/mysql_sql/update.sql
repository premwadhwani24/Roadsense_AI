USE ai_smart_road_monitoring_system_application;

/* =========================================================
   USER MANAGEMENT
   ========================================================= */
-- Deactivate a user
UPDATE users
SET active = FALSE
WHERE id = 10;

-- Change user role
UPDATE users
SET role_id = 2
WHERE id = 5;


/* =========================================================
   POTHOLE STATUS & SEVERITY UPDATE
   ========================================================= */
UPDATE potholes
SET
    severity = 'CRITICAL',
    status = 'IN_PROGRESS'
WHERE id = 25;


/* =========================================================
   UPDATE POTHOLE DIMENSIONS (AI RE-MEASUREMENT)
   ========================================================= */
UPDATE potholes
SET
    length = 1.8,
    width = 1.2,
    depth = 0.6
WHERE id = 25;


/* =========================================================
   UPDATE AI CONFIDENCE
   ========================================================= */
UPDATE ai_predictions
SET confidence = 96.75
WHERE pothole_id = 25;


/* =========================================================
   COMPLETE REPAIR ACTIVITY
   ========================================================= */
UPDATE repair_activity
SET
    status = 'COMPLETED',
    remarks = 'Repair completed successfully'
WHERE pothole_id = 25;


/* =========================================================
   DASHBOARD MAINTENANCE
   ========================================================= */
UPDATE dashboard_district_summary
SET
    repaired_potholes = repaired_potholes + 1,
    last_updated = CURRENT_TIMESTAMP
WHERE district = 'District_5';
