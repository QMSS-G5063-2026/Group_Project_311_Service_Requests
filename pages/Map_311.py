import streamlit as st
import pandas as pd
import pydeck as pdk
from data_loader import load_data

st.set_page_config(layout="wide", page_title="NYC 311 Geospatial Lead")

# Accessing the Shared Data
df = load_data()

# Sidebar Filters 
st.sidebar.header("📍 Map Controls")

# Neighborhood Filter 
neighborhoods = ["All"] + sorted(df['Neighborhood'].dropna().unique().tolist())
selected_hood = st.sidebar.selectbox("Search Neighborhood", neighborhoods)

# ZIP Code Filter
zips = ["All"] + sorted(df['Incident Zip'].unique().tolist())
selected_zip = st.sidebar.selectbox("Search ZIP Code", zips)

# Complaint Category Filter
categories = ["All"] + sorted(df['Complaint'].unique().tolist())
selected_complaint = st.sidebar.selectbox("Complaint Type", categories)

# Global State Logic (for my teammates)
# This makes sure that when they click "Word Cloud," it's already filtered.
st.session_state['global_zip'] = selected_zip
st.session_state['global_hood'] = selected_hood
st.session_state['global_complaint'] = selected_complaint

# Filtering the data for Mapping
map_df = df.copy()
if selected_hood != "All":
    map_df = map_df[map_df['Neighborhood'] == selected_hood]
if selected_zip != "All":
    map_df = map_df[map_df['Incident Zip'] == selected_zip]
if selected_complaint != "All":
    map_df = map_df[map_df['Complaint'] == selected_complaint]

# Building the 3D Hexagon Map
st.title(f"311 Clusters: {selected_hood if selected_hood != 'All' else 'NYC Citywide'}")

# Setting the initial view based on the selection
if selected_hood != "All" and not map_df.empty:
    init_lat = map_df['Latitude'].mean()
    init_lon = map_df['Longitude'].mean()
    init_zoom = 13
else:
    init_lat, init_lon, init_zoom = 40.7128, -74.0060, 10

view_state = pdk.ViewState(
    latitude=init_lat,
    longitude=init_lon,
    zoom=init_zoom,
    pitch=45,
    bearing=0
)

# Layer definition: This clusters points automatically
hexagon_layer = pdk.Layer(
    "HexagonLayer",
    data=map_df,
    get_position='[Longitude, Latitude]',
    radius=150,          # Cluster radius in meters
    elevation_scale=50,  # Height factor
    elevation_range=[0, 2000],
    pickable=True,
    extruded=True,       # 3D
    color_range=[[255,255,178], [254,217,118], [254,178,76], [253,141,60], [240,59,32], [189,0,38]]
)

st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/dark-v9',
    initial_view_state=view_state,
    layers=[hexagon_layer],
    tooltip={"text": "Density Count: {elevationValue}"}
))

# Including a status update
st.info(f"Showing {len(map_df):,} filtered incidents. Your teammates' pages are now synced to this selection.")