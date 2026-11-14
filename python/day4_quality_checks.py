"""
day4_quality_checks.py
----------------------
Automated data quality inspection.
Uses FIXED SIMULATION_DATE (not system clock) so results are consistent.

Author: [Your Name]
Day 4 - Data Quality Management
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
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")


def load_data():
    """Load all 4 CSV files into DataFrames."""
    customers = pd.read_csv(os.path.join(RAW_DIR, "customers.csv"))
    installations = pd.read_csv(os.path.join(RAW_DIR, "installations.csv"))
    commissioning = pd.read_csv(os.path.join(RAW_DIR, "commissioning.csv"))
    regional = pd.read_csv(os.path.join(RAW_DIR, "regional_reports.csv"))
    return customers, installations, commissioning, regional


def check_customers(df):
    """Run all customer-related quality checks."""
    checks = {}
    checks["total_customers"] = len(df)
    checks["missing_contact"] = df["Contact_Number"].isnull().sum()
    checks["duplicate_customer_ids"] = df["Customer_ID"].duplicated(keep=False).sum()
    checks["unique_districts_raw"] = df["District"].nunique()

    district_nonnull = df["District"].dropna().astype(str)
    checks["wrong_district_case"] = (
        district_nonnull != district_nonnull.str.strip().str.title()
    ).sum()
    checks["district_extra_spaces"] = (
        district_nonnull != district_nonnull.str.strip()
    ).sum()
    checks["approved_customers"] = (df["Application_Status"] == "Approved").sum()
    checks["approved_missing_contact"] = (
        (df["Application_Status"] == "Approved") & df["Contact_Number"].isnull()
    ).sum()
    checks["missing_district"] = df["District"].isnull().sum()
    return checks


def check_installations(df):
    """Run all installation-related quality checks."""
    checks = {}
    checks["total_installations"] = len(df)
    checks["negative_capacity"] = (df["Solar_Capacity_KW"] < 0).sum()
    checks["zero_capacity"] = (df["Solar_Capacity_KW"] == 0).sum()
    checks["bad_capacity"] = (df["Solar_Capacity_KW"] <= 0).sum()
    checks["valid_capacity_sum"] = round(
        df.loc[df["Solar_Capacity_KW"] > 0, "Solar_Capacity_KW"].sum(), 2
    )

    # Use SIMULATION_DATE for future check
    df["Installation_Date"] = pd.to_datetime(
        df["Installation_Date"], errors="coerce"
    )
    checks["future_dates"] = (df["Installation_Date"] > SIMULATION_DATE).sum()
    checks["invalid_dates"] = df["Installation_Date"].isnull().sum()

    valid_statuses = {"Planned", "In_Progress", "Completed", "Cancelled"}
    checks["bad_status"] = (~df["Installation_Status"].isin(valid_statuses)).sum()
    checks["status_distribution"] = (
        df["Installation_Status"].value_counts().to_dict()
    )
    checks["completed_installations"] = (
        df["Installation_Status"] == "Completed"
    ).sum()
    return checks


def check_commissioning(df):
    """Run commissioning quality checks."""
    checks = {}
    checks["total_commissioning"] = len(df)
    checks["missing_comm_date"] = df["Commissioning_Date"].isnull().sum()
    checks["completed_commissioning"] = (
        df["Commissioning_Status"] == "Completed"
    ).sum()
    return checks


def calculate_quality_score(total_records, total_issues):
    if total_records == 0:
        return 0.0
    return round(((total_records - total_issues) / total_records) * 100, 2)


def main():
    print("=" * 60)
    print("  🌞 SOLAR PROGRAM — DATA QUALITY INSPECTION")
    print(f"  Simulation date: {SIMULATION_DATE.strftime('%Y-%m-%d')}")
    print("=" * 60)

    customers, installations, commissioning, regional = load_data()
    print(f"\n📂 Loaded: {len(customers):,} customers, "
          f"{len(installations):,} installations, "
          f"{len(commissioning):,} commissioning")

    c_checks = check_customers(customers)
    i_checks = check_installations(installations)
    cm_checks = check_commissioning(commissioning)

    print("\n" + "=" * 60)
    print("  CUSTOMER QUALITY CHECKS")
    print("=" * 60)
    print(f"   Total records:              {c_checks['total_customers']:>6,}")
    print(f"   Missing Contact_Number:     {c_checks['missing_contact']:>6,}")
    print(f"   Duplicate Customer_IDs:     {c_checks['duplicate_customer_ids']:>6,}")
    print(f"   Unique districts (raw):     {c_checks['unique_districts_raw']:>6,}")
    print(f"   Wrong district case:        {c_checks['wrong_district_case']:>6,}")
    print(f"   Approved customers:         {c_checks['approved_customers']:>6,}")

    print("\n" + "=" * 60)
    print("  INSTALLATION QUALITY CHECKS")
    print("=" * 60)
    print(f"   Total installations:        {i_checks['total_installations']:>6,}")
    print(f"   Negative capacity:          {i_checks['negative_capacity']:>6,}")
    print(f"   Zero capacity:              {i_checks['zero_capacity']:>6,}")
    print(f"   Future dates (vs {SIMULATION_DATE.strftime('%Y-%m-%d')}): "
          f"{i_checks['future_dates']:>6,}")
    print(f"   Bad status values:          {i_checks['bad_status']:>6,}")
    print(f"   Valid capacity sum (KW):    {i_checks['valid_capacity_sum']:>10,.2f}")

    print("\n" + "=" * 60)
    print("  COMMISSIONING QUALITY CHECKS")
    print("=" * 60)
    print(f"   Total commissioning:        {cm_checks['total_commissioning']:>6,}")
    print(f"   Missing Comm_Date:          {cm_checks['missing_comm_date']:>6,}")

    total_issues = (
        c_checks["missing_contact"]
        + c_checks["duplicate_customer_ids"]
        + c_checks["wrong_district_case"]
        + i_checks["bad_capacity"]
        + i_checks["future_dates"]
        + i_checks["bad_status"]
        + cm_checks["missing_comm_date"]
    )
    total_records = (
        c_checks["total_customers"]
        + i_checks["total_installations"]
        + cm_checks["total_commissioning"]
    )
    score = calculate_quality_score(total_records, total_issues)

    print("\n" + "=" * 60)
    print("  📊 DATA QUALITY SUMMARY")
    print("=" * 60)
    print(f"   Total records: {total_records:>10,}")
    print(f"   Total issues:  {total_issues:>10,}")
    print(f"   Quality Score: {score:>9.2f}%")

    if score >= 98:
        print("   Status: ✅ EXCELLENT")
    elif score >= 95:
        print("   Status: 🟢 GOOD")
    elif score >= 90:
        print("   Status: 🟡 ACCEPTABLE")
    else:
        print("   Status: 🔴 POOR — needs cleaning")

    # Save
    os.makedirs(REPORTS_DIR, exist_ok=True)
    output_path = os.path.join(REPORTS_DIR, "Day4_Data_Quality_Report.xlsx")
    report_data = {
        "Check": [
            "Total Customers", "Missing Contact", "Duplicate IDs",
            "Unique Districts", "Wrong District Case", "Approved Customers",
            "Total Installations", "Negative Capacity", "Zero Capacity",
            "Future Dates", "Bad Status", "Completed Installations",
            "Total Commissioning", "Missing Comm Date",
            "Total Records", "Total Issues", "Data Quality Score (%)",
        ],
        "Value": [
            c_checks["total_customers"], c_checks["missing_contact"],
            c_checks["duplicate_customer_ids"], c_checks["unique_districts_raw"],
            c_checks["wrong_district_case"], c_checks["approved_customers"],
            i_checks["total_installations"], i_checks["negative_capacity"],
            i_checks["zero_capacity"], i_checks["future_dates"],
            i_checks["bad_status"], i_checks["completed_installations"],
            cm_checks["total_commissioning"], cm_checks["missing_comm_date"],
            total_records, total_issues, score,
        ],
    }
    pd.DataFrame(report_data).to_excel(
        output_path, index=False, sheet_name="Quality_Summary"
    )
    print(f"\n💾 Saved: {output_path}")
    print("\n" + "=" * 60)
    print("  🎉 DAY 4 QUALITY CHECK COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()