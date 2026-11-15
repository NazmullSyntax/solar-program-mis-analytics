"""
query_demo.py
-------------
Demo SQL queries against the database.
"""
import os
import sqlite3
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "solar_program.db")


def run_query(title, sql):
    """Execute query and print result."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print("=" * 60)

    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(sql, conn)
        print(df.to_string(index=False))
        print(f"\n   ({len(df)} rows)")
    finally:
        conn.close()


def main():
    # Query 1: Simple select
    run_query("1. First 5 customers", """
        SELECT Customer_ID, Customer_Name, District, Region
        FROM customers
        LIMIT 5
    """)

    # Query 2: WHERE clause
    run_query("2. Completed installations in Dhaka", """
        SELECT i.Installation_ID, c.Customer_Name, i.Solar_Capacity_KW
        FROM installations i
        JOIN customers c ON i.Customer_ID = c.Customer_ID
        WHERE c.District = 'Dhaka'
          AND i.Installation_Status = 'Completed'
        LIMIT 5
    """)

    # Query 3: GROUP BY
    run_query("3. Installation count by status", """
        SELECT Installation_Status, COUNT(*) AS count
        FROM installations
        GROUP BY Installation_Status
        ORDER BY count DESC
    """)

    # Query 4: Aggregate + JOIN
    run_query("4. Region-wise summary", """
        SELECT
            c.Region,
            COUNT(DISTINCT i.Installation_ID) AS installations,
            ROUND(SUM(i.Solar_Capacity_KW), 2) AS total_kw,
            ROUND(AVG(i.Solar_Capacity_KW), 2) AS avg_kw
        FROM installations i
        JOIN customers c ON i.Customer_ID = c.Customer_ID
        GROUP BY c.Region
        ORDER BY installations DESC
    """)

    # Query 5: View usage
    run_query("5. Using pre-built view", """
        SELECT * FROM vw_district_summary
        WHERE total_installations > 250
        ORDER BY total_installations DESC
    """)


if __name__ == "__main__":
    main()