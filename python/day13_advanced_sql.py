"""
day13_advanced_sql.py
---------------------
Run advanced SQL queries (JOINs, Subqueries, Views) and export to Excel.

Author: [Your Name]
Day 13 - Advanced SQL
"""

import os
import sqlite3
import pandas as pd

# =====================================================
# PATHS
# =====================================================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "solar_program.db")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")


def run_query(title, sql, conn):
    """Execute a SQL query and return DataFrame."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)
    df = pd.read_sql_query(sql, conn)
    print(df.head(10).to_string(index=False))  # print first 10 rows
    if len(df) > 10:
        print(f"   ... ({len(df) - 10} more rows)")
    return df


def main():
    print("=" * 60)
    print("  🌞 DAY 13 — ADVANCED SQL (JOINs, Subqueries, Views)")
    print("=" * 60)

    conn = sqlite3.connect(DB_PATH)
    results = {}

    try:
        # 1. INNER JOIN
        results["INNER_JOIN"] = run_query(
            "1. INNER JOIN — Customers with Installations",
            """
            SELECT c.Customer_Name, c.District, i.Solar_Capacity_KW, i.Installation_Status
            FROM customers c
            INNER JOIN installations i ON c.Customer_ID = i.Customer_ID
            LIMIT 10;
            """,
            conn
        )

        # 2. LEFT JOIN
        results["LEFT_JOIN"] = run_query(
            "2. LEFT JOIN — Customers WITHOUT Installations",
            """
            SELECT c.Customer_ID, c.Customer_Name, c.District
            FROM customers c
            LEFT JOIN installations i ON c.Customer_ID = i.Customer_ID
            WHERE i.Installation_ID IS NULL
            LIMIT 10;
            """,
            conn
        )

        # 3. 3-Table JOIN
        results["THREE_TABLE_JOIN"] = run_query(
            "3. 3-Table JOIN — Full Customer Journey",
            """
            SELECT c.Customer_Name, c.District,
                   i.Installation_Date, i.Solar_Capacity_KW,
                   co.Commissioning_Date, co.Commissioning_Status
            FROM customers c
            LEFT JOIN installations i ON c.Customer_ID = i.Customer_ID
            LEFT JOIN commissioning co ON c.Customer_ID = co.Customer_ID
            LIMIT 10;
            """,
            conn
        )

        # 4. Subquery
        results["SUBQUERY"] = run_query(
            "4. Subquery — Installations Above Average Capacity",
            """
            SELECT Installation_ID, Customer_ID, Solar_Capacity_KW
            FROM installations
            WHERE Solar_Capacity_KW > (SELECT AVG(Solar_Capacity_KW) FROM installations)
            ORDER BY Solar_Capacity_KW DESC
            LIMIT 10;
            """,
            conn
        )

        # 5. Create and Use View
        print("\n🔧 Creating view: vw_district_performance...")
        conn.executescript("""
            DROP VIEW IF EXISTS vw_district_performance;
            CREATE VIEW vw_district_performance AS
            SELECT
                c.District, c.Region,
                COUNT(DISTINCT i.Installation_ID) AS Total_Installations,
                ROUND(SUM(i.Solar_Capacity_KW), 2) AS Total_KW,
                SUM(CASE WHEN i.Installation_Status = 'Completed' THEN 1 ELSE 0 END) AS Completed_Count
            FROM customers c
            LEFT JOIN installations i ON c.Customer_ID = i.Customer_ID
            GROUP BY c.District, c.Region;
        """)
        conn.commit()

        results["VIEW"] = run_query(
            "5. Using View — District Performance",
            """
            SELECT * FROM vw_district_performance
            ORDER BY Total_KW DESC
            LIMIT 10;
            """,
            conn
        )

    finally:
        conn.close()

    # --- Export to Excel ---
    print("\n" + "=" * 60)
    print("  💾 Exporting to Excel...")
    print("=" * 60)
    
    os.makedirs(REPORTS_DIR, exist_ok=True)
    output_file = os.path.join(REPORTS_DIR, "Day13_Advanced_SQL.xlsx")
    
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        for sheet_name, df in results.items():
            df.to_excel(writer, sheet_name=sheet_name[:31], index=False)  # Excel sheet name max 31 chars
            
    print(f"   ✅ Saved: {output_file}")

    print("\n" + "=" * 60)
    print("  🎉 DAY 13 ADVANCED SQL COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()