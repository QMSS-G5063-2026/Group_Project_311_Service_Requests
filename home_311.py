import streamlit as st
import pandas as pd

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

df = pd.read_csv("NYC_311_Master_2024_2025.csv")

st.write(df)

col1, col2 = st.columns(2)

col1.metric("Rows", df.shape[0])
col2.metric("Columns", df.shape[1])
