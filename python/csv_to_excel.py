"""
csv_to_excel.py
---------------
Convert all CSV files in data/raw/ to .xlsx Excel files.
Run this from the PROJECT ROOT folder (solar-program-mis-analytics/).

Author: [Your Name]
Day 4 - Excel Data Management
"""

import os
import pandas as pd

# =====================================================
# PATH SETUP — works no matter where you run this from
# =====================================================
# __file__ = path to THIS script
# os.path.dirname(__file__) = python/ folder
# os.path.dirname(...) one more time = PROJECT ROOT
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")

FILES = ["customers", "installations", "commissioning", "regional_reports"]


def convert_all():
    """Read each CSV and save as .xlsx"""
    print("🔄 Starting conversion...\n")
    print(f"📁 Looking in: {RAW_DIR}\n")

    if not os.path.exists(RAW_DIR):
        print(f"❌ ERROR: Folder not found: {RAW_DIR}")
        print("   Did you run data_generator.py first?")
        return

    success_count = 0

    for name in FILES:
        csv_path = os.path.join(RAW_DIR, f"{name}.csv")
        xlsx_path = os.path.join(RAW_DIR, f"{name}.xlsx")

        if not os.path.exists(csv_path):
            print(f"⚠️  Skipped (not found): {csv_path}")
            continue

        df = pd.read_csv(csv_path)
        df.to_excel(xlsx_path, index=False, engine="openpyxl")
        print(f"✅ {name}.csv → {name}.xlsx  ({len(df):,} rows)")
        success_count += 1

    print(f"\n🎉 Done! {success_count} file(s) converted.")


if __name__ == "__main__":
    convert_all()