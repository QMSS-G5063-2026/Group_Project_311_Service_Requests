import streamlit as st
import pandas as pd
import pydeck as pdk
from data_loader import load_data

st.set_page_config(layout="wide", page_title="NYC 311 Geospatial Analysis")

# Load Data
df = load_data()

# Sidebar Controls
st.sidebar.header("📍 Map Controls")

# Ensure categories are handled as strings for the dropdowns
hoods = ["All"] + sorted(df['Neighborhood'].unique().astype(str))
selected_hood = st.sidebar.selectbox("Search Neighborhood", hoods)

zips = ["All"] + sorted(df['Incident Zip'].unique().astype(str))
selected_zip = st.sidebar.selectbox("Search ZIP Code", zips)

complaints = ["All"] + sorted(df['Complaint'].unique().astype(str))
selected_complaint = st.sidebar.selectbox("Complaint Type", complaints)

# Sync State for Teammates
st.session_state['global_hood'] = selected_hood
st.session_state['global_zip'] = selected_zip
st.session_state['global_complaint'] = selected_complaint

# Filtering the Data
map_df = df.copy()
if selected_hood != "All":
    map_df = map_df[map_df['Neighborhood'] == selected_hood]
if selected_zip != "All":
    map_df = map_df[map_df['Incident Zip'] == selected_zip]
if selected_complaint != "All":
    map_df = map_df[map_df['Complaint'] == selected_complaint]

# Dynamic View Logic 
if not map_df.empty:
    center_lat = float(map_df['Latitude'].mean())
    center_lon = float(map_df['Longitude'].mean())
    zoom_level = 14 if selected_hood != "All" or selected_zip != "All" else 11
else:
    center_lat, center_lon, zoom_level = 40.7128, -74.0060, 10

view_state = pdk.ViewState(
    latitude=center_lat,
    longitude=center_lon,
    zoom=zoom_level,
    pitch=0
)

layer = pdk.Layer(
    "ScatterplotLayer",
    data=map_df.astype(object), 
    get_position='[Longitude, Latitude]',
    get_color='[147, 112, 219, 200]', 
    get_radius=40,                   
    pickable=True,
)

# Rendering
st.title(f"311 Spatial Analysis: {selected_hood if selected_hood != 'All' else 'Citywide'}")

st.pydeck_chart(pdk.Deck(
    map_style='https://basemaps.cartocdn.com/gl/positron-gl-style/style.json',
    initial_view_state=view_state,
    layers=[layer],
    tooltip={"text": "Complaint: {Complaint}\nDetail: {Complaint Detail}"}
))

st.info(f"Total points plotted: {len(map_df):,}")