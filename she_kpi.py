import pandas as pd
import numpy as np


def build_she_kpi_pipeline(
    exposure_df: pd.DataFrame,
    incidents_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate monthly SHE (Safety, Health & Environment) KPIs
    by facility.

    Parameters
    ----------
    exposure_df : pd.DataFrame
        Monthly operational/exposure data.

    incidents_df : pd.DataFrame
        Individual incident records.

    Returns
    -------
    pd.DataFrame
        Monthly SHE KPI results by facility.
    """

    # ---------------------------------------------------------
    # 1. Validate required columns
    # ---------------------------------------------------------

    exposure_required = {
        "Facility_ID",
        "Period_Date",
        "Man_Hours",
        "Scope1_CO2e",
        "Scope2_CO2e",
        "Production_Tons",
        "Water_m3",
        "Total_Waste_MT",
        "Recycled_Waste_MT",
    }

    incidents_required = {
        "Facility_ID",
        "Date",
        "Event_Classification",
        "DART_Case",
        "Actual_Lost_Days",
        "Scheduled_Charges",
    }

    missing_exposure = exposure_required - set(exposure_df.columns)
    missing_incidents = incidents_required - set(incidents_df.columns)

    if missing_exposure:
        raise ValueError(
            f"Missing exposure columns: {sorted(missing_exposure)}"
        )

    if missing_incidents:
        raise ValueError(
            f"Missing incident columns: {sorted(missing_incidents)}"
        )

    # ---------------------------------------------------------
    # 2. Work with copies so original data is not modified
    # ---------------------------------------------------------

    exposure = exposure_df.copy()
    incidents = incidents_df.copy()

    # ---------------------------------------------------------
    # 3. Convert dates to monthly periods
    # ---------------------------------------------------------

    exposure["Period_Date"] = (
        pd.to_datetime(exposure["Period_Date"], errors="coerce")
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    incidents["Period_Date"] = (
        pd.to_datetime(incidents["Date"], errors="coerce")
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    # Check for invalid dates
    if exposure["Period_Date"].isna().any():
        raise ValueError(
            "Exposure data contains invalid Period_Date values."
        )

    if incidents["Period_Date"].isna().any():
        raise ValueError(
            "Incident data contains invalid Date values."
        )

    # ---------------------------------------------------------
    # 4. Clean numeric incident fields
    # ---------------------------------------------------------

    incidents["Actual_Lost_Days"] = pd.to_numeric(
        incidents["Actual_Lost_Days"],
        errors="coerce"
    ).fillna(0)

    incidents["Scheduled_Charges"] = pd.to_numeric(
        incidents["Scheduled_Charges"],
        errors="coerce"
    ).fillna(0)

    # ---------------------------------------------------------
    # 5. Create incident classification flags
    # ---------------------------------------------------------

    incidents["Is_Recordable"] = incidents[
        "Event_Classification"
    ].isin([
        "Fatal",
        "LTI",
        "Restricted",
        "Medical_Aid"
    ])

    incidents["Is_LTI"] = incidents[
        "Event_Classification"
    ].isin([
        "Fatal",
        "LTI"
    ])

    incidents["Is_DART"] = (
        incidents["DART_Case"]
        .astype(str)
        .str.lower()
        .isin(["true", "1", "yes"])
    )

    incidents["Total_Days_Charged"] = (
        incidents["Actual_Lost_Days"]
        + incidents["Scheduled_Charges"]
    )

    # ---------------------------------------------------------
    # 6. Aggregate incident data
    # ---------------------------------------------------------

    incident_summary = (
        incidents
        .groupby(
            ["Facility_ID", "Period_Date"],
            as_index=False
        )
        .agg(
            Total_Recordables=(
                "Is_Recordable",
                "sum"
            ),

            Total_LTIs=(
                "Is_LTI",
                "sum"
            ),

            Total_DART_Cases=(
                "Is_DART",
                "sum"
            ),

            Total_Days_Lost=(
                "Actual_Lost_Days",
                "sum"
            ),

            Total_Days_Charged=(
                "Total_Days_Charged",
                "sum"
            ),

            Near_Miss_Count=(
                "Event_Classification",
                lambda x: (x == "Near_Miss").sum()
            ),
        )
    )

    # ---------------------------------------------------------
    # 7. Clean exposure data
    # ---------------------------------------------------------

    numeric_columns = [
        "Man_Hours",
        "Scope1_CO2e",
        "Scope2_CO2e",
        "Production_Tons",
        "Water_m3",
        "Total_Waste_MT",
        "Recycled_Waste_MT",
    ]

    for column in numeric_columns:
        exposure[column] = pd.to_numeric(
            exposure[column],
            errors="coerce"
        ).fillna(0)

    # ---------------------------------------------------------
    # 8. Merge exposure and incident data
    # ---------------------------------------------------------

    merged = pd.merge(
        exposure,
        incident_summary,
        on=["Facility_ID", "Period_Date"],
        how="left"
    )

    # Missing incident values mean zero incidents
    incident_columns = [
        "Total_Recordables",
        "Total_LTIs",
        "Total_DART_Cases",
        "Total_Days_Lost",
        "Total_Days_Charged",
        "Near_Miss_Count",
    ]

    merged[incident_columns] = (
        merged[incident_columns]
        .fillna(0)
    )

    # ---------------------------------------------------------
    # 9. Calculate Safety KPIs
    # ---------------------------------------------------------

    merged["TRIR"] = np.where(
        merged["Man_Hours"] > 0,
        (
            merged["Total_Recordables"] * 200_000
        ) / merged["Man_Hours"],
        0
    )

    merged["LTIFR"] = np.where(
        merged["Man_Hours"] > 0,
        (
            merged["Total_LTIs"] * 1_000_000
        ) / merged["Man_Hours"],
        0
    )

    merged["DART_Rate"] = np.where(
        merged["Man_Hours"] > 0,
        (
            merged["Total_DART_Cases"] * 200_000
        ) / merged["Man_Hours"],
        0
    )

    merged["DISR"] = np.where(
        merged["Man_Hours"] > 0,
        (
            merged["Total_Days_Charged"] * 1_000_000
        ) / merged["Man_Hours"],
        0
    )

    merged["ADCDI"] = np.where(
        merged["Total_LTIs"] > 0,
        (
            merged["Total_Days_Charged"]
            / merged["Total_LTIs"]
        ),
        0
    )

    # ---------------------------------------------------------
    # 10. Calculate Environmental KPIs
    # ---------------------------------------------------------

    merged["Total_GHG_CO2e"] = (
        merged["Scope1_CO2e"]
        + merged["Scope2_CO2e"]
    )

    merged["GHG_Intensity_MT_per_Ton"] = np.where(
        merged["Production_Tons"] > 0,
        (
            merged["Total_GHG_CO2e"]
            / merged["Production_Tons"]
        ),
        0
    )

    merged["Water_Intensity_m3_per_Ton"] = np.where(
        merged["Production_Tons"] > 0,
        (
            merged["Water_m3"]
            / merged["Production_Tons"]
        ),
        0
    )

    merged["Waste_Diversion_Rate_Pct"] = np.where(
        merged["Total_Waste_MT"] > 0,
        (
            merged["Recycled_Waste_MT"]
            / merged["Total_Waste_MT"]
        ) * 100,
        0
    )

    # ---------------------------------------------------------
    # 11. Organise results
    # ---------------------------------------------------------

    merged = merged.sort_values(
        ["Period_Date", "Facility_ID"]
    ).reset_index(drop=True)

    # Round calculated values
    numeric_result_columns = merged.select_dtypes(
        include="number"
    ).columns

    merged[numeric_result_columns] = (
        merged[numeric_result_columns]
        .round(3)
    )

    return merged

if __name__ == "__main__":

    print("Loading SHE data...")

    exposure_df = pd.read_excel(
        "SHE_Sample_Data.xlsx",
        sheet_name="Exposure"
    )

    incidents_df = pd.read_excel(
        "SHE_Sample_Data.xlsx",
        sheet_name="Incidents"
    )

    print("Calculating SHE KPIs...")

    results = build_she_kpi_pipeline(
        exposure_df,
        incidents_df
    )

    print("\nSHE KPI RESULTS")
    print("=" * 60)

    print(results)

    results.to_excel(
        "SHE_KPI_Results.xlsx",
        index=False
    )

    print("\n" + "=" * 60)
    print("KPI calculation completed successfully!")
    print("Results saved to SHE_KPI_Results.xlsx")
    print("=" * 60)