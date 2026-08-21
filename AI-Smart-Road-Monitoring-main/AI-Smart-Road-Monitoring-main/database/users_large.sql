TRUNCATE TABLE users;

INSERT INTO users (username, password, email, role_id, active)
SELECT
  CONCAT('user_', seq),
  '$2a$10$abcdefghijklmnopqrstuv',
  CONCAT('user_', seq, '@example.com'),
  (seq % 5) + 1,
  TRUE
FROM (
  SELECT @row := @row + 1 AS seq
  FROM information_schema.tables t1,
       information_schema.tables t2,
       (SELECT @row := 0) r
  LIMIT 1000
) x;
