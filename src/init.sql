USE ${MYSQL_DATABASE};
SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS weekday (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(8) NOT NULL UNIQUE
);

INSERT INTO weekday (name) VALUES
('月'), ('火'), ('水'), ('木'), ('金'), ('土'), ('日'), ('毎日'), ('土日');

CREATE TABLE IF NOT EXISTS default_task_list(
    default_task_id INT AUTO_INCREMENT PRIMARY KEY,
    task_name VARCHAR(10) NOT NULL,
    weekday_id INT NOT NULL,
    homemaker VARCHAR(10),
    weight INT,
    FOREIGN KEY (weekday_id) REFERENCES weekday(id)
);

INSERT INTO default_task_list (task_name, weekday_id, homemaker, weight)
SELECT d.task_name, w.id, d.homemaker, d.weight
FROM(
    SELECT '料理(朝)/お弁当' AS task_name, '毎日' AS w_name, '母,父' AS homemaker, 5 AS weight UNION ALL
    SELECT '料理(昼)', '土日', '全員', 3 UNION ALL
    SELECT '料理(夜)', '毎日', '母,父', 5 UNION ALL
    SELECT '食器洗い', '毎日', '全員', 3 UNION ALL
    SELECT 'トイレ掃除', '日', '全員', 2 UNION ALL
    SELECT 'お風呂掃除', '毎日', '長男,次女', 2 UNION ALL
    SELECT 'ごみ捨て', '毎日', '全員', 1 UNION ALL
    SELECT '玄関掃除', '日', '全員', 2 UNION ALL
    SELECT '洗濯畳む', '毎日', '長男,次女', 3 UNION ALL
    SELECT '洗濯(干すまで)', '毎日', '母,父', 4 UNION ALL
    SELECT '掃除機(全部屋)', '日', '全員', 3
) AS d
JOIN weekday AS w ON w.name = d.w_name;

COMMIT;