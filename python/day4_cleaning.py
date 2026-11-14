"""
day4_cleaning.py
----------------
Basic cleaning operations for Day 4.
Uses FIXED SIMULATION_DATE for consistency.

Author: [Your Name]
Day 4 - Excel Data Cleaning
"""

import os
import pandas as pd
from datetime import datetime

# =====================================================
# FIXED SIMULATION DATE (must match data_generator.py)
# =====================================================
SIMULATION_DATE = pd.Timestamp("2025-11-15")

# =====================================================
# PATH SETUP
# =====================================================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
CLEANED_DIR = os.path.join(PROJECT_ROOT, "data", "cleaned")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")


REGION_MAP = {
    "Rangpur": "North", "Dinajpur": "North",
    "Bogura": "North", "Rajshahi": "North",
    "Dhaka": "Central", "Gazipur": "Central",
    "Tangail": "Central", "Mymensingh": "Central",
    "Chattogram": "South", "Cox'S Bazar": "South",
    "Khulna": "South", "Barishal": "South",
    "Sylhet": "East", "Cumilla": "East",
    "Brahmanbaria": "East",
    "Jashore": "West", "Kushtia": "West",
    "Faridpur": "West",
}


def clean_customers(df):
    """Clean customer table."""
    print("  🧹 Cleaning customers...")
    original = len(df)

    df = df.drop_duplicates(subset=["Customer_ID"], keep="first").copy()

    df["District"] = df["District"].astype(str).str.strip().str.title()
    df.loc[df["District"] == "Nan", "District"] = None

    df["Contact_Number"] = (
        df["Contact_Number"]
        .astype(str)
        .str.strip()
        .replace("nan", "MISSING")
        .replace("", "MISSING")
    )

    df["Region"] = df["District"].map(REGION_MAP).fillna("Unknown")

    print(f"     Before: {original:,} → After: {len(df):,} "
          f"(removed {original - len(df)} duplicates)")
    return df


def clean_installations(df):
    """Clean installations."""
    print("  🧹 Cleaning installations...")
    original = len(df)

    df["Solar_Capacity_KW"] = pd.to_numeric(
        df["Solar_Capacity_KW"], errors="coerce"
    )
    df.loc[df["Solar_Capacity_KW"] <= 0, "Solar_Capacity_KW"] = None

    df["Installation_Date"] = pd.to_datetime(
        df["Installation_Date"], errors="coerce"
    )
    # Use SIMULATION_DATE for future check
    df.loc[df["Installation_Date"] > SIMULATION_DATE, "Installation_Date"] = pd.NaT

    status_fix = {
        "complete": "Completed", "Complete": "Completed",
        "COMPLETED": "Completed", "done": "Completed",
    }
    df["Installation_Status"] = (
        df["Installation_Status"].astype(str).replace(status_fix)
    )

    print(f"     Before: {original:,} → After: {len(df):,}")
    return df


def clean_commissioning(df):
    """Clean commissioning dates."""
    print("  🧹 Cleaning commissioning...")
    df["Commissioning_Date"] = pd.to_datetime(
        df["Commissioning_Date"], errors="coerce"
    )
    return df


def print_file_summary():
    """Print folder verification."""
    print("\n" + "=" * 60)
    print("  📁 FILE VERIFICATION")
    print("=" * 60)
    folders = [
        ("data/raw", RAW_DIR),
        ("data/cleaned", CLEANED_DIR),
        ("reports", REPORTS_DIR),
    ]
    for label, path in folders:
        print(f"\n  [{label}]")
        if not os.path.exists(path):
            print("     (folder not found)")
            continue
        for f in sorted(os.listdir(path)):
            size_kb = os.path.getsize(os.path.join(path, f)) // 1024
            print(f"     * {f:40s} ({size_kb} KB)")


def main():
    print("=" * 60)
    print("  🧹 DAY 4 — DATA CLEANING")
    print(f"  Simulation date: {SIMULATION_DATE.strftime('%Y-%m-%d')}")
    print("=" * 60)

    os.makedirs(CLEANED_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)

    print("\n📂 Loading raw data...")
    customers = pd.read_csv(os.path.join(RAW_DIR, "customers.csv"))
    installations = pd.read_csv(os.path.join(RAW_DIR, "installations.csv"))
    commissioning = pd.read_csv(os.path.join(RAW_DIR, "commissioning.csv"))
    regional = pd.read_csv(os.path.join(RAW_DIR, "regional_reports.csv"))

    print(f"   ✅ Customers:     {len(customers):,} rows")
    print(f"   ✅ Installations: {len(installations):,} rows")
    print(f"   ✅ Commissioning: {len(commissioning):,} rows")
    print(f"   ✅ Regional:      {len(regional):,} rows")

    print("\n🔧 Cleaning...")
    customers_clean = clean_customers(customers)
    installations_clean = clean_installations(installations)
    commissioning_clean = clean_commissioning(commissioning)

    print("\n💾 Saving cleaned data...")
    customers_clean.to_csv(
        os.path.join(CLEANED_DIR, "customers_clean.csv"), index=False
    )
    installations_clean.to_csv(
        os.path.join(CLEANED_DIR, "installations_clean.csv"), index=False
    )
    commissioning_clean.to_csv(
        os.path.join(CLEANED_DIR, "commissioning_clean.csv"), index=False
    )
    regional.to_csv(
        os.path.join(CLEANED_DIR, "regional_reports_clean.csv"), index=False
    )
    print(f"   ✅ 4 files saved to: {CLEANED_DIR}")

    print("\n📊 Building combined Excel for Day 5 reporting...")
    output_xlsx = os.path.join(REPORTS_DIR, "Solar_Cleaned_Data.xlsx")
    with pd.ExcelWriter(output_xlsx, engine="openpyxl") as writer:
        customers_clean.to_excel(writer, sheet_name="Customers", index=False)
        installations_clean.to_excel(writer, sheet_name="Installations", index=False)
        commissioning_clean.to_excel(writer, sheet_name="Commissioning", index=False)
        regional.to_excel(writer, sheet_name="Regional_Reports", index=False)
    print(f"   ✅ Saved: {output_xlsx}")

    print_file_summary()

    print("\n" + "=" * 60)
    print("  🎉 CLEANING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()