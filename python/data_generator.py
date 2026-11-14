"""
data_generator.py
-----------------
Generates synthetic dataset for a Rooftop Solar Program in Bangladesh.
Creates 4 CSV files with realistic data and controlled quality issues.

Author: [Your Name]
Date: Day 3 of 30-day project
"""

import random
import csv
import os
from datetime import datetime, timedelta
import numpy as np

# =====================================================
# 1. SETUP: Random seed for reproducibility
# =====================================================
random.seed(42)
np.random.seed(42)

# =====================================================
# 2. CONSTANTS: Bangladesh districts and regions
# =====================================================
REGION_DISTRICTS = {
    "North":   ["Rangpur", "Dinajpur", "Bogura", "Rajshahi"],
    "Central": ["Dhaka", "Gazipur", "Tangail", "Mymensingh"],
    "South":   ["Chattogram", "Cox's Bazar", "Khulna", "Barishal"],
    "East":    ["Sylhet", "Cumilla", "Brahmanbaria"],
    "West":    ["Jashore", "Kushtia", "Faridpur"],
}

UPAZILAS = {
    "Dhaka": ["Savar", "Keraniganj", "Dhamrai"],
    "Gazipur": ["Kaliakair", "Sreepur", "Kapasia"],
    "Tangail": ["Mirzapur", "Kalihati", "Ghatail"],
    "Chattogram": ["Patiya", "Sitakunda", "Hathazari"],
    "Sylhet": ["Beanibazar", "Golapganj", "Zakiganj"],
    "Rajshahi": ["Bagha", "Charghat", "Puthia"],
}

CUSTOMER_TYPES = ["Residential", "Commercial", "Institutional", "Industrial"]

# Synthetic Bangladeshi names
FIRST_NAMES = ["Rahim", "Karim", "Salma", "Fatima", "Hasan", "Jahangir",
               "Nasrin", "Rafiq", "Shilpi", "Anwar", "Sumaiya", "Tanvir",
               "Mizanur", "Sultana", "Kamal", "Rehana", "Sohel", "Nusrat",
               "Rakib", "Murshida"]

LAST_NAMES = ["Uddin", "Islam", "Akter", "Hossain", "Rahman", "Begum",
              "Alam", "Khan", "Sarker", "Ahmed"]

# =====================================================
# 3. HELPER FUNCTIONS
# =====================================================

def random_name():
    """Generate a synthetic Bangladeshi name."""
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def random_phone():
    """Generate a synthetic BD phone number. NOT a real number."""
    prefixes = ["017", "018", "019", "016"]
    return random.choice(prefixes) + "".join(
        [str(random.randint(0, 9)) for _ in range(8)]
    )


def random_date(start_days=730, end_days=0):
    """Return a random date between (today - start_days) and (today - end_days)."""
    today = datetime.today()
    delta = random.randint(end_days, start_days)
    return (today - timedelta(days=delta)).strftime("%Y-%m-%d")


def pick_region_for_district(district):
    """Find which region a district belongs to."""
    for region, districts in REGION_DISTRICTS.items():
        if district in districts:
            return region
    return "Unknown"


def add_quality_issues(value, probability=0.03):
    """
    Randomly corrupt a value with given probability.
    Used to introduce realistic data quality problems.
    """
    if random.random() > probability:
        return value
    # Corrupt types: None, empty, whitespace, wrong case
    return random.choice([None, "", "  ", str(value).lower(),
                          str(value).upper() + " "])

# =====================================================
# 4. DATA GENERATORS
# =====================================================

