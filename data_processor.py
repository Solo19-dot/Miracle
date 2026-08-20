import pandas as pd
import re


# =========================================================
# COLUMN ALIASES
# =========================================================

COLUMN_ALIASES = {

    # Exposure data
    "Facility_ID": [
        "facility_id",
        "facility id",
        "facility",
        "plant",
        "plant id",
        "plant name",
        "site",
        "site id",
        "location"
    ],

  "Period_Date": [
    "period_date",
    "period date",
    "month",
    "reporting month",
    "reporting period"
],

"Date": [
    "date",
    "incident date",
    "event date",
    "accident date",
    "occurrence date",
    "date of incident"
],

    "Man_Hours": [
        "man_hours",
        "man hours",
        "manhours",
        "hours worked",
        "employee hours",
        "work hours",
        "labour hours",
        "labor hours",
        "total hours"
    ],

    "Scope1_CO2e": [
        "scope1_co2e",
        "scope 1 co2e",
        "scope 1",
        "scope1",
        "scope 1 emissions",
        "scope 1 co2e emissions"
    ],

    "Scope2_CO2e": [
        "scope2_co2e",
        "scope 2 co2e",
        "scope 2",
        "scope2",
        "scope 2 emissions",
        "scope 2 co2e emissions"
    ],

    "Production_Tons": [
        "production_tons",
        "production tons",
        "production tonnes",
        "production tonnage",
        "production",
        "output tons",
        "output tonnes"
    ],

    "Water_m3": [
        "water_m3",
        "water m3",
        "water",
        "water consumption",
        "water usage",
        "water use",
        "water consumed"
    ],

    "Total_Waste_MT": [
        "total_waste_mt",
        "total waste mt",
        "total waste",
        "waste",
        "waste generated",
        "total waste generated"
    ],

    "Recycled_Waste_MT": [
        "recycled_waste_mt",
        "recycled waste mt",
        "recycled waste",
        "recycled",
        "recycled waste amount",
        "waste recycled"
    ],

    # Incident data
    "Event_Classification": [
        "event_classification",
        "event classification",
        "incident type",
        "incident classification",
        "event type",
        "case type",
        "incident category",
        "classification"
    ],

    "DART_Case": [
        "dart_case",
        "dart case",
        "dart",
        "dart case?",
        "days away restricted transfer"
    ],

    "Actual_Lost_Days": [
        "actual_lost_days",
        "actual lost days",
        "lost days",
        "days lost",
        "actual days lost",
        "lost time days"
    ],

    "Scheduled_Charges": [
        "scheduled_charges",
        "scheduled charges",
        "scheduled days",
        "charges",
        "scheduled charge days"
    ]
}


# =========================================================
# NORMALIZE COLUMN NAME
# =========================================================

def normalize_column_name(column):

    column = str(column).strip().lower()

    column = re.sub(
        r"[^a-z0-9]+",
        " ",
        column
    )

    return column.strip()


# =========================================================
# FIND MATCHING COLUMN
# =========================================================

def find_matching_column(
    dataframe_columns,
    aliases
):

    normalized_columns = {
        column: normalize_column_name(column)
        for column in dataframe_columns
    }

    normalized_aliases = [
        normalize_column_name(alias)
        for alias in aliases
    ]

    # Exact normalized match
    for original, normalized in normalized_columns.items():

        if normalized in normalized_aliases:
            return original

    return None


# =========================================================
# STANDARDIZE DATAFRAME COLUMNS
# =========================================================

def standardize_columns(
    df: pd.DataFrame
):

    df = df.copy()

    mapping = {}

    for standard_name, aliases in COLUMN_ALIASES.items():

        match = find_matching_column(
            df.columns,
            aliases
        )

        if match is not None:

            mapping[match] = standard_name

    df = df.rename(
        columns=mapping
    )

    return df, mapping


# =========================================================
# IDENTIFY DATASET TYPE
# =========================================================

def identify_dataset(df):

    standardized_df, mapping = standardize_columns(df)

    columns = set(
        standardized_df.columns
    )

    exposure_fields = {
        "Facility_ID",
        "Period_Date",
        "Man_Hours",
        "Scope1_CO2e",
        "Scope2_CO2e",
        "Production_Tons",
        "Water_m3",
        "Total_Waste_MT",
        "Recycled_Waste_MT"
    }

    incident_fields = {
        "Facility_ID",
        "Date",
        "Event_Classification",
        "DART_Case",
        "Actual_Lost_Days",
        "Scheduled_Charges"
    }

    exposure_score = len(
        columns.intersection(
            exposure_fields
        )
    )

    incident_score = len(
        columns.intersection(
            incident_fields
        )
    )

    # Exposure dataset requires the core fields
    if (
        "Facility_ID" in columns
        and "Period_Date" in columns
        and "Man_Hours" in columns
    ):

        return (
            "Exposure",
            standardized_df,
            mapping,
            exposure_score
        )

    # Incident dataset requires the core fields
    if (
        "Facility_ID" in columns
        and "Date" in columns
        and "Event_Classification" in columns
    ):

        return (
            "Incidents",
            standardized_df,
            mapping,
            incident_score
        )

    return (
        "Unknown",
        standardized_df,
        mapping,
        max(
            exposure_score,
            incident_score
        )
    )