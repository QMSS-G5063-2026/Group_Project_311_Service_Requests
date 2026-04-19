import streamlit as st
from data_loader import load_data


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
This project analyzes NYC 311 complaints to uncover:
- Spatial patterns across boroughs
- Trends over time
- Most common complaint types
- Neighborhood-level differences
""")

st.divider()

# ─────────────────────────────────────────────
# NAVIGATION (SAFE VERSION)
# ─────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🗺️ Map Analysis")
    st.markdown("Visualize where complaints occur across NYC.")
    if st.button("Open Map"):
        st.switch_page("map_311.py")

with col2:
    st.markdown("### 📈 Time Trends")
    st.markdown("Track how complaints change over time.")
    if st.button("Open Trends"):
        st.switch_page("trends_311.py")

with col3:
    st.markdown("### ☁️ Word Insights")
    st.markdown("Explore complaint text patterns by borough.")
    if st.button("Open Word Cloud"):
        st.switch_page("wordcloud_311.py")

st.divider()

# ─────────────────────────────────────────────
# FOOTER METRICS PLACEHOLDER (OPTIONAL)
# ─────────────────────────────────────────────
st.caption("NYC 311 Data Explorer | Streamlit Dashboard Project 2026")
