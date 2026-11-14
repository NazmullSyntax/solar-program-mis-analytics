# Solar Program Business Process

## 1. Overview
This document describes the end-to-end workflow of a Rooftop Solar Program
in Bangladesh (reference: ESDO DRS Rooftop Solar Program model).

## 2. Process Steps
| Step | Activity | Data Created |
|------|----------|--------------|
| 1 | Customer Inquiry | Name, phone (not in system yet) |
| 2 | Registration | Customer_ID, District, Region, Upazila, Type, Reg_Date |
| 3 | Site Survey | Feasibility notes |
| 4 | Quotation | Installation_Cost |
| 5 | Installation | Installation_Date, Capacity_KW, Installer_ID |
| 6 | Inspection | Inspection_Status |
| 7 | Commissioning | Commissioning_Date, Test_Result |

## 3. Regions & Districts
| Region | Districts |
|--------|-----------|
| North | Rangpur, Dinajpur, Bogura, Rajshahi |
| Central | Dhaka, Gazipur, Tangail, Mymensingh |
| South | Chattogram, Cox's Bazar, Khulna, Barishal |
| East | Sylhet, Cumilla, Brahmanbaria |
| West | Jashore, Kushtia, Faridpur |

## 4. Customer Types
Residential, Commercial, Institutional, Industrial

## 5. Status Values (Standard)
- Application_Status: Pending, Approved, Rejected, Completed
- Installation_Status: Planned, In_Progress, Completed, Cancelled
- Inspection_Status: Pending, Passed, Failed
- Commissioning_Status: Pending, Completed, Failed
- Report_Status: Submitted, Verified, Rejected, Pending

## 6. Data Flow
Regional Office (Excel) → data/raw/ → Python cleaning →
data/cleaned/ → SQLite DB → PowerBI / Streamlit / Reports