import streamlit as st
from data_loader import load_data
import pandas as pd
import textwrap

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
# TITLE
# ─────────────────────────────────────────────
st.subheader("🧩 Explore Complaint Categories")
st.caption("👇 Click a category to see detailed complaint types and breakdowns.")

group_counts = df["Complaint_Group"].value_counts()

# ─────────────────────────────────────────────
# CSS (FIXED FOR WRAPPING)
# ─────────────────────────────────────────────
st.markdown("""
<style>

div[data-testid="column"] {
    display: flex;
}

div.stButton {
    width: 100%;
}

/* CARD BUTTON */
div.stButton > button {
    width: 100%;
    height: 80px;

    border-radius: 12px;
    border: 1px solid #e0e6ed;
    background-color: #f5f7fa;

    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;

    text-align: center;
    padding: 6px;

    font-size: 12px;
    font-weight: 600;
    line-height: 1.2;

    white-space: normal;
    word-break: break-word;

    overflow: visible;

    transition: all 0.2s ease-in-out;
}

/* hover */
div.stButton > button:hover {
    background: linear-gradient(180deg, #e8f1fb, #dbeafe);
    border: 1px solid #1f77b4;
    transform: translateY(-3px);
    color: #1f77b4;
}

/* focus */
div.stButton > button:focus {
    outline: none;
    border: 2px solid #1f77b4;
}

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# LABEL WRAPPER (NO TRUNCATION)
# ─────────────────────────────────────────────
def format_label(group, count, width=22):
    wrapped_group = "\n".join(textwrap.wrap(group, width=width))
    return f"{wrapped_group}\n{count:,}"

# ─────────────────────────────────────────────
# GRID
# ─────────────────────────────────────────────
cols = st.columns(3)

for i, (group, count) in enumerate(group_counts.items()):
    with cols[i % 3]:

        label = format_label(group, count)

        if st.button(label, key=f"group_{i}"):
            st.session_state["selected_group"] = group

# ─────────────────────────────────────────────
# SELECTION
# ─────────────────────────────────────────────
selected_group = st.session_state.get("selected_group", None)

if selected_group:

    st.markdown(f"## 🔎 {selected_group}")

    sub_df = df[df["Complaint_Group"] == selected_group]

    complaint_counts = (
        sub_df["Complaint"]
        .value_counts()
        .reset_index()
    )

    complaint_counts.columns = ["Complaint", "Count"]

    complaint_counts = complaint_counts[
        (complaint_counts["Count"] > 0) &
        (complaint_counts["Complaint"].notna())
    ]

    st.markdown("### 📋 Complaint Types")
    st.dataframe(complaint_counts, use_container_width=True)

    col1, col2 = st.columns(2)
    col1.metric("Total Complaints", len(sub_df))
    col2.metric("Unique Complaint Types", sub_df["Complaint"].nunique())

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
