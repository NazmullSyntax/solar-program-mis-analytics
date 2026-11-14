"""
day4_cleaning.py
----------------
Basic cleaning operations (Day 4 version — simple clean only).
Full cleaning will be done on Day 8 with advanced Pandas.
This script produces clean CSVs ready for Excel reporting.

Author: [Your Name]
Day 4 - Excel Data Cleaning
"""

import os
import pandas as pd
from datetime import datetime

# =====================================================
# PATH SETUP
# =====================================================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
CLEANED_DIR = os.path.join(PROJECT_ROOT, "data", "cleaned")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")


# =====================================================
# CLEANING FUNCTIONS
# =====================================================

def clean_customers(df):
    """
    Clean customer table:
    1. Remove duplicate Customer_IDs (keep first)
    2. TRIM + PROPER the District column
    3. TRIM + fill 'MISSING' for Contact_Number
    4. Recompute Region based on cleaned District
    """
    print("  🧹 Cleaning customers...")
    original = len(df)

    # 1. Remove duplicates by Customer_ID (keep first)
    df = df.drop_duplicates(subset=["Customer_ID"], keep="first").copy()

    # 2. Clean District: TRIM + Title Case
    df["District"] = df["District"].astype(str).str.strip().str.title()
    df.loc[df["District"] == "Nan", "District"] = None

    # 3. Clean Contact: keep None for missing
    df["Contact_Number"] = df["Contact_Number"].fillna("MISSING")

    # 4. Re-map Region (in case district changed case)
    region_map = {
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
    df["Region"] = df["District"].map(region_map).fillna("Unknown")

    print(f"     Before: {original:,} → After: {len(df):,} "
          f"(removed {original - len(df)} duplicates)")
    return df


def clean_installations(df):
    """
    Clean installations:
    1. Fix negative/zero capacity → NaN
    2. Fix future dates → NaN
    3. Standardize status spelling
    """
    print("  🧹 Cleaning installations...")
    original = len(df)

    # 1. Bad capacity → NaN
    df.loc[df["Solar_Capacity_KW"] <= 0, "Solar_Capacity_KW"] = None

    # 2. Future dates → NaN
    df["Installation_Date"] = pd.to_datetime(
        df["Installation_Date"], errors="coerce"
    )
    today = pd.Timestamp.today().normalize()
    df.loc[df["Installation_Date"] > today, "Installation_Date"] = pd.NaT

    # 3. Standardize status
    status_fix = {
        "complete": "Completed",
        "Complete": "Completed",
        "COMPLETED": "Completed",
        "done": "Completed",
    }
    df["Installation_Status"] = df["Installation_Status"].replace(status_fix)

    print(f"     Before: {original:,} → After: {len(df):,}")
    return df


def clean_commissioning(df):
    """Clean commissioning: fill missing dates with NaN."""
    print("  🧹 Cleaning commissioning...")
    df["Commissioning_Date"] = pd.to_datetime(
        df["Commissioning_Date"], errors="coerce"
    )
    return df


# =====================================================
# MAIN
# =====================================================
def main():
    print("=" * 60)
    print("  🧹 DAY 4 — DATA CLEANING")
    print("=" * 60)

    # Ensure output folder exists
    os.makedirs(CLEANED_DIR, exist_ok=True)

    # Load raw
    print("\n📂 Loading raw data...")
    customers = pd.read_csv(os.path.join(RAW_DIR, "customers.csv"))
    installations = pd.read_csv(os.path.join(RAW_DIR, "installations.csv"))
    commissioning = pd.read_csv(os.path.join(RAW_DIR, "commissioning.csv"))
    regional = pd.read_csv(os.path.join(RAW_DIR, "regional_reports.csv"))

    # Clean
    print("\n🔧 Cleaning...")
    customers_clean = clean_customers(customers)
    installations_clean = clean_installations(installations)
    commissioning_clean = clean_commissioning(commissioning)

    # Save cleaned CSVs
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

    # Save combined Excel for reporting (Day 5 will use this)
    print("\n📊 Building combined Excel for Day 5 reporting...")
    output_xlsx = os.path.join(REPORTS_DIR, "Solar_Cleaned_Data.xlsx")
    os.makedirs(REPORTS_DIR, exist_ok=True)
    with pd.ExcelWriter(output_xlsx, engine="openpyxl") as writer:
        customers_clean.to_excel(writer, sheet_name="Customers", index=False)
        installations_clean.to_excel(writer, sheet_name="Installations", index=False)
        commissioning_clean.to_excel(writer, sheet_name="Commissioning", index=False)
        regional.to_excel(writer, sheet_name="Regional_Reports", index=False)
    print(f"   ✅ Saved: {output_xlsx}")

    print("\n" + "=" * 60)
    print("  🎉 CLEANING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()