INSERT INTO potholes (
  road_id, gps_location, gps_pin,
  latitude, longitude,
  length, width, depth,
  severity, status,
  detected_date, image_path
)
SELECT
  (seq % 1000) + 1,
  'GPS_LOC',
  'PIN',
  23.0 + RAND(),
  85.0 + RAND(),
  ROUND(RAND()*2,2),
  ROUND(RAND()*2,2),
  ROUND(RAND()*1,2),
  ELT(1 + (seq % 3), 'LOW', 'MEDIUM', 'HIGH'),
  ELT(1 + (seq % 3), 'OPEN', 'IN_PROGRESS', 'REPAIRED'),
  NOW(),
  CONCAT('uploads/images/pothole_', seq, '.jpg')
FROM (
  SELECT @p := @p + 1 AS seq
  FROM information_schema.tables,
       (SELECT @p := 0) r
  LIMIT 1000
) t;