def generate_customers(n=5200):
    """
    Generate customer records.
    Include controlled quality issues: duplicates, missing, wrong district names.
    """
    customers = []
    all_districts = [d for ds in REGION_DISTRICTS.values() for d in ds]

    for i in range(n):
        district = random.choice(all_districts)
        region = pick_region_for_district(district)

        # Get upazila — fallback if not predefined
        upazila = random.choice(UPAZILAS.get(district, ["Sadar"]))

        # ------ INTRODUCE QUALITY ISSUES ------
        # 1. Occasionally use wrong district spelling
        if random.random() < 0.02:
            district = random.choice([
                district.lower(),
                district.upper(),
                f" {district}",
                district.replace("a", "@")
            ])

        # 2. Missing contact number sometimes
        contact = random_phone()
        if random.random() < 0.03:
            contact = None

        customers.append({
            "Customer_ID": f"CUST-{i+1:05d}",
            "Customer_Name": random_name(),
            "District": district,
            "Region": region,
            "Upazila": upazila,
            "Customer_Type": random.choice(CUSTOMER_TYPES),
            "Registration_Date": random_date(start_days=900, end_days=30),
            "Contact_Number": contact,
            "Application_Status": random.choices(
                ["Pending", "Approved", "Rejected", "Completed"],
                weights=[10, 60, 5, 25], k=1
            )[0]
        })

    # Add ~30 duplicate customer IDs
    for _ in range(30):
        dup = random.choice(customers).copy()
        customers.append(dup)

    return customers


def generate_installations(customers):
    """
    Generate installation records for APPROVED/COMPLETED customers.
    Include invalid capacity values, wrong statuses, invalid dates.
    """
    installations = []
    approved = [c for c in customers
                if c["Application_Status"] in ("Approved", "Completed")]

    for i, cust in enumerate(approved):
        # Solar capacity (KW): residential 1-5, commercial 5-20, etc.
        if cust["Customer_Type"] == "Residential":
            capacity = round(random.uniform(1.0, 5.0), 1)
        elif cust["Customer_Type"] == "Commercial":
            capacity = round(random.uniform(5.0, 20.0), 1)
        elif cust["Customer_Type"] == "Institutional":
            capacity = round(random.uniform(10.0, 50.0), 1)
        else:  # Industrial
            capacity = round(random.uniform(20.0, 100.0), 1)

        # Installation status weighted
        status = random.choices(
            ["Planned", "In_Progress", "Completed", "Cancelled"],
            weights=[15, 10, 70, 5], k=1
        )[0]

        # Inspection status
        if status == "Completed":
            inspection = random.choices(
                ["Passed", "Failed", "Pending"],
                weights=[90, 5, 5], k=1
            )[0]
        else:
            inspection = "Pending"

        # Cost in BDT — roughly 80,000 BDT per KW
        cost = round(capacity * random.uniform(70000, 95000), 0)

        # ------ INTRODUCE QUALITY ISSUES ------
        # 1. Some negative capacity
        if random.random() < 0.02:
            capacity = -capacity

        # 2. Some zero capacity
        if random.random() < 0.015:
            capacity = 0.0

        # 3. Some invalid dates (future date)
        inst_date = random_date(start_days=700, end_days=0)
        if random.random() < 0.02:
            future = datetime.today() + timedelta(days=random.randint(10, 365))
            inst_date = future.strftime("%Y-%m-%d")

        # 4. Wrong status spelling occasionally
        if random.random() < 0.01:
            status = random.choice(["complete", "Complete", "COMPLETED", "done"])

        installations.append({
            "Installation_ID": f"INST-{i+1:05d}",
            "Customer_ID": cust["Customer_ID"],
            "Solar_Capacity_KW": capacity,
            "Installation_Date": inst_date,
            "Installation_Status": status,
            "Installer_ID": f"INS-{random.randint(1, 50):03d}",
            "Installation_Cost": cost,
            "Inspection_Status": inspection
        })

    return installations


