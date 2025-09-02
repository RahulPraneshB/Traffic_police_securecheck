-- database/queries.sql
-- SecureCheck Capstone: Full SQL Query List

-- 🚗 VEHICLE-BASED

-- 1. Top 10 vehicle numbers involved in drug-related stops
SELECT vehicle_number, COUNT(*) AS drug_related_count
FROM trafficlogs
WHERE drugs_related_stop = TRUE
GROUP BY vehicle_number
ORDER BY drug_related_count DESC
LIMIT 10;

-- 2. Vehicles most frequently searched
SELECT vehicle_number, COUNT(*) AS search_count
FROM trafficlogs
WHERE search_conducted = TRUE
GROUP BY vehicle_number
ORDER BY search_count DESC
LIMIT 10;


-- 🧍 DEMOGRAPHIC-BASED

-- 3. Driver age group with highest arrest rate
SELECT 
  CASE 
    WHEN driver_age_raw < 18 THEN '<18'
    WHEN driver_age_raw BETWEEN 18 AND 25 THEN '18-25'
    WHEN driver_age_raw BETWEEN 26 AND 40 THEN '26-40'
    WHEN driver_age_raw BETWEEN 41 AND 60 THEN '41-60'
    ELSE '60+'
  END AS age_group,
  COUNT(*) AS total_stops,
  SUM(is_arrested) AS total_arrests,
  ROUND(SUM(is_arrested)*100.0 / COUNT(*), 2) AS arrest_rate
FROM trafficlogs
GROUP BY age_group
ORDER BY arrest_rate DESC;

-- 4. Gender distribution by country
SELECT country_name, driver_gender, COUNT(*) AS count
FROM trafficlogs
GROUP BY country_name, driver_gender
ORDER BY country_name, count DESC;

-- 5. Highest search rate by race-gender combo
SELECT driver_race, driver_gender,
  COUNT(*) AS total_stops,
  SUM(search_conducted) AS total_searches,
  ROUND(SUM(search_conducted)*100.0 / COUNT(*), 2) AS search_rate
FROM trafficlogs
GROUP BY driver_race, driver_gender
ORDER BY search_rate DESC
LIMIT 1;


-- 🕒 TIME & DURATION

-- 6. Most common time of day for stops
SELECT HOUR(stop_time) AS hour_of_day,
       COUNT(*) AS stop_count
FROM trafficlogs
GROUP BY hour_of_day
ORDER BY stop_count DESC;

-- 7. Average stop duration per violation
SELECT violation, stop_duration, COUNT(*) AS stop_count
FROM trafficlogs
GROUP BY violation, stop_duration
ORDER BY violation;

-- 8. Night vs day arrest comparison
SELECT 
  CASE 
    WHEN HOUR(stop_time) BETWEEN 6 AND 18 THEN 'Day'
    ELSE 'Night'
  END AS time_period,
  COUNT(*) AS total_stops,
  SUM(is_arrested) AS arrests,
  ROUND(SUM(is_arrested)*100.0 / COUNT(*), 2) AS arrest_rate
FROM trafficlogs
GROUP BY time_period;


-- ⚖️ VIOLATION-BASED

-- 9. Search and arrest rates by violation
SELECT violation,
       COUNT(*) AS total,
       SUM(search_conducted) AS searches,
       SUM(is_arrested) AS arrests,
       ROUND(SUM(search_conducted)*100.0 / COUNT(*), 2) AS search_rate,
       ROUND(SUM(is_arrested)*100.0 / COUNT(*), 2) AS arrest_rate
FROM trafficlogs
GROUP BY violation
ORDER BY search_rate DESC;

-- 10. Most common violations under age 25
SELECT violation, COUNT(*) AS count
FROM trafficlogs
WHERE driver_age_raw < 25
GROUP BY violation
ORDER BY count DESC;

-- 11. Violations rarely leading to search or arrest
SELECT violation, COUNT(*) AS total,
       SUM(search_conducted) AS searches,
       SUM(is_arrested) AS arrests
FROM trafficlogs
GROUP BY violation
HAVING searches = 0 AND arrests = 0;


-- 🌍 LOCATION-BASED

-- 12. Countries with highest drug-related stop rate
SELECT country_name,
       COUNT(*) AS total_stops,
       SUM(drugs_related_stop) AS drug_related,
       ROUND(SUM(drugs_related_stop)*100.0 / COUNT(*), 2) AS drug_stop_rate
FROM trafficlogs
GROUP BY country_name
ORDER BY drug_stop_rate DESC;

-- 13. Arrest rate by country and violation
SELECT country_name, violation,
       COUNT(*) AS total,
       SUM(is_arrested) AS arrests,
       ROUND(SUM(is_arrested)*100.0 / COUNT(*), 2) AS arrest_rate
FROM trafficlogs
GROUP BY country_name, violation
ORDER BY arrest_rate DESC;

-- 14. Country with most searches conducted
SELECT country_name, COUNT(*) AS search_count
FROM trafficlogs
WHERE search_conducted = TRUE
GROUP BY country_name
ORDER BY search_count DESC
LIMIT 1;


-- 🧠 COMPLEX QUERIES

-- 15. Yearly stops and arrests per country
SELECT country_name, YEAR(stop_date) AS year,
       COUNT(*) AS total_stops,
       SUM(is_arrested) AS arrests
FROM trafficlogs
GROUP BY country_name, YEAR(stop_date)
ORDER BY country_name, year;

-- 16. Violation trends by age and race
SELECT driver_race, driver_age_raw, violation, COUNT(*) AS total
FROM trafficlogs
GROUP BY driver_race, driver_age_raw, violation
ORDER BY total DESC;

-- 17. Time pattern analysis (year, month, hour)
SELECT 
  YEAR(stop_date) AS year,
  MONTH(stop_date) AS month,
  HOUR(stop_time) AS hour,
  COUNT(*) AS stops
FROM trafficlogs
GROUP BY year, month, hour
ORDER BY year, month, hour;

-- 18. Violations with high search/arrest rates
SELECT violation,
       COUNT(*) AS total,
       SUM(search_conducted) AS searches,
       SUM(is_arrested) AS arrests,
       ROUND(SUM(search_conducted)*100.0 / COUNT(*), 2) AS search_rate,
       ROUND(SUM(is_arrested)*100.0 / COUNT(*), 2) AS arrest_rate
FROM trafficlogs
GROUP BY violation
HAVING search_rate > 50 OR arrest_rate > 50
ORDER BY arrest_rate DESC;

-- 19. Driver demographics by country
SELECT country_name, driver_gender, driver_race,
       ROUND(AVG(driver_age_raw), 1) AS avg_age,
       COUNT(*) AS total
FROM trafficlogs
GROUP BY country_name, driver_gender, driver_race;

-- 20. Top 5 violations with highest arrest rates
SELECT violation,
       COUNT(*) AS total,
       SUM(is_arrested) AS arrests,
       ROUND(SUM(is_arrested)*100.0 / COUNT(*), 2) AS arrest_rate
FROM trafficlogs
GROUP BY violation
ORDER BY arrest_rate DESC
LIMIT 5;
