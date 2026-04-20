import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    # Loading the 2025 Filtered Master File
    df = pd.read_csv("NYC_311_2025_Filtered.csv", low_memory=False)
    
    # Fixing the "6 Boroughs" Issue (Filter for real NYC Boroughs only)
    valid_boroughs = ["BRONX", "BROOKLYN", "MANHATTAN", "QUEENS", "STATEN ISLAND"]
    df = df[df['Borough'].isin(valid_boroughs)]
    
    # Numeric Coordinate Enforcement (Fixing blank maps)
    df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
    df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
    df = df.dropna(subset=["Latitude", "Longitude"])
    
    # Cleaning ZIP Codes (Strings without decimals)
    df['Incident Zip'] = df['Incident Zip'].fillna(0).astype(int).astype(str)
    
    # Cleaning Neighborhoods (Ensures drop-down is clean)
    df = df.dropna(subset=["Neighborhood"])
    
    return df