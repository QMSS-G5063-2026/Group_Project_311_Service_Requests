# -*- coding: utf-8 -*-
"""
Created on Sun Apr 19 11:49:18 2026

@author: ys3435 

- Word Cloud page for NYC 311 Dashboard
- Word cloud reshapes into the selected borough's silhouette.
- Filters mirror Map_311.py and Over_Time_311.py exactly.
"""
#


import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFilter
from wordcloud import WordCloud
from data_loader import load_data
 
st.set_page_config(page_title="NYC 311 Word Cloud", layout="wide")
 
# ─────────────────────────────────────────────
# BOROUGH SILHOUETTE MASKS
# Each mask: black (0) = fill area, white (255) = background
# ─────────────────────────────────────────────
def _make_mask(polys, W=800, H=500):
    img = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(img)
    for poly in polys:
        draw.polygon(poly, fill="black")
    img = img.filter(ImageFilter.GaussianBlur(radius=3))
    arr = np.array(img)
    return np.where(arr < 200, 0, 255).astype(np.uint8)
 
@st.cache_resource
def build_masks():
    manhattan = [
        (80,380),(100,330),(125,278),(155,228),(190,182),(228,140),
        (268,104),(308,74),(348,50),(386,34),(420,26),(450,26),
        (476,34),(498,50),(514,72),(524,98),(528,126),(526,156),
        (518,186),(504,214),(486,240),(464,262),(440,282),(414,298),
        (386,310),(356,320),(326,326),(296,328),(268,326),(242,320),
        (218,310),(198,296),(180,278),(166,256),(155,232),(148,205),
        (144,178),(143,150),(145,122),(150,96),(158,72),(168,52),
        (180,36),(194,24),(210,16),(228,12),(247,12),(80,380),
    ]
    brooklyn = [
        (60,70),(170,48),(285,42),(390,48),(480,62),(548,82),
        (598,108),(628,138),(640,172),(632,206),(612,236),(582,260),
        (544,278),(502,290),(458,298),(413,302),(368,303),(323,300),
        (280,293),(240,283),(204,270),(173,254),(148,236),(130,216),
        (118,196),(112,175),(112,154),(118,134),(129,115),(145,98),
        (163,84),(180,74),(140,72),(100,70),(60,70),
    ]
    queens = [
        (50,195),(68,155),(94,115),(128,80),(170,50),(216,28),
        (266,12),(320,4),(376,2),(432,6),(486,18),(534,36),
        (575,60),(606,88),(628,120),(638,154),(638,188),(628,220),
        (608,248),(580,272),(546,290),(507,302),(465,308),(422,308),
        (379,304),(337,296),(297,284),(260,270),(227,253),(198,234),
        (175,214),(157,194),(144,175),(137,158),(92,172),(50,195),
    ]
    bronx = [
        (120,360),(132,320),(150,278),(176,240),(208,206),(246,176),
        (288,150),(332,128),(378,112),(426,100),(474,94),(520,92),
        (562,96),(598,106),(626,120),(646,140),(654,162),(652,184),
        (640,204),(620,220),(594,232),(562,240),(528,244),(493,244),
        (458,242),(424,238),(391,232),(360,228),(332,226),(307,228),
        (285,234),(266,244),(250,258),(238,276),(229,298),(224,322),
        (222,348),(222,364),(170,366),(120,360),
    ]
    staten = [
        (240,72),(282,50),(326,36),(374,28),(422,28),(468,36),
        (508,52),(540,74),(564,102),(576,132),(578,163),(570,194),
        (552,222),(526,246),(494,264),(458,276),(420,282),(381,282),
        (342,276),(306,264),(274,247),(248,226),(228,202),(216,176),
        (212,149),(216,122),(228,98),(248,78),(240,72),
    ]
    # "All" uses a wide rectangle — no shape restriction
    all_nyc = [(20, 20), (780, 20), (780, 480), (20, 480)]
 
    return {
        "All Manhattan":  _make_mask([all_nyc]),
        "Manhattan":      _make_mask([manhattan]),
        "Brooklyn":       _make_mask([brooklyn]),
        "Queens":         _make_mask([queens]),
        "Bronx":          _make_mask([bronx]),
        "Staten Island":  _make_mask([staten]),
    }
 
####### ####### ####### ####### ####### ####### ####### 
####### DATA

@st.cache_data(show_spinner="Loading 311 data...")
def get_data():
    df = load_data()
    df["Incident Zip"] = df["Incident Zip"].astype(str)
    df = df[
        (df["Incident Zip"].str.len() == 5) &
        (df["Incident Zip"] != "00000") &
        (df["Incident Zip"].str.isnumeric())
    ]
    df["Created Date"] = pd.to_datetime(df["Created Date"], errors="coerce")
    df = df.dropna(subset=["Created Date"])
    return df
 
df       = get_data()
masks    = build_masks()
 



####### ####### ####### ####### ####### ####### ####### 
####### SIDEBAR FILTERS  (mirrors Map_311.py exactly)

st.sidebar.header("Filter Manhattan Data")
 
hoods = ["All Manhattan"] + sorted(df["Neighborhood"].dropna().unique().astype(str))
selected_hood = st.sidebar.selectbox("Neighborhood", hoods)
 
groups = ["All Categories"] + sorted(df["Complaint_Group"].dropna().unique().astype(str))
selected_group = st.sidebar.selectbox("Complaint Category", groups)
 
if selected_group != "All Categories":
    relevant = df[df["Complaint_Group"] == selected_group]["Complaint"].dropna().unique()
    issues   = ["All in Category"] + sorted(relevant.astype(str))
    selected_issue = st.sidebar.selectbox("Specific Issue", issues)
else:
    selected_issue = "All in Category"
 
# Borough selector — drives the silhouette shape
st.sidebar.divider()
borough_options = ["All Manhattan", "Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"]
selected_borough = st.sidebar.selectbox("Borough shape", borough_options)







####### ####### ####### ####### ####### ####### ####### 
####### APPLY FILTERS

filtered = df.copy()
 
if selected_hood != "All Manhattan":
    filtered = filtered[filtered["Neighborhood"] == selected_hood]
if selected_group != "All Categories":
    filtered = filtered[filtered["Complaint_Group"] == selected_group]
if selected_issue != "All in Category":
    filtered = filtered[filtered["Complaint"] == selected_issue]
 






####### ####### ####### ####### ####### ####### ####### 
####### PAGE

st.title("☁️ NYC 311 Complaint Word Cloud")
st.markdown(f"Displaying **{len(filtered):,}** reports — shaped as **{selected_borough}**")
 
if filtered.empty:
    st.warning("No complaints match the current filters. Try broadening your selection.")
else:
    freq = filtered["Complaint"].value_counts().to_dict()
    mask = masks[selected_borough]
 
    wc = WordCloud(
        mask=mask,
        background_color="white",
        colormap="RdYlBu",
        max_words=100,
        prefer_horizontal=0.78,
        contour_width=3,
        contour_color="#1a1a2e",
        min_font_size=9,
        max_font_size=110,
        collocations=False,
    ).generate_from_frequencies(freq)
 
    fig, ax = plt.subplots(figsize=(14, 9))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    fig.patch.set_alpha(0)
    plt.tight_layout(pad=0)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
 
####### ####### ####### ####### ####### ####### ####### 
####### METRICS  (from Map_311.py)

if not filtered.empty:
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    col1.metric("Hotspot Neighborhood", filtered["Neighborhood"].value_counts().idxmax())
    col2.metric("Total Reports", f"{len(filtered):,}")
    col3.metric("Top Complaint", filtered["Complaint"].value_counts().idxmax())
 
