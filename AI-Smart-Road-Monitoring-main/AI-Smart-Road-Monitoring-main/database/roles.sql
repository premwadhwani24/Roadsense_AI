INSERT INTO roads (road_name, district, state, latitude, longitude)
SELECT
  CONCAT('Road_', seq),
  CONCAT('District_', seq % 20),
  'State_X',
  23.000000 + RAND(),
  85.000000 + RAND()
FROM (
  SELECT @r := @r + 1 AS seq
  FROM information_schema.tables,
       (SELECT @r := 0) r
  LIMIT 1000
) t;
