"""
day8_advanced_cleaning.py
-------------------------
Advanced data cleaning pipeline (FINAL CORRECTED VERSION).

Key features:
  - Fuzzy matching for corrupted district names
  - Future dates fixed BEFORE inference (critical order)
  - Dedup installations lookup (no row inflation)
  - Idempotent: same input → same output
  - Quality score before/after comparison

Author: [Your Name]
Day 8 - Advanced Data Cleaning
"""

import os
import pandas as pd
from difflib import get_close_matches

# =====================================================
# SETUP
# =====================================================
SIMULATION_DATE = pd.Timestamp("2025-11-15")
PROJECT_START = pd.Timestamp("2023-01-01")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
CLEANED_DIR = os.path.join(PROJECT_ROOT, "data", "cleaned")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")

# =====================================================
# REFERENCE DATA
# =====================================================
REAL_DISTRICTS = [
    "Rangpur", "Dinajpur", "Bogura", "Rajshahi",
    "Dhaka", "Gazipur", "Tangail", "Mymensingh",
    "Chattogram", "Cox'S Bazar", "Khulna", "Barishal",
    "Sylhet", "Cumilla", "Brahmanbaria",
    "Jashore", "Kushtia", "Faridpur",
]

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
# UTILITIES
# =====================================================

def fix_district_name(name):
    """Fix corrupted district name via normalize + fuzzy match."""
    if pd.isna(name):
        return "Unknown"
    cleaned = str(name).replace("@", "a").strip().title()
    if cleaned in REAL_DISTRICTS:
        return cleaned
    matches = get_close_matches(cleaned, REAL_DISTRICTS, n=1, cutoff=0.75)
    return matches[0] if matches else "Unknown"


# =====================================================
# CLEANING FUNCTIONS
# =====================================================

def clean_customers(df):
    """Clean customer table."""
    print("\n🧹 Cleaning customers...")

    # 1. Dedup
    dup = df["Customer_ID"].duplicated().sum()
    df = df.drop_duplicates(subset=["Customer_ID"], keep="first").copy()
    print(f"   Removed {dup} duplicate Customer_IDs")

    # 2. Fuzzy district
    before = df["District"].nunique()
    df["District"] = df["District"].apply(fix_district_name)
    after = df["District"].nunique()
    print(f"   Districts: {before} → {after} (fuzzy-fixed)")

    # 3. Contact_Number — cast to str FIRST to avoid dtype warning
    df["Contact_Number"] = (
        df["Contact_Number"]
        .astype(str)
        .str.strip()
        .replace({"nan": "MISSING", "None": "MISSING", "": "MISSING"})
    )
    print(f"   Contact numbers normalized")

    # 4. Region
    df["Region"] = df["District"].map(REGION_MAP).fillna("Unknown")

    # 5. Registration_Date
    df["Registration_Date"] = pd.to_datetime(
        df["Registration_Date"], errors="coerce"
    )
    future = (df["Registration_Date"] > SIMULATION_DATE).sum()
    old = (df["Registration_Date"] < PROJECT_START).sum()
    df.loc[df["Registration_Date"] > SIMULATION_DATE, "Registration_Date"] = pd.NaT
    df.loc[df["Registration_Date"] < PROJECT_START, "Registration_Date"] = pd.NaT
    print(f"   Invalid registration dates fixed: {future + old}")

    return df


def clean_installations(df, customers_df):
    """Clean installation table."""
    print("\n🧹 Cleaning installations...")

    df["Solar_Capacity_KW"] = pd.to_numeric(
        df["Solar_Capacity_KW"], errors="coerce"
    )
    df["Installation_Date"] = pd.to_datetime(
        df["Installation_Date"], errors="coerce"
    )

    # Fix bad capacity
    bad_cap = (df["Solar_Capacity_KW"] <= 0).sum()
    df.loc[df["Solar_Capacity_KW"] <= 0, "Solar_Capacity_KW"] = None
    print(f"   Fixed {bad_cap} bad capacities")

    # Fix future dates
    future = (df["Installation_Date"] > SIMULATION_DATE).sum()
    df.loc[df["Installation_Date"] > SIMULATION_DATE, "Installation_Date"] = pd.NaT
    print(f"   Fixed {future} future installation dates")

    # Standardize status
    status_fix = {
        "complete": "Completed", "Complete": "Completed",
        "COMPLETED": "Completed", "done": "Completed",
    }
    df["Installation_Status"] = df["Installation_Status"].astype(str).replace(status_fix)

    return df


