"""
data_quality_system.py
----------------------
Automated Data Quality Validation System.

Features:
  - 6-dimension quality checks (Completeness, Uniqueness, Validity, etc.)
  - Weighted scoring by severity
  - HTML dashboard report
  - Production-ready modular design

Author: [Your Name]
Day 10 - Data Quality System
"""

import os
import pandas as pd
from datetime import datetime

# =====================================================
# CONFIGURATION
# =====================================================
SIMULATION_DATE = pd.Timestamp("2025-11-15")
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEANED_DIR = os.path.join(PROJECT_ROOT, "data", "cleaned")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")

# Severity weights
SEVERITY_WEIGHTS = {
    "critical": 3.0,   # Business-breaking
    "high": 2.0,       # Report-breaking
    "medium": 1.0,     # Operational
    "low": 0.5,        # Informational
}


# =====================================================
# DATA QUALITY CHECKER CLASS
# =====================================================
class DataQualityChecker:
    """
    Automated data quality validation for solar program data.
    """

    def __init__(self, customers, installations, commissioning):
        self.customers = customers
        self.installations = installations
        self.commissioning = commissioning
        self.issues = []

    def _add_issue(self, dimension, name, count, severity, total, table):
        """Register an issue."""
        self.issues.append({
            "Dimension": dimension,
            "Issue": name,
            "Count": count,
            "Total": total,
            "Percent": round(count / total * 100, 2) if total > 0 else 0,
            "Severity": severity,
            "Weight": SEVERITY_WEIGHTS[severity],
            "Weighted_Count": count * SEVERITY_WEIGHTS[severity],
            "Table": table,
        })

    # ---------- DIMENSION 1: COMPLETENESS ----------
    def check_completeness(self):
        """Check missing values."""
        # Customers
        n = len(self.customers)
        missing_contact = (
            self.customers["Contact_Number"].isnull().sum() +
            (self.customers["Contact_Number"] == "MISSING").sum()
        )
        self._add_issue(
            "Completeness", "Missing Contact_Number",
            missing_contact, "medium", n, "Customers"
        )

        missing_district = self.customers["District"].isnull().sum()
        self._add_issue(
            "Completeness", "Missing District",
            missing_district, "high", n, "Customers"
        )

        # Commissioning
        nc = len(self.commissioning)
        missing_comm = self.commissioning["Commissioning_Date"].isnull().sum()
        self._add_issue(
            "Completeness", "Missing Commissioning_Date",
            missing_comm, "low", nc, "Commissioning"
        )

    # ---------- DIMENSION 2: UNIQUENESS ----------
    def check_uniqueness(self):
        """Check duplicates."""
        n = len(self.customers)
        dup_cust = self.customers["Customer_ID"].duplicated().sum()
        self._add_issue(
            "Uniqueness", "Duplicate Customer_IDs",
            dup_cust, "critical", n, "Customers"
        )

        ni = len(self.installations)
        dup_inst = self.installations["Installation_ID"].duplicated().sum()
        self._add_issue(
            "Uniqueness", "Duplicate Installation_IDs",
            dup_inst, "critical", ni, "Installations"
        )

    # ---------- DIMENSION 3: VALIDITY ----------
    def check_validity(self):
        """Check business rule violations."""
        ni = len(self.installations)

        # Capacity should be positive
        bad_capacity = (self.installations["Solar_Capacity_KW"] <= 0).sum()
        self._add_issue(
            "Validity", "Non-positive Capacity",
            bad_capacity, "critical", ni, "Installations"
        )

        # Valid status values
        valid_statuses = {"Planned", "In_Progress", "Completed", "Cancelled"}
        bad_status = (~self.installations["Installation_Status"].isin(valid_statuses)).sum()
        self._add_issue(
            "Validity", "Invalid Installation Status",
            bad_status, "high", ni, "Installations"
        )

    # ---------- DIMENSION 4: CONSISTENCY ----------
    def check_consistency(self):
        """Check cross-column consistency."""
        # Customer district consistency
        n = len(self.customers)
        unknown_district = (self.customers["District"] == "Unknown").sum()
        self._add_issue(
            "Consistency", "Unknown Districts",
            unknown_district, "high", n, "Customers"
        )

        # Comm status vs date
        nc = len(self.commissioning)
        inconsistent_comm = (
            (self.commissioning["Commissioning_Status"] == "Completed") &
            (self.commissioning["Commissioning_Date"].isnull())
        ).sum()
        self._add_issue(
            "Consistency", "Completed Commissioning Without Date",
            inconsistent_comm, "high", nc, "Commissioning"
        )

    # ---------- DIMENSION 5: TIMELINESS ----------
    def check_timeliness(self):
        """Check future/impossible dates."""
        ni = len(self.installations)
        install_dates = pd.to_datetime(
            self.installations["Installation_Date"], errors="coerce"
        )
        future_install = (install_dates > SIMULATION_DATE).sum()
        self._add_issue(
            "Timeliness", "Future Installation Dates",
            future_install, "high", ni, "Installations"
        )

        nc = len(self.commissioning)
        comm_dates = pd.to_datetime(
            self.commissioning["Commissioning_Date"], errors="coerce"
        )
        future_comm = (comm_dates > SIMULATION_DATE).sum()
        self._add_issue(
            "Timeliness", "Future Commissioning Dates",
            future_comm, "high", nc, "Commissioning"
        )

    # ---------- CALCULATE SCORE ----------
    def calculate_score(self):
        """Calculate weighted and unweighted scores."""
        total_records = (
            len(self.customers) +
            len(self.installations) +
            len(self.commissioning)
        )

        # Filter out issues from raw records counts
        # (weighted score = sum of weighted issues on total records)
        total_weighted_issues = sum(
            issue["Weighted_Count"] for issue in self.issues
        )
        total_raw_issues = sum(issue["Count"] for issue in self.issues)

        weighted_score = (
            (total_records - total_weighted_issues) / total_records * 100
            if total_records > 0 else 0
        )
        raw_score = (
            (total_records - total_raw_issues) / total_records * 100
            if total_records > 0 else 0
        )

        return {
            "total_records": total_records,
            "total_raw_issues": total_raw_issues,
            "total_weighted_issues": round(total_weighted_issues, 1),
            "raw_score": round(raw_score, 2),
            "weighted_score": round(weighted_score, 2),
        }

    # ---------- HTML REPORT ----------
    def generate_html_report(self, output_path):
        """Generate a professional HTML dashboard."""
        summary = self.calculate_score()

        # Build issues table HTML
        issues_html = ""
        for issue in self.issues:
            severity_color = {
                "critical": "#dc3545",
                "high": "#fd7e14",
                "medium": "#ffc107",
                "low": "#28a745",
            }[issue["Severity"]]
            issues_html += f"""
            <tr>
                <td>{issue['Dimension']}</td>
                <td>{issue['Issue']}</td>
                <td>{issue['Count']:,}</td>
                <td>{issue['Percent']}%</td>
                <td><span style="color: white; background: {severity_color};
                    padding: 2px 8px; border-radius: 4px; font-size: 0.9em;">
                    {issue['Severity'].upper()}</span></td>
                <td>{issue['Weight']}x</td>
                <td>{issue['Weighted_Count']:.1f}</td>
            </tr>
            """

        # Build HTML
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Solar Program — Data Quality Dashboard</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f4f6f8;
            margin: 0;
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }}
        h1 {{
            color: #1f4e78;
            margin: 0 0 8px 0;
        }}
        .subtitle {{
            color: #666;
            margin-bottom: 24px;
        }}
        .cards {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 32px;
        }}
        .card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            border-left: 4px solid #1f4e78;
        }}
        .card.alert {{
            border-left-color: #dc3545;
            background: #fff5f5;
        }}
        .card.good {{
            border-left-color: #28a745;
            background: #f0fff4;
        }}
        .card .label {{
            font-size: 0.85em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }}
        .card .value {{
            font-size: 2em;
            font-weight: 700;
            color: #1f4e78;
        }}
        .card.alert .value {{
            color: #dc3545;
        }}
        .card.good .value {{
            color: #28a745;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 16px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }}
        th {{
            background: #1f4e78;
            color: white;
            font-weight: 600;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .footer {{
            margin-top: 32px;
            text-align: center;
            color: #999;
            font-size: 0.85em;
        }}
    </style>
</head>
<body>
<div class="container">
    <h1>🌞 Solar Program — Data Quality Dashboard</h1>
    <p class="subtitle">
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} |
        Simulation date: {SIMULATION_DATE.strftime('%Y-%m-%d')}
    </p>

    <div class="cards">
        <div class="card">
            <div class="label">Total Records</div>
            <div class="value">{summary['total_records']:,}</div>
        </div>
        <div class="card alert">
            <div class="label">Total Issues</div>
            <div class="value">{summary['total_raw_issues']:,}</div>
        </div>
        <div class="card good">
            <div class="label">Raw Score</div>
            <div class="value">{summary['raw_score']}%</div>
        </div>
        <div class="card good">
            <div class="label">Weighted Score</div>
            <div class="value">{summary['weighted_score']}%</div>
        </div>
    </div>

    <h2>📋 Issues Breakdown</h2>
    <table>
        <thead>
            <tr>
                <th>Dimension</th>
                <th>Issue</th>
                <th>Count</th>
                <th>%</th>
                <th>Severity</th>
                <th>Weight</th>
                <th>Weighted</th>
            </tr>
        </thead>
        <tbody>
            {issues_html}
        </tbody>
    </table>

    <div class="footer">
        Solar Program MIS — Data Quality System v1.0 |
        Generated by Data Management Officer
    </div>
</div>
</body>
</html>
        """

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        return output_path


# =====================================================
# MAIN
# =====================================================
def main():
    print("=" * 60)
    print("  🌞 DAY 10 — DATA QUALITY VALIDATION SYSTEM")
    print(f"  Simulation date: {SIMULATION_DATE.strftime('%Y-%m-%d')}")
    print("=" * 60)

    # Load
    print("\n📂 Loading cleaned data (v2)...")
    customers = pd.read_csv(os.path.join(CLEANED_DIR, "customers_v2.csv"))
    installations = pd.read_csv(os.path.join(CLEANED_DIR, "installations_v2.csv"))
    commissioning = pd.read_csv(os.path.join(CLEANED_DIR, "commissioning_v2.csv"))
    print(f"   ✅ Customers:     {len(customers):,}")
    print(f"   ✅ Installations: {len(installations):,}")
    print(f"   ✅ Commissioning: {len(commissioning):,}")

    # Run all checks
    print("\n🔍 Running quality checks...")
    checker = DataQualityChecker(customers, installations, commissioning)

    checker.check_completeness()
    print("   ✅ Completeness")
    checker.check_uniqueness()
    print("   ✅ Uniqueness")
    checker.check_validity()
    print("   ✅ Validity")
    checker.check_consistency()
    print("   ✅ Consistency")
    checker.check_timeliness()
    print("   ✅ Timeliness")

    # Print results
    print("\n" + "=" * 60)
    print("  📊 ISSUES FOUND")
    print("=" * 60)
    print(f"   {'Dimension':<15} {'Issue':<35} {'Count':>6} {'Severity':>10}")
    print("   " + "-" * 70)
    for issue in checker.issues:
        print(f"   {issue['Dimension']:<15} {issue['Issue']:<35} "
              f"{issue['Count']:>6} {issue['Severity']:>10}")

    # Summary
    summary = checker.calculate_score()
    print("\n" + "=" * 60)
    print("  📈 QUALITY SUMMARY")
    print("=" * 60)
    print(f"   Total records:         {summary['total_records']:>10,}")
    print(f"   Raw issues:            {summary['total_raw_issues']:>10,}")
    print(f"   Weighted issues:       {summary['total_weighted_issues']:>10,.1f}")
    print(f"   Raw Score:             {summary['raw_score']:>9.2f}%")
    print(f"   Weighted Score:        {summary['weighted_score']:>9.2f}%")

    # Rating
    score = summary["weighted_score"]
    if score >= 98:
        rating = "✅ EXCELLENT"
    elif score >= 95:
        rating = "🟢 GOOD"
    elif score >= 90:
        rating = "🟡 ACCEPTABLE"
    else:
        rating = "🔴 POOR"
    print(f"   Rating:                {rating}")

    # Save HTML
    print("\n💾 Generating HTML dashboard...")
    os.makedirs(REPORTS_DIR, exist_ok=True)
    html_path = os.path.join(REPORTS_DIR, "Data_Quality_Dashboard.html")
    checker.generate_html_report(html_path)
    print(f"   ✅ Saved: {html_path}")

    # Save Excel
    print("\n💾 Generating Excel summary...")
    excel_path = os.path.join(REPORTS_DIR, "Day10_Quality_Summary.xlsx")
    issues_df = pd.DataFrame(checker.issues)
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        issues_df.to_excel(writer, sheet_name="Issues", index=False)
        pd.DataFrame([summary]).to_excel(writer, sheet_name="Summary", index=False)
    print(f"   ✅ Saved: {excel_path}")

    print("\n" + "=" * 60)
    print("  🎉 DAY 10 QUALITY SYSTEM COMPLETE")
    print("=" * 60)
    print("\n💡 Open the HTML dashboard in your browser:")
    print(f"   start {html_path}")


if __name__ == "__main__":
    main()