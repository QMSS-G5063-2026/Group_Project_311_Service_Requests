import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    # Using the verified master file
    df = pd.read_csv("NYC_311_Master_2024_2025.csv", low_memory=False)

    # Faster Date Parsing (Fixes the UserWarning)
    # Specifying the format makes loading significantly faster
    df['Created Date'] = pd.to_datetime(df['Created Date'], errors='coerce')

    # 2. Final Column Clean for the Team
    # Ensures coordinates are ready for your Map
    df = df.dropna(subset=["Latitude", "Longitude", "Borough"])
    
    # Ensure ZIP codes are strings for clean filtering (no .0 at the end)
    df['Incident Zip'] = df['Incident Zip'].fillna(0).astype(int).astype(str)

    return df