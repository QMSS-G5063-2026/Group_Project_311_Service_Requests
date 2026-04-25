import streamlit as st
import pandas as pd
import altair as alt
from data_loader import load_data

st.set_page_config(page_title="NYC 311 Over Time", layout="wide")

st.title("📈 NYC 311 Complaints Over Time (Manhattan 2025)")

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
df = load_data()
# ─────────────────────────────────────────────
# CLEAN ZIP CODES
# ─────────────────────────────────────────────

df["Incident Zip"] = df["Incident Zip"].astype(str)

# remove bad ZIPs
df = df[
    (df["Incident Zip"].str.len() == 5) &
    (df["Incident Zip"] != "00000")
]

# optional: ensure numeric-like format only
df = df[df["Incident Zip"].str.isnumeric()]

# ─────────────────────────────────────────────
# SAFETY: ENSURE DATETIME
# ─────────────────────────────────────────────
df["Created Date"] = pd.to_datetime(df["Created Date"], errors="coerce")
df = df.dropna(subset=["Created Date"])

df["Month"] = df["Created Date"].dt.to_period("M")

# ─────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────
st.sidebar.header("Filters")

# ── Complaint Group Mode ──
categories = sorted(df["Complaint_Group"].dropna().unique())

view_mode = st.sidebar.radio(
    "Complaint View Mode",
    ["All", "Single Group", "Compare Groups"],
    key="view_mode"
)

if view_mode == "All":
    plot_df = df.copy()

elif view_mode == "Single Group":
    selected_group = st.sidebar.selectbox(
        "Select Complaint Group",
        categories,
        key="complaint_group_single"
    )
    plot_df = df[df["Complaint_Group"] == selected_group]

else:
    selected_groups = st.sidebar.multiselect(
        "Select Complaint Groups",
        categories,
        default=categories[:3],
        key="complaint_group_multi"
    )
    plot_df = df[df["Complaint_Group"].isin(selected_groups)]

# ─────────────────────────────────────────────
# LOCATION FILTERS (LINKED)
# ─────────────────────────────────────────────
st.sidebar.subheader("Location Filters")

neighborhoods = sorted(df["Neighborhood"].dropna().unique())

selected_neighborhood = st.sidebar.selectbox(
    "Neighborhood",
    ["All"] + neighborhoods,
    key="neighborhood_filter"
)

# ZIP options depend on neighborhood
if selected_neighborhood == "All":
    zip_options = sorted(df["Incident Zip"].dropna().unique())
else:
    zip_options = sorted(
        df[df["Neighborhood"] == selected_neighborhood]["Incident Zip"].dropna().unique()
    )

selected_zip = st.sidebar.selectbox(
    "Incident Zip",
    ["All"] + zip_options,
    key="zip_filter"
)

# ─────────────────────────────────────────────
# APPLY LOCATION FILTERS
# ─────────────────────────────────────────────
if selected_neighborhood != "All":
    plot_df = plot_df[plot_df["Neighborhood"] == selected_neighborhood]

if selected_zip != "All":
    plot_df = plot_df[plot_df["Incident Zip"] == selected_zip]

# ─────────────────────────────────────────────
# DEBUG (optional)
# ─────────────────────────────────────────────
st.write("📊 Filtered Shape:", plot_df.shape)

# ─────────────────────────────────────────────
# TIME AGGREGATION
# ─────────────────────────────────────────────
time_df = (
    plot_df.groupby(["Month", "Complaint_Group"])
    .size()
    .reset_index(name="Count")
)

time_df["Date"] = time_df["Month"].dt.to_timestamp()
time_df = time_df.sort_values("Date")

# ─────────────────────────────────────────────
# TITLE
# ─────────────────────────────────────────────
st.subheader("📊 Monthly Complaint Trends")

# ─────────────────────────────────────────────
# ALTair CHART (INTERACTIVE + TOOLTIPS)
# ─────────────────────────────────────────────
if len(time_df) > 0:

    chart = (
        alt.Chart(time_df)
        .mark_line(point=True)
        .encode(
            x=alt.X("Date:T", title="Month"),
            y=alt.Y("Count:Q", title="Complaints"),
            color=alt.Color("Complaint_Group:N", title="Complaint Group"),
            tooltip=[
                alt.Tooltip("Date:T", title="Month"),
                alt.Tooltip("Complaint_Group:N", title="Group"),
                alt.Tooltip("Count:Q", title="Count")
            ]
        )
        .properties(height=500)
        .interactive()
    )

    st.altair_chart(chart, use_container_width=True)

else:
    st.warning("No data available for this selection.")

# ─────────────────────────────────────────────
# METRICS
# ─────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

col1.metric("Total Complaints", len(plot_df))

if len(time_df) > 0:
    col2.metric("Avg Monthly", round(time_df["Count"].mean(), 1))

    peak_row = time_df.loc[time_df["Count"].idxmax()]
    col3.metric("Peak Month", peak_row["Date"].strftime("%Y-%m"))
else:
    col2.metric("Avg Monthly", "0")
    col3.metric("Peak Month", "No data")