INSERT INTO repair_activity (
  pothole_id, status, assigned_to, repair_date, remarks
)
SELECT
  seq,
  'COMPLETED',
  CONCAT('Engineer_', seq % 10),
  CURDATE(),
  'Routine maintenance'
FROM (
  SELECT @x := @x + 1 AS seq
  FROM information_schema.tables,
       (SELECT @x := 0) r
  LIMIT 1000
) t;
