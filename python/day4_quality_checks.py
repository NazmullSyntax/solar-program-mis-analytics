"""
day4_quality_checks.py
----------------------
Automated data quality inspection.
Replicates all 12 Excel formulas from Day 4 lesson.
Outputs a summary to console AND saves a data quality Excel report.

Author: [Your Name]
Day 4 - Data Quality Management
"""

import os
import pandas as pd
from datetime import datetime

# =====================================================
# PATH SETUP
# =====================================================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")


# =====================================================
# LOAD DATA
# =====================================================
def load_data():
    """Load all 4 CSV files into DataFrames."""
    customers = pd.read_csv(os.path.join(RAW_DIR, "customers.csv"))
    installations = pd.read_csv(os.path.join(RAW_DIR, "installations.csv"))
    commissioning = pd.read_csv(os.path.join(RAW_DIR, "commissioning.csv"))
    regional = pd.read_csv(os.path.join(RAW_DIR, "regional_reports.csv"))
    return customers, installations, commissioning, regional


# =====================================================
# QUALITY CHECKS
# =====================================================
def check_customers(df):
    """Run all customer-related quality checks."""
    checks = {}

    # Check 1: Total records
    checks["total_customers"] = len(df)

    # Check 2: Missing contact numbers
    checks["missing_contact"] = df["Contact_Number"].isnull().sum()

    # Check 3: Duplicate Customer IDs (all occurrences)
    dup_mask = df["Customer_ID"].duplicated(keep=False)
    checks["duplicate_customer_ids"] = dup_mask.sum()

    # Check 4: Unique districts (count)
    checks["unique_districts_raw"] = df["District"].nunique()

    # Check 5: Districts where case doesn't match PROPER case
    # (e.g. "dhaka" or "DHAKA" instead of "Dhaka")
    district_nonnull = df["District"].dropna().astype(str)
    wrong_case = (district_nonnull != district_nonnull.str.strip().str.title()).sum()
    checks["wrong_district_case"] = wrong_case

    # Check 6: Districts with extra spaces
    has_space = (district_nonnull != district_nonnull.str.strip()).sum()
    checks["district_extra_spaces"] = has_space

    # Check 7: Approved customers count
    checks["approved_customers"] = (df["Application_Status"] == "Approved").sum()

    # Check 8: Approved with missing contact
    checks["approved_missing_contact"] = (
        (df["Application_Status"] == "Approved") & df["Contact_Number"].isnull()
    ).sum()

    # Check 9: Missing district
    checks["missing_district"] = df["District"].isnull().sum()

    return checks


def check_installations(df):
    """Run all installation-related quality checks."""
    checks = {}

    # Check 1: Total installations
    checks["total_installations"] = len(df)

    # Check 2: Negative capacity (impossible)
    checks["negative_capacity"] = (df["Solar_Capacity_KW"] < 0).sum()

    # Check 3: Zero capacity (invalid)
    checks["zero_capacity"] = (df["Solar_Capacity_KW"] == 0).sum()

    # Check 4: Total bad capacity
    checks["bad_capacity"] = (df["Solar_Capacity_KW"] <= 0).sum()

    # Check 5: Valid capacity sum (positive only)
    valid_capacity = df.loc[df["Solar_Capacity_KW"] > 0, "Solar_Capacity_KW"].sum()
    checks["valid_capacity_sum"] = round(valid_capacity, 2)

    # Check 6: Future dates
    df["Installation_Date"] = pd.to_datetime(df["Installation_Date"], errors="coerce")
    today = pd.Timestamp.today().normalize()
    checks["future_dates"] = (df["Installation_Date"] > today).sum()

    # Check 7: Invalid dates (unparseable)
    checks["invalid_dates"] = df["Installation_Date"].isnull().sum()

    # Check 8: Bad status values
    valid_statuses = {"Planned", "In_Progress", "Completed", "Cancelled"}
    checks["bad_status"] = (~df["Installation_Status"].isin(valid_statuses)).sum()

    # Check 9: Status distribution
    checks["status_distribution"] = df["Installation_Status"].value_counts().to_dict()

    # Check 10: Completed installations count
    checks["completed_installations"] = (df["Installation_Status"] == "Completed").sum()

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


# =====================================================
# CALCULATE DATA QUALITY SCORE
# =====================================================
def calculate_quality_score(total_records, total_issues):
    """
    Data Quality Score = (valid records / total) × 100
    """
    if total_records == 0:
        return 0.0
    valid = total_records - total_issues
    return round((valid / total_records) * 100, 2)


