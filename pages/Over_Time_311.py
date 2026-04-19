import streamlit as st
import pandas as pd

st.set_page_config(page_title="NYC 311 Over Time", layout="wide")

st.title("📈 NYC 311 Complaints Over Time")

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
df = pd.read_csv("NYC_311_Master_2024_2025.csv")

# Ensure correct types
df["Complaint Year"] = pd.to_numeric(df["Complaint Year"], errors="coerce")
df["Complaint Month"] = pd.to_numeric(df["Complaint Month"], errors="coerce")

# ─────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────
st.sidebar.header("Filters")

boroughs = sorted(df["Borough"].dropna().unique())
categories = sorted(df["Main Complaint Category"].dropna().unique())

selected_borough = st.sidebar.selectbox("Select Borough", boroughs)
selected_category = st.sidebar.selectbox("Select Complaint Category", categories)

# ─────────────────────────────────────────────
# FILTER DATA
# ─────────────────────────────────────────────
filtered = df[
    (df["Borough"] == selected_borough) &
    (df["Main Complaint Category"] == selected_category)
]

# ─────────────────────────────────────────────
# BUILD TIME SERIES
# ─────────────────────────────────────────────
time_df = (
    filtered.groupby(["Complaint Year", "Complaint Month"])
    .size()
    .reset_index(name="Count")
)

# Create datetime column
time_df["Date"] = pd.to_datetime(
    time_df["Complaint Year"].astype(int).astype(str)
    + "-" +
    time_df["Complaint Month"].astype(int).astype(str)
)

time_df = time_df.sort_values("Date")

# ─────────────────────────────────────────────
# METRICS
# ─────────────────────────────────────────────
if len(time_df) > 0 and time_df["Count"].notna().any():

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Complaints", len(filtered))
    col2.metric("Avg Monthly Complaints", round(time_df["Count"].mean(), 1))

    peak_row = time_df.loc[time_df["Count"].idxmax()]

    col3.metric(
        "Peak Month",
        peak_row["Date"].strftime("%Y-%m")
    )

else:
    col1, col2, col3 = st.columns(3)

    col1.metric("Total Complaints", len(filtered))
    col2.metric("Avg Monthly Complaints", "0")
    col3.metric("Peak Month", "No data")