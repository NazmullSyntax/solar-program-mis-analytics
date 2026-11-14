# KPI Definitions — Solar Program MIS

## Volume KPIs
| # | KPI | Formula | Owner |
|---|-----|---------|-------|
| 1 | Total Customers | COUNT(DISTINCT Customer_ID) | Data Officer |
| 2 | Total Installed Systems | COUNT(Installation_ID WHERE status='Completed') | Operations |
| 3 | Total Solar Capacity (KW) | SUM(Solar_Capacity_KW WHERE status='Completed') | Operations |
| 4 | Total Commissioned Systems | COUNT(Commissioning_ID WHERE status='Completed') | Field Team |

## Rate KPIs
| # | KPI | Formula | Target |
|---|-----|---------|--------|
| 5 | Installation Completion Rate | (Completed ÷ Approved) × 100 | ≥ 80% |
| 6 | Commissioning Completion Rate | (Commissioned ÷ Installed) × 100 | ≥ 90% |
| 7 | Inspection Pass Rate | (Passed ÷ Total Inspections) × 100 | ≥ 95% |

## Data Quality KPIs
| # | KPI | Formula | Target |
|---|-----|---------|--------|
| 8 | Data Quality Score | (Valid ÷ Total) × 100 | ≥ 98% |
| 9 | Duplicate Rate | (Duplicates ÷ Total) × 100 | ≤ 1% |

## Geographic KPIs
| # | KPI | Formula |
|---|-----|---------|
| 10 | District-wise Installation | COUNT GROUP BY District |
| 11 | Region-wise Capacity | SUM(KW) GROUP BY Region |

## Time-based KPIs
| # | KPI | Formula |
|---|-----|---------|
| 12 | Monthly Installation Trend | COUNT GROUP BY Month |