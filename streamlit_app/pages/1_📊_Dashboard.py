"""
1_📊_Dashboard.py
-----------------
Interactive Dashboard for Solar Program.
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import os

# Page setup
st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
st.title("📊 Program Dashboard")
st.markdown("Executive overview of solar installations across Bangladesh.")
st.markdown("---")

# DB Path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "solar_program.db")

@st.cache_resource
def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

conn = get_connection()

# =====================================================
# 1. KPI Cards (Top Row)
# =====================================================
# Querying total metrics
query_kpi = """
    SELECT 
        (SELECT COUNT(*) FROM customers) AS total_customers,
        (SELECT COUNT(*) FROM installations) AS total_installs,
        (SELECT ROUND(SUM(Solar_Capacity_KW), 2) FROM installations WHERE Installation_Status = 'Completed') AS total_kw
"""
kpi_df = pd.read_sql_query(query_kpi, conn)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Total Customers 👥", value=f"{kpi_df['total_customers'].iloc[0]:,}")
with col2:
    st.metric(label="Total Installations 🔧", value=f"{kpi_df['total_installs'].iloc[0]:,}")
with col3:
    st.metric(label="Total Capacity ⚡", value=f"{kpi_df['total_kw'].iloc[0]:,.2f} KW")

st.markdown("---")

# =====================================================
# 2. Charts (Middle Row)
# =====================================================
col_left, col_right = st.columns(2)

# Chart 1: Region-wise Capacity
with col_left:
    st.subheader("Capacity by Region")
    query_region = """
        SELECT c.Region, SUM(i.Solar_Capacity_KW) AS total_kw
        FROM installations i
        JOIN customers c ON i.Customer_ID = c.Customer_ID
        WHERE i.Installation_Status = 'Completed'
        GROUP BY c.Region
    """
    df_region = pd.read_sql_query(query_region, conn)
    
    fig_bar = px.bar(
        df_region, 
        x='Region', 
        y='total_kw', 
        color='Region',
        text_auto='.2s',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_bar.update_layout(showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)

# Chart 2: Installation Status Distribution
with col_right:
    st.subheader("Installation Status")
    query_status = """
        SELECT Installation_Status, COUNT(*) AS count
        FROM installations
        GROUP BY Installation_Status
    """
    df_status = pd.read_sql_query(query_status, conn)
    
    fig_pie = px.pie(
        df_status, 
        names='Installation_Status', 
        values='count', 
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# =====================================================
# 3. Data Table (Bottom Row)
# =====================================================
st.subheader("Latest Installations (Top 10)")
query_latest = """
    SELECT 
        i.Installation_ID, 
        c.Customer_Name, 
        c.District, 
        i.Solar_Capacity_KW, 
        i.Installation_Status
    FROM installations i
    JOIN customers c ON i.Customer_ID = c.Customer_ID
    ORDER BY i.Installation_Date DESC
    LIMIT 10
"""
df_latest = pd.read_sql_query(query_latest, conn)
st.dataframe(df_latest, use_container_width=True)
