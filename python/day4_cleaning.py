"""
day4_cleaning.py
----------------
Basic cleaning operations for Day 4.
Full cleaning will be done on Day 8 with advanced Pandas.
This script produces clean CSVs ready for Day 5 Excel reporting.

Author: [Your Name]
Day 4 - Excel Data Cleaning
"""

import os
import pandas as pd
from datetime import datetime

# =====================================================
# PATH SETUP — works from ANY working directory
# =====================================================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
CLEANED_DIR = os.path.join(PROJECT_ROOT, "data", "cleaned")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")


# =====================================================
# REGION MAP (module-level so multiple functions use it)
# =====================================================
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


# =====================================================
# CLEANING FUNCTIONS
# =====================================================

def clean_customers(df):
    """
    Clean customer table:
      1. Remove duplicate Customer_IDs (keep first occurrence)
      2. TRIM + TITLE-CASE the District column
      3. Convert Contact_Number to string, fill missing with 'MISSING'
      4. Recompute Region from cleaned District
    """
    print("  🧹 Cleaning customers...")
    original = len(df)

    # --- 1. Remove duplicates ---
    df = df.drop_duplicates(subset=["Customer_ID"], keep="first").copy()

    # --- 2. Clean District: strip spaces + Title Case ---
    df["District"] = df["District"].astype(str).str.strip().str.title()
    # Convert literal "nan" (from float NaN converted to string) to real None
    df.loc[df["District"] == "Nan", "District"] = None

    # --- 3. Clean Contact_Number ---
    # First cast the whole column to string so "nan" becomes literal text,
    # then replace with the sentinel "MISSING".
    df["Contact_Number"] = (
        df["Contact_Number"]
        .astype(str)               # float NaN → "nan"
        .str.strip()               # remove extra spaces
        .replace("nan", "MISSING") # literal "nan" → "MISSING"
        .replace("", "MISSING")    # empty string → "MISSING"
    )

    # --- 4. Re-map Region using REGION_MAP ---
    df["Region"] = df["District"].map(REGION_MAP).fillna("Unknown")

    print(f"     Before: {original:,} → After: {len(df):,} "
          f"(removed {original - len(df)} duplicates)")
    return df


def clean_installations(df):
    """
    Clean installations:
      1. Negative / zero capacity → NaN (invalid)
      2. Future installation dates → NaT (invalid)
      3. Standardize status spelling variations
    """
    print("  🧹 Cleaning installations...")
    original = len(df)

    # --- 1. Bad capacity → NaN ---
    df["Solar_Capacity_KW"] = pd.to_numeric(
        df["Solar_Capacity_KW"], errors="coerce"
    )
    df.loc[df["Solar_Capacity_KW"] <= 0, "Solar_Capacity_KW"] = None

    # --- 2. Future dates → NaT ---
    df["Installation_Date"] = pd.to_datetime(
        df["Installation_Date"], errors="coerce"
    )
    today = pd.Timestamp.today().normalize()
    df.loc[df["Installation_Date"] > today, "Installation_Date"] = pd.NaT

    # --- 3. Standardize status spelling ---
    status_fix = {
        "complete": "Completed",
        "Complete": "Completed",
        "COMPLETED": "Completed",
        "done": "Completed",
    }
    df["Installation_Status"] = (
        df["Installation_Status"].astype(str).replace(status_fix)
    )

    print(f"     Before: {original:,} → After: {len(df):,}")
    return df


def clean_commissioning(df):
    """
    Clean commissioning:
      - Parse Commissioning_Date to datetime (invalid → NaT)
    """
    print("  🧹 Cleaning commissioning...")
    df["Commissioning_Date"] = pd.to_datetime(
        df["Commissioning_Date"], errors="coerce"
    )
    return df


# =====================================================
# VERIFICATION HELPER
# =====================================================

def print_file_summary():
    """Print a quick verification of all output folders."""
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


# =====================================================
# MAIN
# =====================================================

def main():
    print("=" * 60)
    print("  🧹 DAY 4 — DATA CLEANING")
    print("=" * 60)

    # Ensure output folders exist
    os.makedirs(CLEANED_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)

    # --- Load raw data ---
    print("\n📂 Loading raw data...")
    customers = pd.read_csv(os.path.join(RAW_DIR, "customers.csv"))
    installations = pd.read_csv(os.path.join(RAW_DIR, "installations.csv"))
    commissioning = pd.read_csv(os.path.join(RAW_DIR, "commissioning.csv"))
    regional = pd.read_csv(os.path.join(RAW_DIR, "regional_reports.csv"))

    print(f"   ✅ Customers:     {len(customers):,} rows")
    print(f"   ✅ Installations: {len(installations):,} rows")
    print(f"   ✅ Commissioning: {len(commissioning):,} rows")
    print(f"   ✅ Regional:      {len(regional):,} rows")

    # --- Clean ---
    print("\n🔧 Cleaning...")
    customers_clean = clean_customers(customers)
    installations_clean = clean_installations(installations)
    commissioning_clean = clean_commissioning(commissioning)

    # --- Save cleaned CSVs ---
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

    # --- Combined Excel for Day 5 ---
    print("\n📊 Building combined Excel for Day 5 reporting...")
    output_xlsx = os.path.join(REPORTS_DIR, "Solar_Cleaned_Data.xlsx")
    with pd.ExcelWriter(output_xlsx, engine="openpyxl") as writer:
        customers_clean.to_excel(writer, sheet_name="Customers", index=False)
        installations_clean.to_excel(writer, sheet_name="Installations", index=False)
        commissioning_clean.to_excel(writer, sheet_name="Commissioning", index=False)
        regional.to_excel(writer, sheet_name="Regional_Reports", index=False)
    print(f"   ✅ Saved: {output_xlsx}")

    # --- Verification summary ---
    print_file_summary()

    print("\n" + "=" * 60)
    print("  🎉 CLEANING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()