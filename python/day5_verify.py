"""
day5_verify.py
--------------
Verify Day 5 Pivot Table outputs by computing the same aggregations in pandas.

Author: [Your Name]
Day 5 - Pivot Table Verification
"""

import os
import pandas as pd

# =====================================================
# PATH SETUP
# =====================================================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEANED_DIR = os.path.join(PROJECT_ROOT, "data", "cleaned")

# Fixed simulation date (must match Day 3/4 scripts)
SIMULATION_DATE = pd.Timestamp("2025-11-15")


def main():
    print("=" * 60)
    print("  📊 DAY 5 — PIVOT TABLE VERIFICATION")
    print(f"  Simulation date: {SIMULATION_DATE.strftime('%Y-%m-%d')}")
    print("=" * 60)

    # ---- Load ----
    customers = pd.read_csv(os.path.join(CLEANED_DIR, "customers_clean.csv"))
    installations = pd.read_csv(os.path.join(CLEANED_DIR, "installations_clean.csv"))

    print(f"\n✅ Loaded {len(customers):,} customers, {len(installations):,} installations")

    # ---- VLOOKUP simulation via merge ----
    merged = installations.merge(
        customers[["Customer_ID", "District", "Region", "Customer_Type"]],
        on="Customer_ID",
        how="left"
    )
    print(f"✅ Merged: {len(merged):,} rows")
    print(f"   Missing District after merge: {merged['District'].isnull().sum()}")

    # ---- District Summary ----
    print("\n" + "=" * 60)
    print("  DISTRICT-WISE SUMMARY (Top 10 by installations)")
    print("=" * 60)
    district_summary = (
        merged.groupby("District")
        .agg(
            Installations=("Installation_ID", "count"),
            Total_KW=("Solar_Capacity_KW", "sum"),
            Total_Cost=("Installation_Cost", "sum")
        )
        .sort_values("Installations", ascending=False)
        .head(10)
        .round(2)
    )
    print(district_summary.to_string())

    # ---- Region Summary ----
    print("\n" + "=" * 60)
    print("  REGION-WISE SUMMARY")
    print("=" * 60)
    region_summary = (
        merged.groupby("Region")
        .agg(
            Installations=("Installation_ID", "count"),
            Total_KW=("Solar_Capacity_KW", "sum")
        )
        .sort_values("Installations", ascending=False)
    )
    region_summary["Share_%"] = (
        region_summary["Installations"] / region_summary["Installations"].sum() * 100
    ).round(2)
    print(region_summary.to_string())

    # ---- Monthly Trend ----
    print("\n" + "=" * 60)
    print("  MONTHLY INSTALLATION TREND (Last 12 months)")
    print("=" * 60)
    merged["Installation_Date"] = pd.to_datetime(
        merged["Installation_Date"], errors="coerce"
    )
    merged["Month"] = merged["Installation_Date"].dt.to_period("M")
    monthly = (
        merged.dropna(subset=["Installation_Date"])
        .groupby("Month")
        .agg(Installations=("Installation_ID", "count"))
        .sort_index()
        .tail(12)
    )
    print(monthly.to_string())

    # ---- Status Distribution ----
    print("\n" + "=" * 60)
    print("  INSTALLATION STATUS DISTRIBUTION")
    print("=" * 60)
    print(merged["Installation_Status"].value_counts().to_string())

    # ---- KPI Summary ----
    print("\n" + "=" * 60)
    print("  📊 KEY METRICS")
    print("=" * 60)
    total_install = len(merged)
    completed = (merged["Installation_Status"] == "Completed").sum()
    total_kw = merged["Solar_Capacity_KW"].sum()

    print(f"   Total Customers:            {len(customers):>8,}")
    print(f"   Total Installations:        {total_install:>8,}")
    print(f"   Completed Installations:    {completed:>8,}")
    print(f"   Total Capacity (KW):        {total_kw:>10,.2f}")
    print(f"   Installation Completion %:  {completed/total_install*100:>7.2f}%")

    print("\n" + "=" * 60)
    print("  🎉 Day 5 verification complete")
    print("=" * 60)
    print("\n💡 Compare these numbers with your Excel Pivot Tables.")
    print("   If they match → your Excel report is correct!")


if __name__ == "__main__":
    main()