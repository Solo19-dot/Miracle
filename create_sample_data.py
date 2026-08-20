import pandas as pd


# =========================================================
# SAMPLE EXPOSURE / ENVIRONMENTAL DATA
# =========================================================

exposure_data = [
    # Blantyre Plant
    ["BLT001", "2026-01-01", 150000, 120, 80, 5000, 2500, 100, 70],
    ["BLT001", "2026-02-01", 155000, 125, 82, 5200, 2600, 105, 75],
    ["BLT001", "2026-03-01", 160000, 130, 85, 5400, 2700, 110, 78],
    ["BLT001", "2026-04-01", 158000, 128, 83, 5300, 2650, 108, 80],
    ["BLT001", "2026-05-01", 162000, 132, 87, 5500, 2750, 112, 84],
    ["BLT001", "2026-06-01", 165000, 135, 89, 5600, 2800, 115, 88],

    # Lilongwe Plant
    ["LLW001", "2026-01-01", 140000, 110, 75, 4500, 2200, 90, 60],
    ["LLW001", "2026-02-01", 145000, 114, 77, 4700, 2300, 94, 66],
    ["LLW001", "2026-03-01", 148000, 117, 79, 4800, 2400, 97, 70],
    ["LLW001", "2026-04-01", 150000, 119, 80, 4900, 2450, 100, 73],
    ["LLW001", "2026-05-01", 153000, 122, 82, 5000, 2500, 103, 77],
    ["LLW001", "2026-06-01", 156000, 125, 84, 5100, 2550, 106, 81],

    # Mzuzu Plant
    ["MZU001", "2026-01-01", 120000, 95, 65, 3800, 1900, 80, 50],
    ["MZU001", "2026-02-01", 123000, 98, 67, 3900, 1950, 82, 55],
    ["MZU001", "2026-03-01", 126000, 101, 69, 4000, 2000, 85, 60],
    ["MZU001", "2026-04-01", 128000, 103, 70, 4100, 2050, 87, 63],
    ["MZU001", "2026-05-01", 130000, 105, 72, 4200, 2100, 90, 68],
    ["MZU001", "2026-06-01", 133000, 108, 74, 4300, 2150, 93, 72],
]


exposure_columns = [
    "Facility_ID",
    "Period_Date",
    "Man_Hours",
    "Scope1_CO2e",
    "Scope2_CO2e",
    "Production_Tons",
    "Water_m3",
    "Total_Waste_MT",
    "Recycled_Waste_MT",
]


exposure_df = pd.DataFrame(
    exposure_data,
    columns=exposure_columns
)


# =========================================================
# SAMPLE INCIDENT DATA
# =========================================================

incident_data = [
    # -----------------------------------------------------
    # BLANTYRE
    # -----------------------------------------------------

    ["BLT001", "2026-01-08", "Near_Miss", False, 0, 0],
    ["BLT001", "2026-01-15", "LTI", True, 5, 2],
    ["BLT001", "2026-01-22", "Medical_Aid", False, 0, 0],

    ["BLT001", "2026-02-05", "Near_Miss", False, 0, 0],
    ["BLT001", "2026-02-14", "Restricted", True, 0, 4],

    ["BLT001", "2026-03-03", "Near_Miss", False, 0, 0],
    ["BLT001", "2026-03-18", "LTI", True, 8, 3],
    ["BLT001", "2026-03-25", "Near_Miss", False, 0, 0],

    ["BLT001", "2026-04-10", "Medical_Aid", False, 0, 0],
    ["BLT001", "2026-04-20", "Near_Miss", False, 0, 0],

    ["BLT001", "2026-05-05", "LTI", True, 4, 2],
    ["BLT001", "2026-05-19", "Near_Miss", False, 0, 0],

    ["BLT001", "2026-06-07", "Near_Miss", False, 0, 0],
    ["BLT001", "2026-06-21", "Medical_Aid", False, 0, 0],

    # -----------------------------------------------------
    # LILONGWE
    # -----------------------------------------------------

    ["LLW001", "2026-01-05", "Near_Miss", False, 0, 0],
    ["LLW001", "2026-01-19", "Medical_Aid", False, 0, 0],

    ["LLW001", "2026-02-08", "LTI", True, 3, 1],
    ["LLW001", "2026-02-25", "Near_Miss", False, 0, 0],

    ["LLW001", "2026-03-11", "Restricted", True, 0, 3],
    ["LLW001", "2026-03-27", "Near_Miss", False, 0, 0],

    ["LLW001", "2026-04-09", "Near_Miss", False, 0, 0],
    ["LLW001", "2026-04-18", "Medical_Aid", False, 0, 0],

    ["LLW001", "2026-05-06", "LTI", True, 6, 2],
    ["LLW001", "2026-05-23", "Near_Miss", False, 0, 0],

    ["LLW001", "2026-06-12", "Near_Miss", False, 0, 0],

    # -----------------------------------------------------
    # MZUZU
    # -----------------------------------------------------

    ["MZU001", "2026-01-10", "Near_Miss", False, 0, 0],

    ["MZU001", "2026-02-04", "Medical_Aid", False, 0, 0],
    ["MZU001", "2026-02-16", "Near_Miss", False, 0, 0],

    ["MZU001", "2026-03-08", "LTI", True, 4, 2],
    ["MZU001", "2026-03-22", "Near_Miss", False, 0, 0],

    ["MZU001", "2026-04-14", "Near_Miss", False, 0, 0],

    ["MZU001", "2026-05-03", "Medical_Aid", False, 0, 0],
    ["MZU001", "2026-05-17", "Near_Miss", False, 0, 0],

    ["MZU001", "2026-06-09", "Near_Miss", False, 0, 0],
]


incident_columns = [
    "Facility_ID",
    "Date",
    "Event_Classification",
    "DART_Case",
    "Actual_Lost_Days",
    "Scheduled_Charges",
]


incidents_df = pd.DataFrame(
    incident_data,
    columns=incident_columns
)


# =========================================================
# SAVE TO EXCEL
# =========================================================

with pd.ExcelWriter(
    "SHE_Sample_Data.xlsx",
    engine="openpyxl"
) as writer:

    exposure_df.to_excel(
        writer,
        sheet_name="Exposure",
        index=False
    )

    incidents_df.to_excel(
        writer,
        sheet_name="Incidents",
        index=False
    )


print("========================================")
print("SHE SAMPLE DATA CREATED SUCCESSFULLY")
print("========================================")
print()
print("File created: SHE_Sample_Data.xlsx")
print()
print(f"Exposure records: {len(exposure_df)}")
print(f"Incident records: {len(incidents_df)}")
print()
print("Sheets:")
print("- Exposure")
print("- Incidents")