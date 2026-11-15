# 🌞 Solar Program MIS Analytics System

A complete end-to-end Data Management & MIS (Management Information System) project for a Rooftop Solar Program in Bangladesh (inspired by ESDO's DRS Program). 

This project demonstrates the full data lifecycle: **Data Generation ➔ Cleaning ➔ SQL Database ➔ Python Web App (MIS)**.

## 📸 Project Screenshots


## 🚀 Features
- **Data Generation:** Synthetic dataset of 12,000+ records with realistic data quality issues.
- **Automated Data Pipeline:** Python scripts to clean missing values, fuzzy-match districts, and infer dates.
- **Data Quality System:** Weighted scoring system to measure data health.
- **SQL Database:** Normalized SQLite database with proper constraints (Primary Key, Foreign Key, Checks).
- **MIS Web Application (Streamlit):**
  - Interactive Dashboard (KPIs & Plotly Charts)
  - Customer Database (Search & Add New)
  - Installation Tracking (Update Status)
  - Automated Excel Report Generation.

## 🛠️ Technology Stack
- **Language:** Python 3.10+
- **Data Processing:** Pandas, NumPy
- **Database:** SQLite, SQLAlchemy
- **Web App / UI:** Streamlit, Plotly
- **Data Quality:** Custom Python Pipeline

## 📂 Project Structure
```text
solar-program-mis-analytics/
│
├── data/               # Raw and cleaned CSV files, SQLite database
├── docs/               # Business process and KPI documentation
├── python/             # Data generator, cleaning, and SQL pipeline scripts
├── sql/                # Database schema and KPI queries
├── streamlit_app/      # Web application source code
├── reports/            # Generated Excel reports
└── requirements.txt    # Dependencies
