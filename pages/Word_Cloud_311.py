# -*- coding: utf-8 -*-
"""
Word_Cloud_311.py
NYC 311 Dashboard - Word Cloud Page
Word cloud shaped as a heart (I Love NY style).
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
from wordcloud import WordCloud
from data_loader import load_data

st.set_page_config(page_title="NYC 311 Word Cloud", layout="wide")


# ─────────────────────────────────────────────
# HEART MASK  (black = fill area, white = background)
# ─────────────────────────────────────────────
@st.cache_resource
def build_heart_mask(W=800, H=700):
    img = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(img)

    cx, cy = W // 2, H // 2
    r = 180

    # Left circle of heart
    draw.ellipse(
        [cx - r - r // 2, cy - r - 30, cx - r // 2 + r // 2, cy + r // 2],
        fill="black"
    )
    # Right circle of heart
    draw.ellipse(
        [cx - r // 2 + r // 4, cy - r - 30, cx + r + r // 4, cy + r // 2],
        fill="black"
    )
    # Bottom triangle to form the point
    draw.polygon(
        [
            (cx - r - r // 2 + 10, cy + r // 4),
            (cx + r + r // 4 - 10,  cy + r // 4),
            (cx + r // 8,            cy + r * 2),
        ],
        fill="black"
    )

    arr = np.array(img)
    return np.where(arr < 128, 0, 255).astype(np.uint8)


# ─────────────────────────────────────────────
# DATA
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


df   = get_data()
mask = build_heart_mask()


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
# PAGE
# ─────────────────────────────────────────────
st.title("🗽 NYC 311 Complaint Word Cloud")
st.markdown(f"Displaying **{len(filtered):,}** reports — words inside a red heart")

if filtered.empty:
    st.warning("No complaints match the current filters. Try broadening your selection.")
else:
    freq = filtered["Complaint"].value_counts().to_dict()

    # Red heart background, white words
    wc = WordCloud(
        mask=mask,
        background_color="red",
        color_func=lambda *args, **kwargs: "white",
        max_words=max_words,
        prefer_horizontal=0.85,
        contour_width=5,
        contour_color="#8B0000",
        min_font_size=8,
        max_font_size=120,
        collocations=False,
    ).generate_from_frequencies(freq)

    fig, ax = plt.subplots(figsize=(10, 9), facecolor="white")
    ax.imshow(wc, interpolation="bilinear")

    # "I ♥ NY" label overlaid on the heart
    ax.text(
        0.5, 0.10,
        "I  \u2665  NY",
        transform=ax.transAxes,
        fontsize=40,
        fontweight="bold",
        color="white",
        ha="center",
        va="center",
        zorder=5,
        bbox=dict(
            boxstyle="round,pad=0.4",
            facecolor="red",
            edgecolor="#8B0000",
            linewidth=2,
        )
    )

    ax.axis("off")
    plt.tight_layout(pad=0)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    # Download button
    from io import BytesIO
    buf = BytesIO()
    wc.to_image().save(buf, format="PNG")
    st.download_button(
        label="\u2b07\ufe0f Download Word Cloud",
        data=buf.getvalue(),
        file_name="wordcloud_i_love_ny.png",
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
# TOP 10 TABLE
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
