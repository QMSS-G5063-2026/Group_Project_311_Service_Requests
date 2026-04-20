import streamlit as st
import pandas as pd
import pydeck as pdk
from data_loader import load_data

st.set_page_config(layout="wide", page_title="NYC 311 Geospatial Lead")

# Access Shared Data (Cached for speed)
df = load_data()

# Sidebar Filters
st.sidebar.header("📍 Map Controls")

# Neighborhood Filter
neighborhoods = ["All"] + sorted(df['Neighborhood'].unique().tolist())
selected_hood = st.sidebar.selectbox("Search Neighborhood", neighborhoods)

# ZIP Code Filter
zips = ["All"] + sorted(df['Incident Zip'].unique().tolist())
selected_zip = st.sidebar.selectbox("Search ZIP Code", zips)

# Complaint Category Filter
categories = ["All"] + sorted(df['Complaint'].unique().tolist())
selected_complaint = st.sidebar.selectbox("Complaint Type", categories)

# Global State Triggers (Syncs all the pages)
st.session_state['global_zip'] = selected_zip
st.session_state['global_hood'] = selected_hood
st.session_state['global_complaint'] = selected_complaint

# Filter Logic
map_df = df.copy()
if selected_hood != "All":
    map_df = map_df[map_df['Neighborhood'] == selected_hood]
if selected_zip != "All":
    map_df = map_df[map_df['Incident Zip'] == selected_zip]
if selected_complaint != "All":
    map_df = map_df[map_df['Complaint'] == selected_complaint]

# Dynamic Camera Centering
# Centering on the selected neighborhood or defaults to NYC
if not map_df.empty:
    center_lat = map_df['Latitude'].mean()
    center_lon = map_df['Longitude'].mean()
    zoom_level = 13.5 if selected_hood != "All" else 10
else:
    center_lat, center_lon, zoom_level = 40.7128, -74.0060, 10

view_state = pdk.ViewState(
    latitude=center_lat,
    longitude=center_lon,
    zoom=zoom_level,
    pitch=40,   # Slight angle for 3D effect without "sticks"
    bearing=0
)

# Map Layer Definition
hexagon_layer = pdk.Layer(
    "HexagonLayer",
    data=map_df,
    get_position='[Longitude, Latitude]',
    radius=70,           # Optimized radius for neighborhood detail
    elevation_scale=10,  # Balanced height for 2.8M rows
    elevation_range=[0, 1000],
    pickable=True,
    extruded=True,       
    color_range=[[255,255,178], [254,217,118], [254,178,76], [253,141,60], [240,59,32], [189,0,38]]
)

# Render
st.title(f"311 Clusters: {selected_hood if selected_hood != 'All' else 'NYC Citywide'}")

st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/dark-v9',
    initial_view_state=view_state,
    layers=[hexagon_layer],
    tooltip={"text": "Complaints in Cluster: {elevationValue}"}
))

# Status Message
st.info(f"Showing {len(map_df):,} incidents. Your teammates' pages are now synced to this selection.")