def generate_commissioning(installations):
    """Generate commissioning records for COMPLETED installations."""
    commissioned = []
    completed = [i for i in installations
                 if i["Installation_Status"] == "Completed"]

    for i, inst in enumerate(completed):
        # 85% commissioned, 10% pending, 5% failed
        status = random.choices(
            ["Completed", "Pending", "Failed"],
            weights=[85, 10, 5], k=1
        )[0]

        if status == "Completed":
            # Commissioning date ~10-30 days after installation
            try:
                inst_dt = datetime.strptime(inst["Installation_Date"], "%Y-%m-%d")
                comm_dt = inst_dt + timedelta(days=random.randint(5, 30))
                comm_date = comm_dt.strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                comm_date = random_date(start_days=600, end_days=0)

            test_result = random.choices(
                ["Pass", "Fail"], weights=[95, 5], k=1
            )[0]
        else:
            comm_date = None
            test_result = None

        # ------ QUALITY ISSUE: 3% missing dates ------
        if random.random() < 0.03:
            comm_date = None

        commissioned.append({
            "Commissioning_ID": f"COMM-{i+1:05d}",
            "Customer_ID": inst["Customer_ID"],
            "Commissioning_Date": comm_date,
            "Commissioning_Status": status,
            "System_Test_Result": test_result
        })

    return commissioned


def generate_regional_reports(months=12):
    """
    Generate monthly regional reports.
    Each month → each region → each district sends one report.
    """
    reports = []
    report_id = 1
    today = datetime.today()

    for m in range(months):
        month_start = today.replace(day=1) - timedelta(days=30 * m)
        report_date = month_start.strftime("%Y-%m-%d")

        for region, districts in REGION_DISTRICTS.items():
            for district in districts:
                submitted = random.randint(20, 150)
                verified = random.randint(int(submitted * 0.7), submitted)
                pending = submitted - verified

                status = random.choices(
                    ["Submitted", "Verified", "Rejected", "Pending"],
                    weights=[20, 60, 5, 15], k=1
                )[0]

                # ------ QUALITY ISSUE: missing data 2% ------
                if random.random() < 0.02:
                    verified = None

                reports.append({
                    "Report_ID": f"RPT-{report_id:05d}",
                    "Region": region,
                    "District": district,
                    "Report_Date": report_date,
                    "Submitted_Installations": submitted,
                    "Verified_Installations": verified,
                    "Pending_Installations": pending,
                    "Report_Status": status
                })
                report_id += 1

    return reports


# =====================================================
# 5. FILE WRITER
# =====================================================

def write_csv(data, filename, fieldnames):
    """Write a list of dicts to CSV file."""
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"✅ Wrote {len(data):,} records → {filename}")


# =====================================================
# 6. MAIN
# =====================================================

def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(project_root, "data", "raw")
    os.makedirs(output_dir, exist_ok=True)

    print("🌞 Generating Synthetic Solar Program Dataset...\n")

    # Generate
    customers = generate_customers(5200)
    installations = generate_installations(customers)
    commissioning = generate_commissioning(installations)
    reports = generate_regional_reports(months=12)

    # Write to CSV
    write_csv(
        customers,
        os.path.join(output_dir, "customers.csv"),
        ["Customer_ID", "Customer_Name", "District", "Region", "Upazila",
         "Customer_Type", "Registration_Date", "Contact_Number",
         "Application_Status"]
    )
    write_csv(
        installations,
        os.path.join(output_dir, "installations.csv"),
        ["Installation_ID", "Customer_ID", "Solar_Capacity_KW",
         "Installation_Date", "Installation_Status", "Installer_ID",
         "Installation_Cost", "Inspection_Status"]
    )
    write_csv(
        commissioning,
        os.path.join(output_dir, "commissioning.csv"),
        ["Commissioning_ID", "Customer_ID", "Commissioning_Date",
         "Commissioning_Status", "System_Test_Result"]
    )
    write_csv(
        reports,
        os.path.join(output_dir, "regional_reports.csv"),
        ["Report_ID", "Region", "District", "Report_Date",
         "Submitted_Installations", "Verified_Installations",
         "Pending_Installations", "Report_Status"]
    )

    print("\n🎉 Dataset generation complete!")
    print(f"📁 Files saved to: {os.path.abspath(output_dir)}")


if __name__ == "__main__":
    main()
    