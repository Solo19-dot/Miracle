import streamlit as st
import pandas as pd
import plotly.express as px
import pdfplumber

from docx import Document

from she_kpi import build_she_kpi_pipeline
from data_processor import identify_dataset


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="SHE Performance Dashboard",
    page_icon="🛡️",
    layout="wide"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .main {
        background-color: #f5f7fa;
    }

    .dashboard-title {
        font-size: 36px;
        font-weight: 700;
        margin-bottom: 0;
    }

    .dashboard-subtitle {
        font-size: 16px;
        color: #666666;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 24px;
        font-weight: 600;
        margin-top: 25px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# REQUIRED COLUMNS
# =========================================================

EXPOSURE_COLUMNS = {
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

INCIDENT_COLUMNS = {
    "Facility_ID",
    "Date",
    "Event_Classification",
    "DART_Case",
    "Actual_Lost_Days",
    "Scheduled_Charges",
}


# =========================================================
# FILE READING FUNCTIONS
# =========================================================

def read_excel_file(uploaded_file):

    excel_file = pd.ExcelFile(uploaded_file)

    sheets = {}

    for sheet in excel_file.sheet_names:

        sheets[sheet] = pd.read_excel(
            uploaded_file,
            sheet_name=sheet
        )

    return sheets


def read_csv_file(uploaded_file):

    return {
        "CSV_Data": pd.read_csv(uploaded_file)
    }


def read_word_file(uploaded_file):

    document = Document(uploaded_file)

    tables = {}

    for index, table in enumerate(document.tables):

        rows = []

        for row in table.rows:

            rows.append(
                [cell.text.strip() for cell in row.cells]
            )

        if len(rows) >= 2:

            df = pd.DataFrame(
                rows[1:],
                columns=rows[0]
            )

            tables[
                f"Word_Table_{index + 1}"
            ] = df

    return tables


def read_pdf_file(uploaded_file):

    tables = {}

    table_number = 1

    with pdfplumber.open(uploaded_file) as pdf:

        for page_number, page in enumerate(pdf.pages):

            extracted_tables = page.extract_tables()

            for table in extracted_tables:

                if not table or len(table) < 2:
                    continue

                headers = table[0]
                rows = table[1:]

                if not headers:
                    continue

                df = pd.DataFrame(
                    rows,
                    columns=headers
                )

                tables[
                    f"PDF_Page_{page_number + 1}_Table_{table_number}"
                ] = df

                table_number += 1

    return tables


def read_uploaded_file(uploaded_file):

    file_name = uploaded_file.name.lower()

    if file_name.endswith(".xlsx") or file_name.endswith(".xls"):

        return read_excel_file(uploaded_file)

    elif file_name.endswith(".csv"):

        return read_csv_file(uploaded_file)

    elif file_name.endswith(".docx"):

        return read_word_file(uploaded_file)

    elif file_name.endswith(".pdf"):

        return read_pdf_file(uploaded_file)

    else:

        raise ValueError(
            "Unsupported file type."
        )


# =========================================================
# DATASET DETECTION
# =========================================================

def detect_she_datasets(tables):

    exposure_df = None
    incidents_df = None

    exposure_score = 0
    incident_score = 0

    detected_info = []

    for name, df in tables.items():

        if df is None or df.empty:
            continue

        (
            dataset_type,
            standardized_df,
            mapping,
            score
        ) = identify_dataset(df)

        detected_info.append({
            "source": name,
            "type": dataset_type,
            "score": score,
            "mapping": mapping
        })

        if dataset_type == "Exposure":

            if score > exposure_score:

                exposure_score = score
                exposure_df = standardized_df.copy()

        elif dataset_type == "Incidents":

            if score > incident_score:

                incident_score = score
                incidents_df = standardized_df.copy()

    return (
        exposure_df,
        incidents_df,
        exposure_score,
        incident_score,
        detected_info
    )


# =========================================================
# LOAD SAMPLE DATA
# =========================================================

@st.cache_data
def load_sample_data():

    exposure_df = pd.read_excel(
        "SHE_Sample_Data.xlsx",
        sheet_name="Exposure"
    )

    incidents_df = pd.read_excel(
        "SHE_Sample_Data.xlsx",
        sheet_name="Incidents"
    )

    results = build_she_kpi_pipeline(
        exposure_df,
        incidents_df
    )

    return results, incidents_df


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="dashboard-title">'
    '🛡️ SHE Performance Dashboard'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="dashboard-subtitle">'
    'Safety • Health • Environment Performance Monitoring'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR - DATA SOURCE
# =========================================================

st.sidebar.header("📂 Data Source")

data_mode = st.sidebar.radio(
    "Choose data source",
    [
        "Use Sample Data",
        "Upload SHE Documents"
    ]
)


# =========================================================
# DEFAULT VALUES
# =========================================================

detected_info = []


# =========================================================
# SAMPLE DATA
# =========================================================

if data_mode == "Use Sample Data":

    results, incidents = load_sample_data()

    st.sidebar.success(
        "Using sample SHE data."
    )


# =========================================================
# UPLOADED DATA
# =========================================================

else:

    st.sidebar.info(
        "Upload Excel, CSV, Word or PDF SHE documents."
    )

    uploaded_files = st.sidebar.file_uploader(
        "Upload documents",
        type=[
            "xlsx",
            "xls",
            "csv",
            "docx",
            "pdf"
        ],
        accept_multiple_files=True
    )

    if not uploaded_files:

        st.info(
            "👈 Upload one or more SHE documents "
            "from the sidebar to begin."
        )

        st.stop()

    all_tables = {}

    # -----------------------------------------------------
    # READ UPLOADED DOCUMENTS
    # -----------------------------------------------------

    for uploaded_file in uploaded_files:

        try:

            extracted_tables = read_uploaded_file(
                uploaded_file
            )

            for table_name, df in extracted_tables.items():

                all_tables[
                    f"{uploaded_file.name} - {table_name}"
                ] = df

        except Exception as error:

            st.error(
                f"Could not read {uploaded_file.name}: "
                f"{error}"
            )

    # -----------------------------------------------------
    # CHECK TABLES
    # -----------------------------------------------------

    if not all_tables:

        st.error(
            "No readable tables were found in the "
            "uploaded documents."
        )

        st.stop()

    # -----------------------------------------------------
    # DETECT SHE DATA
    # -----------------------------------------------------

    (
        exposure_df,
        incidents_df,
        exposure_score,
        incident_score,
        detected_info
    ) = detect_she_datasets(all_tables)

    # -----------------------------------------------------
    # SIDEBAR DETECTION RESULTS
    # -----------------------------------------------------

    st.sidebar.markdown("---")

    st.sidebar.subheader(
        "🔍 Detected Data"
    )

    for item in detected_info:

        if item["type"] == "Unknown":

            st.sidebar.warning(
                f"⚠️ {item['source']}: "
                "Unknown dataset"
            )

        else:

            st.sidebar.success(
                f"✅ {item['source']}: "
                f"{item['type']}"
            )

    # -----------------------------------------------------
    # MATCH SCORES
    # -----------------------------------------------------

    st.sidebar.markdown("---")

    st.sidebar.subheader(
        "Data Detection"
    )

    st.sidebar.write(
        f"Exposure match: "
        f"{exposure_score}/{len(EXPOSURE_COLUMNS)}"
    )

    st.sidebar.write(
        f"Incident match: "
        f"{incident_score}/{len(INCIDENT_COLUMNS)}"
    )

    # -----------------------------------------------------
    # VALIDATE EXPOSURE DATA
    # -----------------------------------------------------

    if exposure_df is None:

        st.error(
            "❌ I could not identify an Exposure dataset."
        )

        st.write(
            "The uploaded document should contain information "
            "such as Facility, Date/Period, Man Hours and "
            "Production."
        )

        st.stop()

    # -----------------------------------------------------
    # VALIDATE INCIDENT DATA
    # -----------------------------------------------------

    if incidents_df is None:

        st.error(
            "❌ I could not identify an Incident dataset."
        )

        st.write(
            "The uploaded document should contain information "
            "such as Facility, Date, Event Classification "
            "and DART Case."
        )

        st.stop()

    # -----------------------------------------------------
    # RUN KPI ENGINE
    # -----------------------------------------------------

    try:

        results = build_she_kpi_pipeline(
            exposure_df,
            incidents_df
        )

        incidents = incidents_df

        st.sidebar.success(
            "✅ SHE data successfully processed."
        )

    except Exception as error:

        st.error(
            f"❌ The SHE data could not be processed: "
            f"{error}"
        )

        st.stop()

    # -----------------------------------------------------
    # COLUMN MAPPING
    # -----------------------------------------------------

   # =========================================================
# AUTOMATIC COLUMN MAPPING
# =========================================================

st.markdown(
    '<div class="section-title">'
    '🔎 Automatic Data Mapping'
    '</div>',
    unsafe_allow_html=True
)

st.info(
    "The dashboard automatically matches columns from your "
    "uploaded documents to the SHE data structure."
)


if detected_info:

    for item in detected_info:

        st.markdown(
            f"### 📄 {item['source']}"
        )

        # Dataset type
        if item["type"] == "Exposure":

            st.success(
                f"✅ Detected as Exposure Data "
                f"(Match score: {item['score']})"
            )

        elif item["type"] == "Incidents":

            st.success(
                f"✅ Detected as Incident Data "
                f"(Match score: {item['score']})"
            )

        else:

            st.warning(
                "⚠️ Dataset type could not be determined."
            )

        # Mapping table
        if item["mapping"]:

            mapping_rows = []

            for original, standard in item["mapping"].items():

                mapping_rows.append({
                    "Uploaded Column": original,
                    "SHE Column": standard,
                    "Status": "✅ Recognized"
                })

            mapping_df = pd.DataFrame(
                mapping_rows
            )

            st.dataframe(
                mapping_df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.warning(
                "No recognizable SHE columns were found."
            )

else:

    st.info(
        "Upload a SHE document to see automatic column mapping."
    )

# =========================================================
# DASHBOARD FILTERS
# =========================================================

st.sidebar.markdown("---")

st.sidebar.header("🔎 Dashboard Filters")


facilities = [
    "All Facilities"
] + sorted(
    results["Facility_ID"]
    .astype(str)
    .unique()
    .tolist()
)


selected_facility = st.sidebar.selectbox(
    "Facility",
    facilities
)


months = sorted(
    results["Period_Date"]
    .dt.strftime("%Y-%m")
    .unique()
)


selected_month = st.sidebar.selectbox(
    "Month",
    ["All Months"] + months
)


# =========================================================
# APPLY FILTERS
# =========================================================

filtered = results.copy()


if selected_facility != "All Facilities":

    filtered = filtered[
        filtered["Facility_ID"].astype(str)
        == selected_facility
    ]


if selected_month != "All Months":

    filtered = filtered[
        filtered["Period_Date"].dt.strftime("%Y-%m")
        == selected_month
    ]


# =========================================================
# SAFETY KPIs
# =========================================================

st.markdown(
    '<div class="section-title">'
    '🛡️ Safety Overview'
    '</div>',
    unsafe_allow_html=True
)


total_recordables = int(
    filtered["Total_Recordables"].sum()
)

total_ltis = int(
    filtered["Total_LTIs"].sum()
)

total_dart = int(
    filtered["Total_DART_Cases"].sum()
)

total_near_misses = int(
    filtered["Near_Miss_Count"].sum()
)

total_man_hours = filtered[
    "Man_Hours"
].sum()


if total_man_hours > 0:

    overall_trir = (
        total_recordables * 200_000
    ) / total_man_hours

    overall_ltifr = (
        total_ltis * 1_000_000
    ) / total_man_hours

    overall_dart = (
        total_dart * 200_000
    ) / total_man_hours

else:

    overall_trir = 0
    overall_ltifr = 0
    overall_dart = 0


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "TRIR",
        f"{overall_trir:.2f}"
    )


with col2:

    st.metric(
        "LTIFR",
        f"{overall_ltifr:.2f}"
    )


with col3:

    st.metric(
        "DART Rate",
        f"{overall_dart:.2f}"
    )


with col4:

    st.metric(
        "Near Misses",
        total_near_misses
    )


# =========================================================
# SECOND KPI ROW
# =========================================================

col5, col6, col7, col8 = st.columns(4)


with col5:

    st.metric(
        "Recordable Cases",
        total_recordables
    )


with col6:

    st.metric(
        "LTI Cases",
        total_ltis
    )


with col7:

    st.metric(
        "Days Lost",
        int(
            filtered["Total_Days_Lost"].sum()
        )
    )


with col8:

    st.metric(
        "Days Charged",
        int(
            filtered["Total_Days_Charged"].sum()
        )
    )


# =========================================================
# SAFETY TREND
# =========================================================

st.markdown(
    '<div class="section-title">'
    '📈 Safety Performance Trends'
    '</div>',
    unsafe_allow_html=True
)


trend_data = (
    filtered
    .groupby("Period_Date", as_index=False)
    .agg(
        TRIR=("TRIR", "mean"),
        LTIFR=("LTIFR", "mean"),
        DART_Rate=("DART_Rate", "mean")
    )
)


fig_safety = px.line(
    trend_data,
    x="Period_Date",
    y=[
        "TRIR",
        "LTIFR",
        "DART_Rate"
    ],
    markers=True,
    title="Safety KPI Trends"
)


fig_safety.update_layout(
    xaxis_title="Month",
    yaxis_title="Rate",
    legend_title="KPI"
)


st.plotly_chart(
    fig_safety,
    use_container_width=True
)


# =========================================================
# ENVIRONMENT
# =========================================================

st.markdown(
    '<div class="section-title">'
    '🌱 Environmental Performance'
    '</div>',
    unsafe_allow_html=True
)


total_ghg = filtered[
    "Total_GHG_CO2e"
].sum()

production = filtered[
    "Production_Tons"
].sum()

water = filtered[
    "Water_m3"
].sum()

waste = filtered[
    "Total_Waste_MT"
].sum()

recycled = filtered[
    "Recycled_Waste_MT"
].sum()


if production > 0:

    ghg_intensity = (
        total_ghg / production
    )

    water_intensity = (
        water / production
    )

else:

    ghg_intensity = 0
    water_intensity = 0


if waste > 0:

    waste_diversion = (
        recycled / waste
    ) * 100

else:

    waste_diversion = 0


env1, env2, env3, env4 = st.columns(4)


with env1:

    st.metric(
        "GHG Emissions",
        f"{total_ghg:,.1f} MT CO₂e"
    )


with env2:

    st.metric(
        "GHG Intensity",
        f"{ghg_intensity:.3f} MT/ton"
    )


with env3:

    st.metric(
        "Water Intensity",
        f"{water_intensity:.3f} m³/ton"
    )


with env4:

    st.metric(
        "Waste Diversion",
        f"{waste_diversion:.1f}%"
    )


# =========================================================
# ENVIRONMENTAL CHARTS
# =========================================================

env_data = (
    filtered
    .groupby("Period_Date", as_index=False)
    .agg(
        GHG_Intensity=(
            "GHG_Intensity_MT_per_Ton",
            "mean"
        ),

        Water_Intensity=(
            "Water_Intensity_m3_per_Ton",
            "mean"
        ),

        Waste_Diversion=(
            "Waste_Diversion_Rate_Pct",
            "mean"
        )
    )
)


left, right = st.columns(2)


with left:

    fig_ghg = px.line(
        env_data,
        x="Period_Date",
        y="GHG_Intensity",
        markers=True,
        title="GHG Intensity Trend"
    )

    st.plotly_chart(
        fig_ghg,
        use_container_width=True
    )


with right:

    fig_waste = px.line(
        env_data,
        x="Period_Date",
        y="Waste_Diversion",
        markers=True,
        title="Waste Diversion Trend"
    )

    st.plotly_chart(
        fig_waste,
        use_container_width=True
    )


# =========================================================
# FACILITY COMPARISON
# =========================================================

st.markdown(
    '<div class="section-title">'
    '🏭 Facility Performance'
    '</div>',
    unsafe_allow_html=True
)


facility_data = (
    results
    .groupby("Facility_ID", as_index=False)
    .agg(
        TRIR=("TRIR", "mean"),
        LTIFR=("LTIFR", "mean"),
        Near_Misses=("Near_Miss_Count", "sum"),
        Recordables=("Total_Recordables", "sum"),
        LTIs=("Total_LTIs", "sum")
    )
)


fig_facility = px.bar(
    facility_data,
    x="Facility_ID",
    y="TRIR",
    title="TRIR by Facility",
    text_auto=".2f"
)


st.plotly_chart(
    fig_facility,
    use_container_width=True
)


# =========================================================
# INCIDENT SUMMARY
# =========================================================

st.markdown(
    '<div class="section-title">'
    '⚠️ Incident Summary'
    '</div>',
    unsafe_allow_html=True
)


incident_summary = (
    incidents
    .groupby("Event_Classification")
    .size()
    .reset_index(
        name="Count"
    )
)


fig_incidents = px.bar(
    incident_summary,
    x="Event_Classification",
    y="Count",
    title="Incidents by Classification",
    text_auto=True
)


st.plotly_chart(
    fig_incidents,
    use_container_width=True
)


# =========================================================
# RAW DATA
# =========================================================

with st.expander(
    "📋 View Detailed KPI Data"
):

    display_data = filtered.copy()

    display_data["Period_Date"] = (
        display_data["Period_Date"]
        .dt.strftime("%Y-%m")
    )

    st.dataframe(
        display_data,
        use_container_width=True
    )


# =========================================================
# DOWNLOAD RESULTS
# =========================================================

st.markdown(
    '<div class="section-title">'
    '📥 Export Results'
    '</div>',
    unsafe_allow_html=True
)


csv_data = filtered.to_csv(
    index=False
).encode("utf-8")


st.download_button(
    label="Download KPI Results (CSV)",
    data=csv_data,
    file_name="SHE_KPI_Results.csv",
    mime="text/csv"
)


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "SHE Performance Dashboard | "
    "Python • Pandas • Plotly • Streamlit"
)