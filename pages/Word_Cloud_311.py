# -*- coding: utf-8 -*-
"""
Created on Sun Apr 19 11:49:18 2026

@author: ys3435 

- Word Cloud page for NYC 311 Dashboard
- Word cloud reshapes into the selected borough's silhouette.
- Filters mirror Map_311.py and Over_Time_311.py exactly.
"""#

import subprocess
import sys

subprocess.run([sys.executable, "-m", "pip", "install", "matplotlib", "wordcloud", "Pillow"],
               capture_output=True)

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFilter
from wordcloud import WordCloud
from data_loader import load_data
 
# ─────────────────────────────────────────────
# BOROUGH SILHOUETTE MASKS
# Black (0) = fill area, White (255) = background
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
    # Manhattan — tall narrow island shape
    manhattan = [
        (370, 10), (395, 12), (418, 20), (438, 34), (452, 52),
        (460, 74), (462, 98), (458, 124), (450, 150), (438, 175),
        (422, 198), (403, 220), (382, 240), (358, 258), (333, 273),
        (307, 285), (280, 293), (253, 297), (226, 297), (200, 292),
        (176, 283), (154, 270), (135, 254), (119, 235), (107, 214),
        (99, 192),  (95, 169),  (95, 146),  (99, 123),  (107, 101),
        (119, 81),  (135, 63),  (154, 48),  (176, 36),  (200, 27),
        (226, 22),  (253, 20),  (280, 21),  (307, 26),  (333, 35),
        (358, 47),  (370, 10),
    ]
 
    # Brooklyn — wide trapezoid shape
    brooklyn = [
        (60,  70), (200, 40), (350, 30), (500, 40), (620, 70),
        (700, 110),(740, 160),(730, 210),(700, 255),(655, 290),
        (600, 315),(540, 330),(475, 338),(410, 340),(345, 336),
        (282, 326),(222, 310),(168, 288),(122, 262),(86,  232),
        (62,  198),(50,  162),(50,  126),(62,   96),(60,   70),
    ]
 
    # Queens — large irregular blob
    queens = [
        (50, 200), (70, 155), (100, 112),(140, 74), (188, 44),
        (242, 22), (300, 8),  (362, 2),  (426, 4),  (488, 14),
        (546, 32), (596, 58), (636, 90), (662, 128),(674, 168),
        (672, 208),(656, 246),(628, 278),(590, 304),(544, 322),
        (494, 334),(442, 338),(390, 336),(338, 326),(290, 310),
        (246, 288),(208, 262),(176, 232),(152, 200),(136, 168),
        (92, 180), (50, 200),
    ]
 
    # Bronx — top-heavy shape
    bronx = [
        (100, 380),(112, 335),(132, 290),(160, 248),(196, 210),
        (238, 176),(284, 148),(334, 126),(386, 110),(440,  98),
        (494,  92),(546,  90),(594,  94),(636, 104),(668, 120),
        (690, 140),(700, 164),(698, 188),(684, 210),(660, 228),
        (628, 242),(590, 252),(550, 256),(510, 256),(470, 252),
        (432, 246),(396, 238),(362, 230),(330, 224),(300, 222),
        (272, 224),(248, 230),(228, 240),(212, 254),(200, 272),
        (192, 294),(188, 318),(188, 342),(188, 368),(144, 374),
        (100, 380),
    ]
 
    # Staten Island — oval/teardrop
    staten = [
        (240, 72), (286, 48), (336, 32), (390, 24), (444, 24),
        (496, 34), (540, 54), (574, 82), (596, 116),(604, 152),
        (600, 188),(582, 222),(554, 252),(518, 274),(476, 290),
        (432, 298),(386, 298),(340, 290),(298, 274),(262, 252),
        (232, 224),(212, 192),(202, 158),(202, 124),(214, 92),
        (240, 72),
    ]
 
    # All NYC — full canvas rectangle
    all_nyc = [(20, 20), (780, 20), (780, 480), (20, 480)]
 
    return {
        "All Manhattan": _make_mask([all_nyc]),
        "Manhattan":     _make_mask([manhattan]),
        "Brooklyn":      _make_mask([brooklyn]),
        "Queens":        _make_mask([queens]),
        "Bronx":         _make_mask([bronx]),
        "Staten Island": _make_mask([staten]),
    }
 
 
# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────
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
 
 
df    = get_data()
masks = build_masks()
 
 
# ─────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────
st.sidebar.header("Filter Manhattan Data")
 
hoods = ["All Manhattan"] + sorted(df["Neighborhood"].dropna().unique().astype(str))
selected_hood = st.sidebar.selectbox("Neighborhood", hoods)
 
groups = ["All Categories"] + sorted(df["Complaint_Group"].dropna().unique().astype(str))
selected_group = st.sidebar.selectbox("Complaint Category", groups)
 
if selected_group != "All Categories":
    relevant       = df[df["Complaint_Group"] == selected_group]["Complaint"].dropna().unique()
    issues         = ["All in Category"] + sorted(relevant.astype(str))
    selected_issue = st.sidebar.selectbox("Specific Issue", issues)
else:
    selected_issue = "All in Category"
 
st.sidebar.divider()
 
# Borough shape selector
borough_options  = ["All Manhattan", "Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"]
selected_borough = st.sidebar.selectbox("☁️ Word Cloud Shape", borough_options)
 
# Color theme selector
colormap_options = {
    "Red–Yellow–Blue": "RdYlBu",
    "NYC Subway (Spectral)": "Spectral",
    "Cool Blues": "Blues",
    "Warm Reds": "Reds",
    "Viridis": "viridis",
    "Plasma": "plasma",
}
selected_colormap_label = st.sidebar.selectbox("Color Theme", list(colormap_options.keys()))
selected_colormap        = colormap_options[selected_colormap_label]
 
# Max words slider
max_words = st.sidebar.slider("Max Words", min_value=20, max_value=200, value=100, step=10)
 
 
# ─────────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────────
filtered = df.copy()
 
if selected_hood != "All Manhattan":
    filtered = filtered[filtered["Neighborhood"] == selected_hood]
if selected_group != "All Categories":
    filtered = filtered[filtered["Complaint_Group"] == selected_group]
if selected_issue != "All in Category":
    filtered = filtered[filtered["Complaint"] == selected_issue]
 
 
# ─────────────────────────────────────────────
# PAGE HEADER
# ─────────────────────────────────────────────
st.title("☁️ NYC 311 Complaint Word Cloud")
st.markdown(
    f"Displaying **{len(filtered):,}** reports — "
    f"shaped as **{selected_borough}** · "
    f"color theme: **{selected_colormap_label}**"
)
 
 
# ─────────────────────────────────────────────
# WORD CLOUD
# ─────────────────────────────────────────────
if filtered.empty:
    st.warning("No complaints match the current filters. Try broadening your selection.")
else:
    freq = filtered["Complaint"].value_counts().to_dict()
    mask = masks[selected_borough]
 
    wc = WordCloud(
        mask=mask,
        background_color="white",
        colormap=selected_colormap,
        max_words=max_words,
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
 
    # Download button
    from io import BytesIO
    buf = BytesIO()
    wc_img = wc.to_image()
    wc_img.save(buf, format="PNG")
    st.download_button(
        label="⬇️ Download Word Cloud",
        data=buf.getvalue(),
        file_name=f"wordcloud_{selected_borough.replace(' ', '_')}.png",
        mime="image/png",
    )
 
 
# ─────────────────────────────────────────────
# METRICS
# ─────────────────────────────────────────────
if not filtered.empty:
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    col1.metric("Hotspot Neighborhood", filtered["Neighborhood"].value_counts().idxmax())
    col2.metric("Total Reports",        f"{len(filtered):,}")
    col3.metric("Top Complaint",        filtered["Complaint"].value_counts().idxmax())
 
 
# ─────────────────────────────────────────────
# TOP COMPLAINTS TABLE
# ─────────────────────────────────────────────
if not filtered.empty:
    st.markdown("### 📋 Top 10 Complaints")
    top10 = (
        filtered["Complaint"]
        .value_counts()
        .head(10)
        .reset_index()
    )
    top10.columns = ["Complaint", "Count"]
    st.dataframe(top10, use_container_width=True, hide_index=True)
 
