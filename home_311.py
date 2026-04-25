import streamlit as st
from data_loader import load_data
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
    <h1>Inside Manhattan: 311 Complaints Uncovered (2025)</h1>
    <p>Explore complaint patterns by category, neighborhood, and time to better understand
        quality-of-life issues across Manhattan.</p>
    <p style="font-size:14px; opacity:0.85;">
        Created by Kenneth Shelton, Maryla Wozniak, and Yawar Sheikh
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
df = load_data()
df.columns = df.columns.str.strip()

# ─────────────────────────────────────────────
# CATEGORY CARDS (INTERACTIVE)
# ─────────────────────────────────────────────
st.subheader("🧩 Explore Complaint Categories")

group_counts = df["Complaint_Group"].value_counts()

cols = st.columns(3)

for i, (group, count) in enumerate(group_counts.items()):
    with cols[i % 3]:
        if st.button(f"{group}\n{count:,}", key=group):
            st.session_state["selected_group"] = group

# Get selection
selected_group = st.session_state.get("selected_group", None)

# ─────────────────────────────────────────────
# DRILL-DOWN VIEW
# ─────────────────────────────────────────────
if selected_group:

    st.markdown(f"## 🔎 {selected_group}")

    sub_df = df[df["Complaint_Group"] == selected_group]

    complaint_counts = (
        sub_df["Complaint"]
        .value_counts()
        .reset_index()
    )
    
    complaint_counts.columns = ["Complaint", "Count"]
    
    # Remove zero or invalid values (extra safety)
    complaint_counts = complaint_counts[
        (complaint_counts["Count"] > 0) &
        (complaint_counts["Complaint"].notna())
    ]

    st.markdown("### 📋 Complaint Types")
    st.dataframe(complaint_counts, use_container_width=True)

    # Metrics
    col1, col2 = st.columns(2)
    col1.metric("Total Complaints", len(sub_df))
    col2.metric("Unique Complaint Types", sub_df["Complaint"].nunique())

    # Reset button
    if st.button("🔄 Reset Selection"):
        st.session_state["selected_group"] = None

st.divider()

# ─────────────────────────────────────────────
# DATA PREVIEW
# ─────────────────────────────────────────────
st.subheader("📊 Data Preview")

st.dataframe(df.head(10), use_container_width=True)

# ─────────────────────────────────────────────
# COLUMN INFO
# ─────────────────────────────────────────────
with st.expander("📋 View Column Names"):
    st.write(list(df.columns))

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.caption("NYC 311 Data Explorer | Streamlit Dashboard Project 2026")
