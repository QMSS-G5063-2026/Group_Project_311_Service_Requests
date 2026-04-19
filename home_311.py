import streamlit as st
from data_loader import load_data
import os
import pandas as pd

st.set_page_config(
    page_title="NYC 311 Explorer",
    page_icon="🏙️",
    layout="wide"
)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div style="
    background: linear-gradient(90deg, #1f77b4, #4aa3df);
    padding: 25px;
    border-radius: 10px;
    color: white;
">
    <h1 style="margin-bottom: 10px;">
        NYC 311 Neighborhood Issues Explorer
    </h1>
    <p style="font-size:18px;">
        Explore New York City using 311 complaint data by borough, neighborhood, audience group, or complaint type.
    </p>
    <p style="font-size:16px;">
        Designed to help residents, researchers, and decision-makers understand quality-of-life issues through maps, trends, comparisons, and future analytics.
    </p>
    <p style="font-size:14px; opacity:0.85;">
        Created by  Kenneth Shelton, Maryla Wozniak, and Yawar Sheikh
    </p>
</div>
""", unsafe_allow_html=True)
st.divider()

# ─────────────────────────────────────────────
# INTRO SECTION
# ─────────────────────────────────────────────
st.subheader("📊 Explore the Dashboard")

st.markdown("""
Use the sidebar (←) to navigate between:
- 🗺️ Map Analysis
- 📈 Trends Over Time
- ☁️ Word Cloud
""")

st.divider()

# ─────────────────────────────────────────────
# data tabular
# ─────────────────────────────────────────────

# ─────────────────────────────────────────────
# LOAD DATA (same file used everywhere)
# ─────────────────────────────────────────────
df = pd.read_csv("NYC_311_Master_2024_2025.csv")

# ─────────────────────────────────────────────
# DATA TABULAR PREVIEW
# ─────────────────────────────────────────────
st.subheader("📊 Data Preview")

st.write("First 10 rows of NYC 311 dataset:")

st.dataframe(df.head(10), use_container_width=True)

# ─────────────────────────────────────────────
# DATA INFO METRICS
# ─────────────────────────────────────────────
st.subheader("📌 Dataset Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Rows", f"{len(df):,}")
col2.metric("Columns", df.shape[1])
col3.metric("Boroughs", df["Borough"].nunique())
col4.metric("Complaint Types", df["Main Complaint Category"].nunique())

# ─────────────────────────────────────────────
# OPTIONAL: COLUMN LIST
# ─────────────────────────────────────────────
with st.expander("📋 View Column Names"):
    st.write(list(df.columns))

st.write("CURRENT DIR:", os.getcwd())
st.write("PAGES CONTENT:", os.listdir("pages"))




# ─────────────────────────────────────────────
# FOOTER METRICS PLACEHOLDER (OPTIONAL)
# ─────────────────────────────────────────────
st.caption("NYC 311 Data Explorer | Streamlit Dashboard Project 2026")