def clean_commissioning(df, installations_df):
    """
    Clean commissioning table (FINAL VERSION — future-safe inference).

    Order:
      1. Ensure datetime
      2. Count missing before
      3. Dedup installations lookup
      4. Merge (no row inflation)
      5. Infer missing dates for Completed
      6. Fix future dates BEFORE AND AFTER inference
    """
    print("\n🧹 Cleaning commissioning...")
    original_len = len(df)

    # 1. Ensure datetime
    df["Commissioning_Date"] = pd.to_datetime(
        df["Commissioning_Date"], errors="coerce"
    )

    # 2. Count missing BEFORE
    missing_before = df["Commissioning_Date"].isnull().sum()

    # 3. Fix future dates BEFORE inference
    future_before = (df["Commissioning_Date"] > SIMULATION_DATE).sum()
    df.loc[df["Commissioning_Date"] > SIMULATION_DATE, "Commissioning_Date"] = pd.NaT
    print(f"   Fixed {future_before} future dates (before inference)")

    # 4. Dedup installations lookup
    install_lookup = (
        installations_df[["Customer_ID", "Installation_Date"]]
        .drop_duplicates(subset=["Customer_ID"], keep="first")
        .copy()
    )

    # 5. Merge (safe, 1:1)
    merged = df.merge(install_lookup, on="Customer_ID", how="left")
    assert len(merged) == original_len, (
        f"Merge inflated: {original_len} → {len(merged)}"
    )

    # 6. Infer missing dates
    def safe_infer(row):
        if pd.notna(row["Commissioning_Date"]):
            return row["Commissioning_Date"]
        if row["Commissioning_Status"] == "Completed" and pd.notna(row["Installation_Date"]):
            try:
                inferred = pd.to_datetime(row["Installation_Date"]) + pd.Timedelta(days=15)
                # Reject inferred if future
                if inferred > SIMULATION_DATE:
                    return None
                return inferred
            except Exception:
                return None
        return None

    merged["Commissioning_Date"] = merged.apply(safe_infer, axis=1)

    # 7. Fix future dates AFTER inference (defensive)
    future_after = (merged["Commissioning_Date"] > SIMULATION_DATE).sum()
    merged.loc[merged["Commissioning_Date"] > SIMULATION_DATE, "Commissioning_Date"] = pd.NaT
    if future_after > 0:
        print(f"   Fixed {future_after} future dates (after inference)")

    # 8. Count missing AFTER
    missing_after = merged["Commissioning_Date"].isnull().sum()
    inferred = missing_before - missing_after
    print(f"   Missing Comm_Date: {missing_before} → {missing_after} "
          f"(inferred {inferred})")
    print(f"   Row count: {original_len} → {len(merged)} (no inflation ✅)")

    return merged[df.columns]


# =====================================================
# QUALITY SCORE
# =====================================================

def calculate_quality(customers, installations, commissioning):
    """Compute data quality metrics."""
    issues = {
        "missing_contact": (
            customers["Contact_Number"].isnull().sum()
            + (customers["Contact_Number"] == "MISSING").sum()
        ),
        "unknown_district": (customers["District"] == "Unknown").sum(),
        "negative_capacity": (installations["Solar_Capacity_KW"] < 0).sum(),
        "zero_capacity": (installations["Solar_Capacity_KW"] == 0).sum(),
        "future_install_dates": (
            pd.to_datetime(installations["Installation_Date"], errors="coerce")
            > SIMULATION_DATE
        ).sum(),
        "future_comm_dates": (
            pd.to_datetime(commissioning["Commissioning_Date"], errors="coerce")
            > SIMULATION_DATE
        ).sum(),
        "missing_comm_date": commissioning["Commissioning_Date"].isnull().sum(),
    }
    total_records = len(customers) + len(installations) + len(commissioning)
    total_issues = sum(issues.values())
    score = ((total_records - total_issues) / total_records) * 100
    return {
        "issues": issues,
        "total_records": total_records,
        "total_issues": total_issues,
        "score": round(score, 2),
    }


# =====================================================
# MAIN
# =====================================================

