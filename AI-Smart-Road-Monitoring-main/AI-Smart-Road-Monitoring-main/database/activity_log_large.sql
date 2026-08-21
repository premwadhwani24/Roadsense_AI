INSERT INTO activity_log (entity, action, message)
SELECT
  'POTHOLE',
  'CREATE',
  CONCAT('Auto generated pothole #', seq)
FROM (
  SELECT @a := @a + 1 AS seq
  FROM information_schema.tables,
       (SELECT @a := 0) r
  LIMIT 1000
) t;
