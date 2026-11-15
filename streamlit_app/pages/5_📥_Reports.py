"""
5_📥_Reports.py
---------------
Generate and download reports from the live database.
"""

import streamlit as st
import sqlite3
import pandas as pd
import os
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Reports", page_icon="📥", layout="wide")
st.title("📥 Management Reports")
st.markdown("Generate and download reports directly from the SQLite database.")
st.markdown("---")

# DB Path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "solar_program.db")

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

conn = get_connection()

# =====================================================
# Report 1: District-wise Performance
# =====================================================
st.subheader("1. District-wise Installation Summary")

query_district = """
    SELECT 
        c.District, 
        c.Region,
        COUNT(i.Installation_ID) AS Total_Installations,
        ROUND(SUM(CASE WHEN i.Installation_Status = 'Completed' THEN i.Solar_Capacity_KW ELSE 0 END), 2) AS Completed_KW
    FROM customers c
    LEFT JOIN installations i ON c.Customer_ID = i.Customer_ID
    GROUP BY c.District, c.Region
    ORDER BY Total_Installations DESC
"""
df_district = pd.read_sql_query(query_district, conn)

st.dataframe(df_district, use_container_width=True)

# Download button for District Report
def convert_df_to_excel(df):
    """Convert DataFrame to Excel bytes for download."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='District_Summary')
    return output.getvalue()

excel_data = convert_df_to_excel(df_district)
st.download_button(
    label="📥 Download District Report (Excel)",
    data=excel_data,
    file_name=f"District_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.markdown("---")

# =====================================================
# Report 2: Monthly Installation Trend
# =====================================================
st.subheader("2. Monthly Installation Trend")

query_monthly = """
    SELECT 
        strftime('%Y-%m', Installation_Date) AS Month,
        COUNT(Installation_ID) AS Total_Installs,
        ROUND(SUM(Solar_Capacity_KW), 2) AS Total_KW
    FROM installations
    WHERE Installation_Status = 'Completed' AND Installation_Date IS NOT NULL
    GROUP BY Month
    ORDER BY Month DESC
    LIMIT 12
"""
df_monthly = pd.read_sql_query(query_monthly, conn)

st.dataframe(df_monthly, use_container_width=True)

# Download button for Monthly Report
excel_data_monthly = convert_df_to_excel(df_monthly)
st.download_button(
    label="📥 Download Monthly Report (Excel)",
    data=excel_data_monthly,
    file_name=f"Monthly_Trend_{datetime.now().strftime('%Y%m%d')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    key="monthly_download"
)

st.markdown("---")
st.info("💡 **Tip:** These reports are generated live from the SQLite database. Any new data entered in the Customers or Installations page will immediately reflect here.")