import streamlit as st
import sqlite3
import pandas as pd
import os

st.set_page_config(page_title="Data Quality", page_icon="🛡️", layout="wide")
st.title("🛡️ Data Quality Dashboard")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "solar_program.db")

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

conn = get_connection()

# Calculate quality metrics via SQL
query = """
    SELECT 
        (SELECT COUNT(*) FROM customers WHERE Contact_Number = 'MISSING') AS missing_contact,
        (SELECT COUNT(*) FROM installations WHERE Solar_Capacity_KW <= 0 OR Solar_Capacity_KW IS NULL) AS bad_capacity,
        (SELECT COUNT(*) FROM commissioning WHERE Commissioning_Date IS NULL AND Commissioning_Status = 'Completed') AS missing_comm_date,
        (SELECT COUNT(*) FROM customers) AS total_cust
"""
kpi = pd.read_sql_query(query, conn).iloc[0]

col1, col2, col3 = st.columns(3)
col1.metric("Missing Contacts", kpi['missing_contact'])
col2.metric("Bad Capacity", kpi['bad_capacity'])
col3.metric("Missing Comm Date", kpi['missing_comm_date'])

st.markdown("---")
st.subheader("Missing Contact Details (Sample)")
missing_df = pd.read_sql_query("SELECT Customer_ID, Customer_Name, District FROM customers WHERE Contact_Number = 'MISSING' LIMIT 50", conn)
st.dataframe(missing_df, use_container_width=True)