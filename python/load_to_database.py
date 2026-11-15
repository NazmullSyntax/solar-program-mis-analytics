"""
load_to_database.py
-------------------
Load cleaned CSV data into SQLite database.

Steps:
  1. Read schema from sql/01_schema.sql
  2. Create SQLite database
  3. Load all 4 tables from cleaned CSVs
  4. Verify row counts

Author: [Your Name]
Day 11 - SQL Database
"""

import os
import sqlite3
import pandas as pd

# =====================================================
# PATHS
# =====================================================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEANED_DIR = os.path.join(PROJECT_ROOT, "data", "cleaned")
SQL_DIR = os.path.join(PROJECT_ROOT, "sql")
DB_PATH = os.path.join(PROJECT_ROOT, "data", "solar_program.db")


def load_schema():
    """Read schema SQL file."""
    schema_path = os.path.join(SQL_DIR, "01_schema.sql")
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema not found: {schema_path}")

    with open(schema_path, "r", encoding="utf-8") as f:
        return f.read()


def execute_schema(schema_sql):
    """Execute schema creation SQL."""
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(schema_sql)
        conn.commit()
        print("   ✅ Schema created successfully")
    finally:
        conn.close()


def load_data():
    """Load CSVs into their respective tables."""
    tables = {
        "customers": "customers_v2.csv",
        "installations": "installations_v2.csv",
        "commissioning": "commissioning_v2.csv",
        "regional_reports": "regional_reports_v2.csv",
    }

    conn = sqlite3.connect(DB_PATH)
    try:
        for table_name, csv_file in tables.items():
            csv_path = os.path.join(CLEANED_DIR, csv_file)
            if not os.path.exists(csv_path):
                print(f"   ⚠️  Skipped (not found): {csv_path}")
                continue

            df = pd.read_csv(csv_path)
            df.to_sql(table_name, conn, if_exists="append", index=False)
            print(f"   ✅ {table_name:20s} ← {len(df):>6,} rows")

        conn.commit()
    finally:
        conn.close()


def verify():
    """Verify row counts and run a sample query."""
    conn = sqlite3.connect(DB_PATH)
    try:
        print("\n📊 Database verification:")
        print("   " + "-" * 45)
        for table in ["customers", "installations", "commissioning", "regional_reports"]:
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"   {table:20s}: {count:>6,} rows")

        # Sample query: District-wise top 5
        print("\n📊 Top 5 districts (from database):")
        print("   " + "-" * 45)
        query = """
            SELECT
                c.District,
                COUNT(DISTINCT i.Installation_ID) AS installations,
                ROUND(SUM(i.Solar_Capacity_KW), 2) AS total_kw
            FROM installations i
            JOIN customers c ON i.Customer_ID = c.Customer_ID
            GROUP BY c.District
            ORDER BY installations DESC
            LIMIT 5
        """
        result = pd.read_sql_query(query, conn)
        print(result.to_string(index=False))

    finally:
        conn.close()


def main():
    print("=" * 60)
    print("  🌞 DAY 11 — LOAD DATA TO SQL DATABASE")
    print("=" * 60)
    print(f"\n📁 Database: {DB_PATH}")

    # Step 1: Read schema
    print("\n🔧 Reading SQL schema...")
    schema = load_schema()

    # Step 2: Execute schema (creates tables + indexes + views)
    print("🔧 Creating tables + indexes + views...")
    execute_schema(schema)

    # Step 3: Load CSV data
    print("\n📂 Loading CSV data into tables...")
    load_data()

    # Step 4: Verify
    verify()

    print("\n" + "=" * 60)
    print("  🎉 DAY 11 DATABASE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()