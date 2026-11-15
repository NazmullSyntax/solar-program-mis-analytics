-- =====================================================
-- Solar Program MIS — Database Schema
-- Day 11: SQL Database Design
-- Database: SQLite
-- =====================================================

-- Drop tables if they exist (for re-runs)
DROP TABLE IF EXISTS commissioning;
DROP TABLE IF EXISTS installations;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS regional_reports;

-- =====================================================
-- TABLE 1: CUSTOMERS
-- =====================================================
CREATE TABLE customers (
    Customer_ID        TEXT PRIMARY KEY,
    Customer_Name      TEXT NOT NULL,
    District           TEXT,
    Region             TEXT,
    Upazila            TEXT,
    Customer_Type      TEXT CHECK (Customer_Type IN
                            ('Residential', 'Commercial', 'Institutional', 'Industrial')),
    Registration_Date  DATE,
    Contact_Number     TEXT DEFAULT 'MISSING',
    Application_Status TEXT CHECK (Application_Status IN
                            ('Pending', 'Approved', 'Rejected', 'Completed')),
    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for fast lookup
CREATE INDEX idx_customers_district ON customers(District);
CREATE INDEX idx_customers_region ON customers(Region);
CREATE INDEX idx_customers_status ON customers(Application_Status);

-- =====================================================
-- TABLE 2: INSTALLATIONS
-- =====================================================
CREATE TABLE installations (
    Installation_ID   TEXT PRIMARY KEY,
    Customer_ID       TEXT NOT NULL,
    Solar_Capacity_KW REAL CHECK (Solar_Capacity_KW IS NULL OR Solar_Capacity_KW > 0),
    Installation_Date DATE,
    Installation_Status TEXT CHECK (Installation_Status IN
                            ('Planned', 'In_Progress', 'Completed', 'Cancelled')),
    Installer_ID      TEXT,
    Installation_Cost REAL CHECK (Installation_Cost IS NULL OR Installation_Cost >= 0),
    Inspection_Status TEXT CHECK (Inspection_Status IN
                            ('Pending', 'Passed', 'Failed')),
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Customer_ID) REFERENCES customers(Customer_ID)
);

CREATE INDEX idx_installations_district ON installations(Customer_ID);
CREATE INDEX idx_installations_status ON installations(Installation_Status);

-- =====================================================
-- TABLE 3: COMMISSIONING
-- =====================================================
CREATE TABLE commissioning (
    Commissioning_ID    TEXT PRIMARY KEY,
    Customer_ID         TEXT NOT NULL,
    Commissioning_Date  DATE,
    Commissioning_Status TEXT CHECK (Commissioning_Status IN
                            ('Pending', 'Completed', 'Failed')),
    System_Test_Result  TEXT CHECK (System_Test_Result IN
                            ('Pass', 'Fail') OR System_Test_Result IS NULL),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Customer_ID) REFERENCES customers(Customer_ID)
);

CREATE INDEX idx_comm_status ON commissioning(Commissioning_Status);

-- =====================================================
-- TABLE 4: REGIONAL_REPORTS
-- =====================================================
CREATE TABLE regional_reports (
    Report_ID              TEXT PRIMARY KEY,
    Region                 TEXT NOT NULL,
    District               TEXT NOT NULL,
    Report_Date            DATE,
    Submitted_Installations INTEGER,
    Verified_Installations  INTEGER,
    Pending_Installations   INTEGER,
    Report_Status          TEXT CHECK (Report_Status IN
                            ('Submitted', 'Verified', 'Rejected', 'Pending')),
    created_at             TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reports_region ON regional_reports(Region);
CREATE INDEX idx_reports_date ON regional_reports(Report_Date);

-- =====================================================
-- VIEWS (Pre-built queries)
-- =====================================================

-- District summary view
CREATE VIEW vw_district_summary AS
SELECT
    c.District,
    c.Region,
    COUNT(DISTINCT c.Customer_ID) AS total_customers,
    COUNT(DISTINCT i.Installation_ID) AS total_installations,
    COALESCE(SUM(i.Solar_Capacity_KW), 0) AS total_kw
FROM customers c
LEFT JOIN installations i ON c.Customer_ID = i.Customer_ID
GROUP BY c.District, c.Region;

-- Completed installations view
CREATE VIEW vw_completed_installations AS
SELECT
    i.Installation_ID,
    i.Customer_ID,
    c.Customer_Name,
    c.District,
    c.Region,
    i.Solar_Capacity_KW,
    i.Installation_Date,
    i.Inspection_Status,
    co.Commissioning_Status,
    co.Commissioning_Date
FROM installations i
JOIN customers c ON i.Customer_ID = c.Customer_ID
LEFT JOIN commissioning co ON c.Customer_ID = co.Customer_ID
WHERE i.Installation_Status = 'Completed';