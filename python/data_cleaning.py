"""
day8_advanced_cleaning.py
-------------------------
Advanced data cleaning pipeline.

Steps:
  1. Load cleaned data from Day 4
  2. Fuzzy-match corrupted district names
  3. Infer missing commissioning dates (domain logic)
  4. Validate dates (future, too old, logical order)
  5. Validate capacity (statistical + business rules)
  6. Recompute data quality score (before/after)
  7. Export cleaned data + comparison report

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
CLEANED_DIR = os.path.join(PROJECT_ROOT, "data", "cleaned")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")

# =====================================================
# REFERENCE DATA
# =====================================================
REAL_DISTRICTS = [
    # North
    "Rangpur", "Dinajpur", "Bogura", "Rajshahi",
    # Central
    "Dhaka", "Gazipur", "Tangail", "Mymensingh",
    # South
    "Chattogram", "Cox'S Bazar", "Khulna", "Barishal",
    # East
    "Sylhet", "Cumilla", "Brahmanbaria",
    # West
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
    """
    Fix corrupted district name using:
      1. @ → a, trim spaces, title case
      2. Exact match
      3. Fuzzy match (difflib)
    """
    if pd.isna(name):
        return "Unknown"

    # Normalize: @ → a, remove spaces, title case
    cleaned = str(name).replace("@", "a").strip().title()

    # Exact match?
    if cleaned in REAL_DISTRICTS:
        return cleaned

    # Fuzzy match (cutoff 0.75 = reasonably strict)
    matches = get_close_matches(cleaned, REAL_DISTRICTS, n=1, cutoff=0.75)
    if matches:
        return matches[0]

    return "Unknown"


def infer_commissioning_date(install_date, status):
    """
    Infer missing commissioning date using domain logic.
      - If status is "Pending" or "Failed" → None is OK
      - If status is "Completed" → should have a date → infer as installation + 15 days
    """
    if pd.notna(install_date) and status == "Completed":
        return pd.to_datetime(install_date) + pd.Timedelta(days=15)
    return None


# =====================================================
# CLEANING PIPELINE
# =====================================================

def clean_customers(df):
    """Advanced customer cleaning."""
    print("\n🧹 Cleaning customers...")
    before_issues = 0

    # --- 1. Remove duplicates by Customer_ID ---
    dup_count = df["Customer_ID"].duplicated().sum()
    df = df.drop_duplicates(subset=["Customer_ID"], keep="first").copy()
    print(f"   Removed {dup_count} duplicate Customer_IDs")
    before_issues += dup_count

    # --- 2. Fuzzy-fix District names ---
    before_districts = df["District"].nunique()
    df["District"] = df["District"].apply(fix_district_name)
    after_districts = df["District"].nunique()
    print(f"   Districts: {before_districts} → {after_districts} "
          f"(fuzzy-fixed)")
    before_issues += (before_districts - after_districts)

    # --- 3. Fill missing Contact_Number ---
    missing_contact = df["Contact_Number"].isnull().sum()
    if "Contact_Number" in df.columns:
        df["Contact_Number"] = df["Contact_Number"].fillna("MISSING")
        print(f"   Filled {missing_contact} missing contacts with 'MISSING'")
        before_issues += missing_contact

    # --- 4. Recompute Region ---
    df["Region"] = df["District"].map(REGION_MAP).fillna("Unknown")

    # --- 5. Validate Registration_Date ---
    df["Registration_Date"] = pd.to_datetime(
        df["Registration_Date"], errors="coerce"
    )
    future_reg = (df["Registration_Date"] > SIMULATION_DATE).sum()
    df.loc[df["Registration_Date"] > SIMULATION_DATE, "Registration_Date"] = pd.NaT
    old_reg = (df["Registration_Date"] < PROJECT_START).sum()
    df.loc[df["Registration_Date"] < PROJECT_START, "Registration_Date"] = pd.NaT
    print(f"   Invalid registration dates: {future_reg + old_reg}")

    return df


def clean_installations(df, customers_df):
    """Advanced installation cleaning."""
    print("\n🧹 Cleaning installations...")

    # --- 1. Convert types ---
    df["Solar_Capacity_KW"] = pd.to_numeric(
        df["Solar_Capacity_KW"], errors="coerce"
    )
    df["Installation_Date"] = pd.to_datetime(
        df["Installation_Date"], errors="coerce"
    )

    # --- 2. Fix negative / zero capacity ---
    bad_cap = (df["Solar_Capacity_KW"] <= 0).sum()
    df.loc[df["Solar_Capacity_KW"] <= 0, "Solar_Capacity_KW"] = None
    print(f"   Fixed {bad_cap} bad capacities (negative/zero → None)")

    # --- 3. Fix future dates ---
    future = (df["Installation_Date"] > SIMULATION_DATE).sum()
    df.loc[df["Installation_Date"] > SIMULATION_DATE, "Installation_Date"] = pd.NaT
    print(f"   Fixed {future} future dates")

    # --- 4. Standardize status ---
    status_fix = {
        "complete": "Completed", "Complete": "Completed",
        "COMPLETED": "Completed", "done": "Completed",
    }
    df["Installation_Status"] = (
        df["Installation_Status"].astype(str).replace(status_fix)
    )

    # --- 5. Merge with customers to check capacity vs customer type ---
    merged = df.merge(
        customers_df[["Customer_ID", "Customer_Type"]],
        on="Customer_ID", how="left"
    )

    def is_capacity_reasonable(row):
        ct, kw = row["Customer_Type"], row["Solar_Capacity_KW"]
        if pd.isna(kw) or pd.isna(ct):
            return True
        return {
            "Residential":   1 <= kw <= 5,
            "Commercial":    5 <= kw <= 20,
            "Institutional": 10 <= kw <= 50,
            "Industrial":    20 <= kw <= 100,
        }.get(ct, True)

    unreasonable = (~merged.apply(is_capacity_reasonable, axis=1)).sum()
    print(f"   Suspicious capacities (vs customer type): {unreasonable}")

    return df


def clean_commissioning(df, installations_df):
    """Advanced commissioning cleaning with domain inference."""
    print("\n🧹 Cleaning commissioning...")

    df["Commissioning_Date"] = pd.to_datetime(
        df["Commissioning_Date"], errors="coerce"
    )

    # --- 1. Merge with installations for inference ---
    merged = df.merge(
        installations_df[["Customer_ID", "Installation_Date"]],
        on="Customer_ID", how="left"
    )

    # --- 2. Infer missing Comm_Date for Completed status ---
    missing_before = merged["Commissioning_Date"].isnull().sum()

    inferred = merged.apply(
        lambda row: infer_commissioning_date(
            row["Installation_Date"], row["Commissioning_Status"]
        ) if pd.isna(row["Commissioning_Date"]) else row["Commissioning_Date"],
        axis=1
    )
    merged["Commissioning_Date"] = inferred

    missing_after = merged["Commissioning_Date"].isnull().sum()
    print(f"   Missing Comm_Date: {missing_before} → {missing_after} "
          f"(inferred {missing_before - missing_after})")

    # --- 3. Validate future dates ---
    future = (merged["Commissioning_Date"] > SIMULATION_DATE).sum()
    merged.loc[
        merged["Commissioning_Date"] > SIMULATION_DATE,
        "Commissioning_Date"
    ] = pd.NaT
    print(f"   Fixed {future} future commissioning dates")

    # Return only original columns
    return merged[df.columns]


# =====================================================
# QUALITY SCORE
# =====================================================

def calculate_quality(customers, installations, commissioning):
    """Compute data quality metrics."""
    issues = {
        "missing_contact": customers["Contact_Number"].isnull().sum() +
                          (customers["Contact_Number"] == "MISSING").sum(),
        "unknown_district": (customers["District"] == "Unknown").sum(),
        "negative_capacity": (installations["Solar_Capacity_KW"] < 0).sum(),
        "zero_capacity": (installations["Solar_Capacity_KW"] == 0).sum(),
        "future_dates": (
            (pd.to_datetime(installations["Installation_Date"], errors="coerce")
             > SIMULATION_DATE).sum()
        ),
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
    print("  🌞 DAY 8 — ADVANCED DATA CLEANING")
    print(f"  Simulation date: {SIMULATION_DATE.strftime('%Y-%m-%d')}")
    print("=" * 60)

    # ---- Load ----
    print("\n📂 Loading Day 4 cleaned data...")
    customers = pd.read_csv(os.path.join(CLEANED_DIR, "customers_clean.csv"))
    installations = pd.read_csv(os.path.join(CLEANED_DIR, "installations_clean.csv"))
    commissioning = pd.read_csv(os.path.join(CLEANED_DIR, "commissioning_clean.csv"))
    regional = pd.read_csv(os.path.join(CLEANED_DIR, "regional_reports_clean.csv"))

    print(f"   Customers:     {len(customers):,}")
    print(f"   Installations: {len(installations):,}")
    print(f"   Commissioning: {len(commissioning):,}")

    # ---- Quality Before ----
    print("\n" + "=" * 60)
    print("  📊 QUALITY SCORE — BEFORE")
    print("=" * 60)
    before = calculate_quality(customers, installations, commissioning)
    print(f"   Total records: {before['total_records']:,}")
    print(f"   Total issues:  {before['total_issues']:,}")
    print(f"   Score:         {before['score']}%")
    for k, v in before["issues"].items():
        print(f"     {k:25s} {v:>5}")

    # ---- Clean ----
    customers_clean = clean_customers(customers)
    installations_clean = clean_installations(installations, customers_clean)
    commissioning_clean = clean_commissioning(commissioning, installations_clean)

    # ---- Quality After ----
    print("\n" + "=" * 60)
    print("  📊 QUALITY SCORE — AFTER")
    print("=" * 60)
    after = calculate_quality(customers_clean, installations_clean, commissioning_clean)
    print(f"   Total records: {after['total_records']:,}")
    print(f"   Total issues:  {after['total_issues']:,}")
    print(f"   Score:         {after['score']}%")
    for k, v in after["issues"].items():
        print(f"     {k:25s} {v:>5}")

    # ---- Improvement ----
    improvement = after["score"] - before["score"]
    print(f"\n   📈 Improvement: +{improvement:.2f} percentage points")

    # ---- Save cleaned data ----
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

    # ---- Save comparison report ----
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
            "Before": [
                before["total_records"],
                before["total_issues"],
                before["score"],
            ],
            "After": [
                after["total_records"],
                after["total_issues"],
                after["score"],
            ],
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