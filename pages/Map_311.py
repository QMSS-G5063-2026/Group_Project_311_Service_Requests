import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from data_loader import load_data

st.set_page_config(layout="wide", page_title="NYC 311 Geospatial Lead")

# Loading the Shared Data
df = load_data()

# Sidebar Filters (Maintains sync with teammates)
st.sidebar.header("📍 Map Controls")
hoods = ["All"] + sorted(df['Neighborhood'].unique().tolist())
selected_hood = st.sidebar.selectbox("Search Neighborhood", hoods)

complaints = ["All"] + sorted(df['Complaint'].unique().tolist())
selected_complaint = st.sidebar.selectbox("Complaint Type", complaints)

# Updates session state for teammates
st.session_state['global_hood'] = selected_hood
st.session_state['global_complaint'] = selected_complaint

# Filtering the data
map_df = df.copy()
if selected_hood != "All":
    map_df = map_df[map_df['Neighborhood'] == selected_hood]
if selected_complaint != "All":
    map_df = map_df[map_df['Complaint'] == selected_complaint]

# Professional Map Logic
st.title(f"311 Service Requests: {selected_hood if selected_hood != 'All' else 'Citywide'}")

# Limiting data for Folium to keep it smooth (Folium handles ~10k-20k points best)
# Taking the most recent requests if the list is too long
if len(map_df) > 10000:
    display_df = map_df.head(10000)
    st.warning("⚠️ Showing the 10,000 most recent records for performance.")
else:
    display_df = map_df

if not display_df.empty:
    avg_lat = display_df['Latitude'].mean()
    avg_lon = display_df['Longitude'].mean()
    
    # Creating the Flat Map (Professional Light Style)
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=13, tiles="CartoDB positron")

    # Adding the "Professional Cluster" layer
    marker_cluster = MarkerCluster(name="311 Complaints").add_to(m)

    # Adding points to cluster
    for idx, row in display_df.iterrows():
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=5,
            popup=f"<b>Type:</b> {row['Complaint']}<br><b>Detail:</b> {row['Complaint Detail']}",
            color="#6a0dad", # Professional Purple
            fill=True,
            fill_color="#6a0dad"
        ).add_to(marker_cluster)

    # Rendering
    st_folium(m, width=1400, height=700, use_container_width=True)
else:
    st.error("No data found for this selection.")

st.info(f"Total records in this view: {len(display_df):,}")