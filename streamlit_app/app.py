"""
app.py
------
Solar Program MIS — Streamlit Web Application
Day 15: Basic setup and home page.
"""

import streamlit as st
import sqlite3
import pandas as pd
import os

# =====================================================
# PAGE CONFIGURATION (ওয়েব পেজের সেটিংস)
# =====================================================
st.set_page_config(
    page_title="Solar Program MIS",
    page_icon="🌞",
    layout="wide"
)

# =====================================================
# DATABASE PATH
# =====================================================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "solar_program.db")


# =====================================================
# DATABASE CONNECTION
# =====================================================
@st.cache_resource
def get_connection():
    """Connect to SQLite database."""
    return sqlite3.connect(DB_PATH, check_same_thread=False)


# =====================================================
# MAIN APP
# =====================================================
def main():
    # --- Header ---
    st.title("🌞 Solar Program MIS")
    st.markdown("### Data Management & Monitoring System")
    st.markdown("---")

    # --- Sidebar ---
    with st.sidebar:
        st.header("⚙️ Navigation")
        st.info("Select a page from the menu above (or below) to get started.")

    # --- Welcome Message ---
    st.markdown("""
    Welcome to the **Solar Program MIS** application. 
    
    This web app allows you to:
    - 📊 View dashboard analytics
    - 👥 Manage customer database
    - 🔧 Track installations
    - ✅ Check commissioning status
    - 📈 Generate reports
    
    Use the sidebar to navigate.
    """)

    # --- Test Database Connection ---
    st.markdown("---")
    st.subheader("🗄️ Database Connection Test")

    try:
        conn = get_connection()
        query = "SELECT COUNT(*) AS total FROM customers"
        df = pd.read_sql_query(query, conn)
        total_customers = df["total"].iloc[0]

        query2 = "SELECT COUNT(*) AS total FROM installations"
        df2 = pd.read_sql_query(query2, conn)
        total_installations = df2["total"].iloc[0]

        col1, col2 = st.columns(2)
        col1.metric("Total Customers", f"{total_customers:,}")
        col2.metric("Total Installations", f"{total_installations:,}")

        st.success("✅ Database connected successfully!")
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")


if __name__ == "__main__":
    main()