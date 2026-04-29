import streamlit as st
import pandas as pd
import pydeck as pdk
from data_loader import load_data

st.set_page_config(layout="wide", page_title="NYC 311 | Manhattan Map Analysis")

# Loading the data
df = load_data()

# Sidebar - Hierarchical Filtering
st.sidebar.header("Filter Manhattan Data")

# Neighborhood Filter
hoods = ["All Manhattan"] + sorted(df['Neighborhood'].unique().astype(str))
selected_hood = st.sidebar.selectbox("Neighborhood", hoods)

# Cascading ZIP Filter logic
if selected_hood != "All Manhattan":
    relevant_zips = df[df['Neighborhood'] == selected_hood]['Incident Zip'].unique()
else:
    relevant_zips = df['Incident Zip'].unique()

# Clean ZIPs: Numeric only, 5-digits
zips = ["All Zips"] + sorted([str(z) for z in relevant_zips if str(z).isdigit() and len(str(z)) == 5])
selected_zip = st.sidebar.selectbox("Incident Zip", zips)

# Category and Issue Filters
groups = ["All Categories"] + sorted(df['Complaint_Group'].unique().astype(str))
selected_group = st.sidebar.selectbox("Complaint Category", groups)

if selected_group != "All Categories":
    relevant_issues = df[df['Complaint_Group'] == selected_group]['Complaint'].unique()
    issues = ["All in Category"] + sorted(relevant_issues.astype(str))
    selected_issue = st.sidebar.selectbox("Specific Issue", issues)
else:
    selected_issue = "All in Category"

# Applying the Filtering Logic
map_df = df.copy()

if selected_hood != "All Manhattan":
    map_df = map_df[map_df['Neighborhood'] == selected_hood]

if selected_zip != "All Zips":
    map_df = map_df[map_df['Incident Zip'] == selected_zip]

if selected_group != "All Categories":
    map_df = map_df[map_df['Complaint_Group'] == selected_group]

if selected_issue != "All in Category":
    map_df = map_df[map_df['Complaint'] == selected_issue]

# Standardized Metrics Row
st.title("NYC 311 Geospatial Analysis")

if not map_df.empty:
    col1, col2, col3 = st.columns(3)
    top_neighborhood = map_df['Neighborhood'].value_counts().idxmax()
    total_issues = len(map_df)
    top_complaint = map_df['Complaint'].value_counts().idxmax()

    with col1:
        st.metric("Hotspot Neighborhood", top_neighborhood)
    with col2:
        st.metric("Total Reports", f"{total_issues:,}")
    with col3:
        st.metric("Top Issue", top_complaint)

st.markdown(f"Displaying **{len(map_df):,}** reports in Manhattan.")

# Map Logic
if selected_hood == "All Manhattan" and selected_issue == "All in Category":
    # Heatmap Layer
    layer = pdk.Layer(
        "HeatmapLayer",
        data=map_df,
        get_position='[Longitude, Latitude]',
        threshold=0.2,      
        radius_pixels=30,   
        intensity=1,
        color_range=[
            [0, 0, 255, 25], [0, 255, 255, 80], [0, 255, 0, 120],
            [255, 255, 0, 180], [255, 128, 0, 220], [255, 0, 0, 255]
        ]
    )
    zoom_level = 11.2
else:
    # Making a scatterplot Layer with sharp points
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position='[Longitude, Latitude]',
        get_color='[106, 13, 173, 180]', 
        radius_min_pixels=3,   
        radius_max_pixels=10,  
        pickable=True,
    )
    zoom_level = 13.0

view_state = pdk.ViewState(
    latitude=40.7831, longitude=-73.9712, zoom=zoom_level, pitch=0
)

# Rendering the Map UI
with st.expander("ℹ️ How to read this map"):
    st.write("""
    * **Heatmap View:** Brighter **red** areas indicate high report density.
    * **Neighborhood View:** Purple dots show exact locations.
    * **Interaction:** Hover over dots for complaint details.
    """)

st.pydeck_chart(pdk.Deck(
    map_style='https://basemaps.cartocdn.com/gl/positron-gl-style/style.json',
    initial_view_state=view_state,
    layers=[layer],
    tooltip={"text": "{Complaint}\n{Neighborhood}"},
    height=700 
), use_container_width=True)