# =====================================================
# MAIN
# =====================================================
def main():
    print("=" * 60)
    print("  🌞 SOLAR PROGRAM — DATA QUALITY INSPECTION")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    # Load
    print("\n📂 Loading data...")
    customers, installations, commissioning, regional = load_data()
    print(f"   ✅ Customers:     {len(customers):>6,} rows")
    print(f"   ✅ Installations: {len(installations):>6,} rows")
    print(f"   ✅ Commissioning: {len(commissioning):>6,} rows")
    print(f"   ✅ Regional:      {len(regional):>6,} rows")

    # Run checks
    print("\n" + "=" * 60)
    print("  CUSTOMER QUALITY CHECKS")
    print("=" * 60)
    c_checks = check_customers(customers)
    print(f"   Total records:              {c_checks['total_customers']:>6,}")
    print(f"   Missing Contact_Number:     {c_checks['missing_contact']:>6,}")
    print(f"   Duplicate Customer_IDs:     {c_checks['duplicate_customer_ids']:>6,}")
    print(f"   Unique districts (raw):     {c_checks['unique_districts_raw']:>6,}")
    print(f"   Wrong district case:        {c_checks['wrong_district_case']:>6,}")
    print(f"   District extra spaces:      {c_checks['district_extra_spaces']:>6,}")
    print(f"   Approved customers:         {c_checks['approved_customers']:>6,}")
    print(f"   Approved + missing contact: {c_checks['approved_missing_contact']:>6,}")

    print("\n" + "=" * 60)
    print("  INSTALLATION QUALITY CHECKS")
    print("=" * 60)
    i_checks = check_installations(installations)
    print(f"   Total installations:        {i_checks['total_installations']:>6,}")
    print(f"   Negative capacity:          {i_checks['negative_capacity']:>6,}")
    print(f"   Zero capacity:              {i_checks['zero_capacity']:>6,}")
    print(f"   Bad capacity total:         {i_checks['bad_capacity']:>6,}")
    print(f"   Future dates:               {i_checks['future_dates']:>6,}")
    print(f"   Invalid dates:              {i_checks['invalid_dates']:>6,}")
    print(f"   Bad status values:          {i_checks['bad_status']:>6,}")
    print(f"   Completed installations:    {i_checks['completed_installations']:>6,}")
    print(f"   Valid capacity sum (KW):    {i_checks['valid_capacity_sum']:>10,.2f}")
    print(f"\n   Status distribution:")
    for status, count in i_checks["status_distribution"].items():
        print(f"      {status:<20} {count:>6,}")

    print("\n" + "=" * 60)
    print("  COMMISSIONING QUALITY CHECKS")
    print("=" * 60)
    cm_checks = check_commissioning(commissioning)
    print(f"   Total commissioning:        {cm_checks['total_commissioning']:>6,}")
    print(f"   Missing Comm_Date:          {cm_checks['missing_comm_date']:>6,}")
    print(f"   Completed commissioning:    {cm_checks['completed_commissioning']:>6,}")

    # Quality Score calculation
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
    print(f"   Total records (all tables): {total_records:>10,}")
    print(f"   Total issues found:         {total_issues:>10,}")
    print(f"   Data Quality Score:         {score:>9.2f}%")

    if score >= 98:
        print("   Status: ✅ EXCELLENT")
    elif score >= 95:
        print("   Status: 🟢 GOOD")
    elif score >= 90:
        print("   Status: 🟡 ACCEPTABLE — needs cleaning")
    else:
        print("   Status: 🔴 POOR — must clean before reporting")

    # Save to Excel
    print("\n💾 Saving detailed report...")
    os.makedirs(REPORTS_DIR, exist_ok=True)
    output_path = os.path.join(REPORTS_DIR, "Day4_Data_Quality_Report.xlsx")

    report_data = {
        "Check": [
            "Total Customers",
            "Missing Contact_Number",
            "Duplicate Customer_IDs",
            "Unique Districts (raw)",
            "Wrong District Case",
            "District Extra Spaces",
            "Approved Customers",
            "Total Installations",
            "Negative Capacity",
            "Zero Capacity",
            "Future Dates",
            "Invalid Dates",
            "Bad Status Values",
            "Completed Installations",
            "Total Commissioning",
            "Missing Commissioning Date",
            "Completed Commissioning",
            "Total Records",
            "Total Issues",
            "Data Quality Score (%)",
        ],
        "Value": [
            c_checks["total_customers"],
            c_checks["missing_contact"],
            c_checks["duplicate_customer_ids"],
            c_checks["unique_districts_raw"],
            c_checks["wrong_district_case"],
            c_checks["district_extra_spaces"],
            c_checks["approved_customers"],
            i_checks["total_installations"],
            i_checks["negative_capacity"],
            i_checks["zero_capacity"],
            i_checks["future_dates"],
            i_checks["invalid_dates"],
            i_checks["bad_status"],
            i_checks["completed_installations"],
            cm_checks["total_commissioning"],
            cm_checks["missing_comm_date"],
            cm_checks["completed_commissioning"],
            total_records,
            total_issues,
            score,
        ],
    }
    report_df = pd.DataFrame(report_data)
    report_df.to_excel(output_path, index=False, sheet_name="Quality_Summary")
    print(f"   ✅ Saved: {output_path}")

    print("\n" + "=" * 60)
    print("  🎉 DAY 4 QUALITY CHECK COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()