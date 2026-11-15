"""
day12_kpi_queries.py
--------------------
Run business KPI queries against the SQLite database.
Export results to Excel for management reporting.

Author: [Your Name]
Day 12 - SQL KPI Queries
"""

import os
import sqlite3
import pandas as pd

# =====================================================
# PATH SETUP
# =====================================================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "solar_program.db")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")


def get_connection():
    """Return SQLite connection."""
    return sqlite3.connect(DB_PATH)


def run_kpi_1_region_capacity(conn):
    """KPI 1: Total Installed Capacity by Region."""
    print("\n" + "=" * 60)
    print("  📊 KPI 1: Total Installed Capacity by Region")
    print("=" * 60)
    
    query = """
        SELECT
            c.Region,
            ROUND(SUM(i.Solar_Capacity_KW), 2) AS Total_KW,
            COUNT(i.Installation_ID) AS Total_Installs
        FROM installations i
        JOIN customers c ON i.Customer_ID = c.Customer_ID
        WHERE i.Installation_Status = 'Completed'
        GROUP BY c.Region
        ORDER BY Total_KW DESC;
    """
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    return df


def run_kpi_2_completion_rate(conn):
    """KPI 2: Completion Rate by District."""
    print("\n" + "=" * 60)
    print("  📊 KPI 2: Top 5 Districts by Completion Rate")
    print("=" * 60)
    
    query = """
        SELECT
            c.District,
            COUNT(i.Installation_ID) AS Total_Applications,
            SUM(CASE WHEN i.Installation_Status = 'Completed' THEN 1 ELSE 0 END) AS Completed,
            ROUND(
                100.0 * SUM(CASE WHEN i.Installation_Status = 'Completed' THEN 1 ELSE 0 END) / COUNT(i.Installation_ID),
                2
            ) AS Completion_Rate_Pct
        FROM installations i
        JOIN customers c ON i.Customer_ID = c.Customer_ID
        GROUP BY c.District
        HAVING Total_Applications > 50
        ORDER BY Completion_Rate_Pct DESC
        LIMIT 5;
    """
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    return df


def run_kpi_3_top_installers(conn):
    """KPI 3: Top Installers by Jobs Completed."""
    print("\n" + "=" * 60)
    print("  📊 KPI 3: Top 10 Installers")
    print("=" * 60)
    
    query = """
        SELECT
            Installer_ID,
            COUNT(Installation_ID) AS Jobs_Completed,
            ROUND(AVG(Solar_Capacity_KW), 2) AS Avg_Capacity_KW
        FROM installations
        WHERE Installation_Status = 'Completed'
        GROUP BY Installer_ID
        ORDER BY Jobs_Completed DESC
        LIMIT 10;
    """
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    return df


def run_kpi_4_monthly_trend(conn):
    """KPI 4: Monthly Installation Trend."""
    print("\n" + "=" * 60)
    print("  📊 KPI 4: Monthly Installation Trend (Recent 12 Months)")
    print("=" * 60)
    
    query = """
        SELECT
            strftime('%Y-%m', Installation_Date) AS Month,
            COUNT(Installation_ID) AS Installations,
            ROUND(SUM(Solar_Capacity_KW), 2) AS Total_KW
        FROM installations
        WHERE Installation_Status = 'Completed'
          AND Installation_Date IS NOT NULL
          AND Installation_Date >= '2024-11-01'
        GROUP BY Month
        ORDER BY Month ASC;
    """
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    return df


def run_kpi_5_pending_commissioning(conn):
    """KPI 5: Installations Pending Commissioning."""
    print("\n" + "=" * 60)
    print("  📊 KPI 5: Installations Pending Commissioning (Top 10)")
    print("=" * 60)
    
    query = """
        SELECT
            i.Installation_ID,
            c.Customer_Name,
            c.District,
            i.Installation_Date
        FROM installations i
        JOIN customers c ON i.Customer_ID = c.Customer_ID
        LEFT JOIN commissioning co ON i.Customer_ID = co.Customer_ID
        WHERE i.Installation_Status = 'Completed'
          AND (co.Commissioning_Status IS NULL OR co.Commissioning_Status != 'Completed')
        ORDER BY i.Installation_Date ASC
        LIMIT 10;
    """
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    return df


def main():
    print("=" * 60)
    print("  🌞 DAY 12 — BUSINESS KPI QUERIES")
    print("=" * 60)

    conn = get_connection()
    
    try:
        # Run all KPIs
        df1 = run_kpi_1_region_capacity(conn)
        df2 = run_kpi_2_completion_rate(conn)
        df3 = run_kpi_3_top_installers(conn)
        df4 = run_kpi_4_monthly_trend(conn)
        df5 = run_kpi_5_pending_commissioning(conn)

        # Export to Excel
        print("\n💾 Exporting KPIs to Excel...")
        os.makedirs(REPORTS_DIR, exist_ok=True)
        output_file = os.path.join(REPORTS_DIR, "Day12_Business_KPIs.xlsx")
        
        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            df1.to_excel(writer, sheet_name="KPI1_Region_Capacity", index=False)
            df2.to_excel(writer, sheet_name="KPI2_Completion_Rate", index=False)
            df3.to_excel(writer, sheet_name="KPI3_Top_Installers", index=False)
            df4.to_excel(writer, sheet_name="KPI4_Monthly_Trend", index=False)
            df5.to_excel(writer, sheet_name="KPI5_Pending_Comm", index=False)
            
        print(f"   ✅ Saved: {output_file}")

    finally:
        conn.close()

    print("\n" + "=" * 60)
    print("  🎉 DAY 12 KPI QUERIES COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()