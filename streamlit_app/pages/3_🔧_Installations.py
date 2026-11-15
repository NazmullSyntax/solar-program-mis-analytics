import streamlit as st
import sqlite3
import pandas as pd
import os

st.set_page_config(page_title="Installations", page_icon="🔧", layout="wide")
st.title("🔧 Installation Tracking")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "solar_program.db")

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

conn = get_connection()

# Load installations
query = """
    SELECT i.Installation_ID, c.Customer_Name, c.District, i.Solar_Capacity_KW, i.Installation_Status, i.Installation_Date
    FROM installations i
    JOIN customers c ON i.Customer_ID = c.Customer_ID
"""
df = pd.read_sql_query(query, conn)

st.subheader("Filter Installations")
status_filter = st.multiselect("Filter by Status", ["Completed", "In_Progress", "Planned", "Cancelled"], default=["Completed"])

if status_filter:
    filtered_df = df[df['Installation_Status'].isin(status_filter)]
else:
    filtered_df = df

st.dataframe(filtered_df, use_container_width=True)

# Update Status
st.markdown("---")
st.subheader("Update Installation Status")

install_id = st.selectbox("Select Installation ID", df['Installation_ID'].tolist())
new_status = st.selectbox("New Status", ["Completed", "In_Progress", "Planned", "Cancelled"])

if st.button("Update Status"):
    cursor = conn.cursor()
    cursor.execute("UPDATE installations SET Installation_Status = ? WHERE Installation_ID = ?", (new_status, install_id))
    conn.commit()
    st.success(f"✅ Updated {install_id} to {new_status}")
    st.rerun()