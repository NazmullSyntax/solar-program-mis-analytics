-- =====================================================
-- Day 12: Business KPI Queries
-- =====================================================

-- KPI 1: Region Capacity
SELECT c.Region, ROUND(SUM(i.Solar_Capacity_KW), 2) AS Total_KW
FROM installations i
JOIN customers c ON i.Customer_ID = c.Customer_ID
WHERE i.Installation_Status = 'Completed'
GROUP BY c.Region;

-- KPI 2: District Completion Rate
SELECT c.District, 
       COUNT(i.Installation_ID) AS Total,
       ROUND(100.0 * SUM(CASE WHEN i.Installation_Status = 'Completed' THEN 1 ELSE 0 END) / COUNT(i.Installation_ID), 2) AS Rate_Pct
FROM installations i
JOIN customers c ON i.Customer_ID = c.Customer_ID
GROUP BY c.District
HAVING Total > 50
ORDER BY Rate_Pct DESC;

-- KPI 3: Top Installers
SELECT Installer_ID, COUNT(Installation_ID) AS Jobs
FROM installations
WHERE Installation_Status = 'Completed'
GROUP BY Installer_ID
ORDER BY Jobs DESC LIMIT 10;

-- KPI 4: Monthly Trend
SELECT strftime('%Y-%m', Installation_Date) AS Month, COUNT(Installation_ID) AS Count
FROM installations
WHERE Installation_Status = 'Completed' AND Installation_Date IS NOT NULL
GROUP BY Month ORDER BY Month;

-- KPI 5: Pending Commissioning
SELECT i.Installation_ID, c.Customer_Name, c.District
FROM installations i
JOIN customers c ON i.Customer_ID = c.Customer_ID
LEFT JOIN commissioning co ON i.Customer_ID = co.Customer_ID
WHERE i.Installation_Status = 'Completed'
  AND (co.Commissioning_Status IS NULL OR co.Commissioning_Status != 'Completed')
LIMIT 10;