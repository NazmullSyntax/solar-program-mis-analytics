import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import date

st.set_page_config(page_title="Customers", page_icon="👥", layout="wide")
st.title("👥 Customer Database")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "solar_program.db")

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

conn = get_connection()

# Tab layout
tab1, tab2 = st.tabs(["🔍 View & Search", "➕ Add New Customer"])

with tab1:
    st.subheader("Search Customers")
    
    # Search box
    search_query = st.text_input("Search by Name, ID, or District", "")
    
    # Query building
    query = "SELECT Customer_ID, Customer_Name, District, Region, Customer_Type, Application_Status FROM customers"
    if search_query:
        query += f" WHERE Customer_Name LIKE '%{search_query}%' OR Customer_ID LIKE '%{search_query}%' OR District LIKE '%{search_query}%'"
    
    df = pd.read_sql_query(query, conn)
    st.dataframe(df, use_container_width=True, height=400)
    st.caption(f"Total records found: {len(df)}")

with tab2:
    st.subheader("Register New Customer")
    
    with st.form("new_customer_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Customer Name*")
            new_district = st.selectbox("District", ["Dhaka", "Chattogram", "Sylhet", "Khulna", "Rajshahi", "Gazipur", "Bogura", "Rangpur"])
            new_contact = st.text_input("Contact Number", "017")
        with col2:
            new_type = st.selectbox("Customer Type", ["Residential", "Commercial", "Institutional", "Industrial"])
            new_region = st.selectbox("Region", ["Central", "South", "East", "West", "North"])
            new_status = st.selectbox("Status", ["Pending", "Approved"])
            
        submit = st.form_submit_button("Save Customer")
        
        if submit:
            if new_name:
                # Generate next ID
                max_id_df = pd.read_sql_query("SELECT Customer_ID FROM customers ORDER BY Customer_ID DESC LIMIT 1", conn)
                if not max_id_df.empty:
                    last_id = max_id_df['Customer_ID'].iloc[0]
                    new_id = f"CUST-{int(last_id.split('-')[1]) + 1:05d}"
                else:
                    new_id = "CUST-00001"
                
                # Insert
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO customers (Customer_ID, Customer_Name, District, Region, Upazila, Customer_Type, Registration_Date, Contact_Number, Application_Status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (new_id, new_name, new_district, new_region, "Sadar", new_type, date.today().strftime("%Y-%m-%d"), new_contact, new_status))
                conn.commit()
                st.success(f"✅ Customer {new_name} added successfully with ID: {new_id}")
                st.rerun()
            else:
                st.error("❌ Name is required!")