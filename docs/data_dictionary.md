# Data Dictionary (Draft — will be finalized on Day 3)

## Table: customers
| Column | Type | Description | Example |
|--------|------|-------------|---------|
| Customer_ID | TEXT (PK) | Unique customer identifier | CUST-00001 |
| Customer_Name | TEXT | Full name (synthetic) | Rahim Uddin |
| District | TEXT | District name | Dhaka |
| Region | TEXT | Region name | Central |
| Upazila | TEXT | Sub-district | Savar |
| Customer_Type | TEXT | Type of customer | Residential |
| Registration_Date | DATE | Date of registration | 2024-03-15 |
| Contact_Number | TEXT | Phone (synthetic) | 01711-XXXXXX |
| Application_Status | TEXT | Current status | Approved |

## Table: installations
| Column | Type | Description |
|--------|------|-------------|
| Installation_ID | TEXT (PK) | Unique installation ID |
| Customer_ID | TEXT (FK) | Links to customers |
| Solar_Capacity_KW | DECIMAL | System size in KW |
| Installation_Date | DATE | Date installed |
| Installation_Status | TEXT | Current status |
| Installer_ID | TEXT | Technician ID |
| Installation_Cost | DECIMAL | Cost in BDT |
| Inspection_Status | TEXT | Quality check status |

## Table: commissioning
| Column | Type | Description |
|--------|------|-------------|
| Commissioning_ID | TEXT (PK) | Unique ID |
| Customer_ID | TEXT (FK) | Links to customers |
| Commissioning_Date | DATE | Date commissioned |
| Commissioning_Status | TEXT | Current status |
| System_Test_Result | TEXT | Pass/Fail |

## Table: regional_reports
| Column | Type | Description |
|--------|------|-------------|
| Report_ID | TEXT (PK) | Unique report ID |
| Region | TEXT | Reporting region |
| District | TEXT | Reporting district |
| Report_Date | DATE | Date of report |
| Submitted_Installations | INT | # submitted |
| Verified_Installations | INT | # verified |
| Pending_Installations | INT | # pending |
| Report_Status | TEXT | Status |