-- Sub-Saharan Africa Sustainable Development Indicator Portfolio
-- Data source: Yu Han's SSA sustainable development indicator dataset
-- Main table name in DB Browser for SQLite: index_data

-- 1. Preview the working dataset
SELECT
  "Alpha-3 code",
  CountryName_CN,
  Year,
  SDI,
  SDI_Economy,
  SDI_Society,
  SDI_Resource,
  SDI_Ecology,
  Region
FROM index_data
LIMIT 10;

-- 2. Check the time coverage
SELECT
  MIN(Year) AS first_year,
  MAX(Year) AS latest_year,
  COUNT(*) AS total_rows
FROM index_data;

-- 3. Rank countries by SDI in the latest available year
SELECT
  "Alpha-3 code",
  CountryName_CN,
  Year,
  ROUND(SDI, 3) AS SDI,
  ROUND(SDI_Economy, 3) AS economy,
  ROUND(SDI_Society, 3) AS society,
  ROUND(SDI_Resource, 3) AS resource,
  ROUND(SDI_Ecology, 3) AS ecology,
  Region
FROM index_data
WHERE Year = (SELECT MAX(Year) FROM index_data)
ORDER BY SDI DESC
LIMIT 15;

-- 4. Compare regional average SDI in the latest available year
SELECT
  Region,
  COUNT(*) AS country_count,
  ROUND(AVG(SDI), 3) AS avg_sdi,
  ROUND(AVG(SDI_Economy), 3) AS avg_economy,
  ROUND(AVG(SDI_Society), 3) AS avg_society,
  ROUND(AVG(SDI_Resource), 3) AS avg_resource,
  ROUND(AVG(SDI_Ecology), 3) AS avg_ecology
FROM index_data
WHERE Year = (SELECT MAX(Year) FROM index_data)
GROUP BY Region
ORDER BY avg_sdi DESC;

-- 5. Track one country over time: Kenya
SELECT
  "Alpha-3 code",
  CountryName_CN,
  Year,
  ROUND(SDI, 3) AS SDI,
  ROUND(SDI_Economy, 3) AS economy,
  ROUND(SDI_Society, 3) AS society,
  ROUND(SDI_Resource, 3) AS resource,
  ROUND(SDI_Ecology, 3) AS ecology,
  Region
FROM index_data
WHERE "Alpha-3 code" = 'KEN'
ORDER BY Year;

-- 6. Find countries with higher social scores than economic scores
SELECT
  "Alpha-3 code",
  CountryName_CN,
  Year,
  ROUND(SDI_Society - SDI_Economy, 3) AS society_economy_gap,
  ROUND(SDI_Society, 3) AS society,
  ROUND(SDI_Economy, 3) AS economy,
  Region
FROM index_data
WHERE Year = (SELECT MAX(Year) FROM index_data)
ORDER BY society_economy_gap DESC
LIMIT 15;