def main():
    print("=" * 60)
    print("  🌞 DAY 8 — ADVANCED DATA CLEANING (FINAL)")
    print(f"  Simulation date: {SIMULATION_DATE.strftime('%Y-%m-%d')}")
    print("=" * 60)

    # Load from RAW (Day 4 cleaned) — NOT from previous v2 (idempotent!)
    print("\n📂 Loading Day 4 cleaned data...")
    customers = pd.read_csv(os.path.join(CLEANED_DIR, "customers_clean.csv"))
    installations = pd.read_csv(os.path.join(CLEANED_DIR, "installations_clean.csv"))
    commissioning = pd.read_csv(os.path.join(CLEANED_DIR, "commissioning_clean.csv"))
    regional = pd.read_csv(os.path.join(CLEANED_DIR, "regional_reports_clean.csv"))

    print(f"   Customers:     {len(customers):,}")
    print(f"   Installations: {len(installations):,}")
    print(f"   Commissioning: {len(commissioning):,}")

    # ---- BEFORE ----
    print("\n" + "=" * 60)
    print("  📊 QUALITY SCORE — BEFORE")
    print("=" * 60)
    before = calculate_quality(customers, installations, commissioning)
    print(f"   Total records: {before['total_records']:,}")
    print(f"   Total issues:  {before['total_issues']:,}")
    print(f"   Score:         {before['score']}%")
    for k, v in before["issues"].items():
        print(f"     {k:25s} {v:>5}")

    # ---- CLEAN ----
    customers_clean = clean_customers(customers)
    installations_clean = clean_installations(installations, customers_clean)
    commissioning_clean = clean_commissioning(commissioning, installations_clean)

    # ---- AFTER ----
    print("\n" + "=" * 60)
    print("  📊 QUALITY SCORE — AFTER")
    print("=" * 60)
    after = calculate_quality(customers_clean, installations_clean, commissioning_clean)
    print(f"   Total records: {after['total_records']:,}")
    print(f"   Total issues:  {after['total_issues']:,}")
    print(f"   Score:         {after['score']}%")
    for k, v in after["issues"].items():
        print(f"     {k:25s} {v:>5}")

    improvement = after["score"] - before["score"]
    print(f"\n   📈 Improvement: {improvement:+.2f} percentage points")

    # ---- SAVE ----
    print("\n💾 Saving Day 8 cleaned data...")
    customers_clean.to_csv(
        os.path.join(CLEANED_DIR, "customers_v2.csv"), index=False
    )
    installations_clean.to_csv(
        os.path.join(CLEANED_DIR, "installations_v2.csv"), index=False
    )
    commissioning_clean.to_csv(
        os.path.join(CLEANED_DIR, "commissioning_v2.csv"), index=False
    )
    regional.to_csv(
        os.path.join(CLEANED_DIR, "regional_reports_v2.csv"), index=False
    )
    print(f"   ✅ Saved *_v2.csv to {CLEANED_DIR}")

    # ---- REPORT ----
    print("\n📊 Saving comparison report...")
    os.makedirs(REPORTS_DIR, exist_ok=True)
    output_file = os.path.join(REPORTS_DIR, "Day8_Cleaning_Report.xlsx")

    comparison = pd.DataFrame({
        "Issue": list(before["issues"].keys()) + ["TOTAL"],
        "Before": list(before["issues"].values()) + [before["total_issues"]],
        "After": list(after["issues"].values()) + [after["total_issues"]],
    })
    comparison["Reduced"] = comparison["Before"] - comparison["After"]

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        comparison.to_excel(writer, sheet_name="Issue_Comparison", index=False)
        pd.DataFrame({
            "Metric": ["Total Records", "Total Issues", "Quality Score (%)"],
            "Before": [before["total_records"], before["total_issues"], before["score"]],
            "After": [after["total_records"], after["total_issues"], after["score"]],
        }).to_excel(writer, sheet_name="Summary", index=False)
        customers_clean.to_excel(writer, sheet_name="Customers_Clean", index=False)
        installations_clean.to_excel(writer, sheet_name="Installations_Clean", index=False)
        commissioning_clean.to_excel(writer, sheet_name="Commissioning_Clean", index=False)

    print(f"   ✅ Saved: {output_file}")

    print("\n" + "=" * 60)
    print("  🎉 DAY 8 ADVANCED CLEANING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()