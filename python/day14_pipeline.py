"""
day14_pipeline.py
-----------------
Python + SQL Integration Pipeline.

Features:
  1. Insert new customer (Create)
  2. Update existing customer's contact (Update)
  3. Delete cancelled installations (Delete)
  4. Read data and generate summary (Read)

Author: [Your Name]
Day 14 - Complete Data Pipeline
"""

import os
import sqlite3
import pandas as pd
from datetime import datetime

# =====================================================
# PATH SETUP
# =====================================================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "solar_program.db")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")


def get_connection():
    """Get DB connection with timeout."""
    # timeout=10 prevents 'database is locked' error
    return sqlite3.connect(DB_PATH, timeout=10)


# =====================================================
# CRUD OPERATIONS
# =====================================================

def insert_new_customer(conn):
    """INSERT: Add a new customer to the database."""
    print("\n[1] INSERT — Adding new customer...")
    
    new_customer = {
        "Customer_ID": "CUST-99999",
        "Customer_Name": "Test New Customer",
        "District": "Dhaka",
        "Region": "Central",
        "Upazila": "Savar",
        "Customer_Type": "Residential",
        "Registration_Date": datetime.now().strftime("%Y-%m-%d"),
        "Contact_Number": "01712345678",
        "Application_Status": "Pending"
    }
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO customers (
                Customer_ID, Customer_Name, District, Region, Upazila,
                Customer_Type, Registration_Date, Contact_Number, Application_Status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            new_customer["Customer_ID"],
            new_customer["Customer_Name"],
            new_customer["District"],
            new_customer["Region"],
            new_customer["Upazila"],
            new_customer["Customer_Type"],
            new_customer["Registration_Date"],
            new_customer["Contact_Number"],
            new_customer["Application_Status"]
        ))
        conn.commit()
        print(f"   ✅ Inserted: {new_customer['Customer_ID']} - {new_customer['Customer_Name']}")
    except sqlite3.IntegrityError as e:
        print(f"   ⚠️  Insert failed (already exists?): {e}")
        conn.rollback()  # Undo the transaction


def update_customer_contact(conn):
    """UPDATE: Change a customer's contact number."""
    print("\n[2] UPDATE — Changing customer contact...")
    
    target_id = "CUST-99999"
    new_contact = "01799999999"
    
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE customers
        SET Contact_Number = ?
        WHERE Customer_ID = ?
    """, (new_contact, target_id))
    
    conn.commit()
    print(f"   ✅ Updated {cursor.rowcount} record(s).")


def delete_cancelled_installations(conn):
    """DELETE: Remove all cancelled installations."""
    print("\n[3] DELETE — Removing cancelled installations...")
    
    # Check how many will be deleted
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM installations WHERE Installation_Status = 'Cancelled'")
    count = cursor.fetchone()[0]
    
    print(f"   Found {count} cancelled installations.")
    
    if count > 0:
        cursor.execute("DELETE FROM installations WHERE Installation_Status = 'Cancelled'")
        conn.commit()
        print(f"   ✅ Deleted {cursor.rowcount} cancelled installations.")
    else:
        print("   No cancelled installations to delete.")


def read_summary(conn):
    """READ: Get a final summary of the database."""
    print("\n[4] READ — Final Database Summary")
    print("   " + "-" * 40)
    
    query = """
        SELECT
            (SELECT COUNT(*) FROM customers) AS Total_Customers,
            (SELECT COUNT(*) FROM installations) AS Total_Installations,
            (SELECT COUNT(*) FROM installations WHERE Installation_Status = 'Completed') AS Completed,
            (SELECT ROUND(SUM(Solar_Capacity_KW), 2) FROM installations) AS Total_KW
    """
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))


def run_kpi_after_pipeline(conn):
    """Verify the pipeline didn't break the data."""
    print("\n[5] VERIFY — Region-wise Capacity After Pipeline")
    print("   " + "-" * 40)
    
    query = """
        SELECT
            c.Region,
            COUNT(i.Installation_ID) AS Installations,
            ROUND(SUM(i.Solar_Capacity_KW), 2) AS Total_KW
        FROM installations i
        JOIN customers c ON i.Customer_ID = c.Customer_ID
        WHERE i.Installation_Status = 'Completed'
        GROUP BY c.Region
        ORDER BY Total_KW DESC
    """
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    return df


# =====================================================
# MAIN
# =====================================================

def main():
    print("=" * 60)
    print("  🌞 DAY 14 — COMPLETE DATA PIPELINE (Python + SQL)")
    print("=" * 60)
    
    conn = get_connection()
    
    try:
        # 1. Insert
        insert_new_customer(conn)
        
        # 2. Update
        update_customer_contact(conn)
        
        # 3. Delete (ক্যান্সেল করা ইনস্টলেশন ডিলিট)
        delete_cancelled_installations(conn)
        
        # 4. Read Summary
        read_summary(conn)
        
        # 5. Verify KPI
        df_region = run_kpi_after_pipeline(conn)
        
        # --- Save to Excel ---
        print("\n💾 Saving final report to Excel...")
        os.makedirs(REPORTS_DIR, exist_ok=True)
        output_file = os.path.join(REPORTS_DIR, "Day14_Pipeline_Report.xlsx")
        
        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            df_region.to_excel(writer, sheet_name="Region_Capacity", index=False)
            
        print(f"   ✅ Saved: {output_file}")
        
    finally:
        conn.close()

    print("\n" + "=" * 60)
    print("  🎉 DAY 14 PIPELINE COMPLETE")
    print("  🎊 WEEK 2 COMPLETED!")
    print("=" * 60)


if __name__ == "__main__":
    main()