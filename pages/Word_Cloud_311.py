# -*- coding: utf-8 -*-
"""
Word_Cloud_311.py
NYC 311 Dashboard - Word Cloud Page
I Love NY logo with complaint words filling the red heart.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from PIL import Image, ImageDraw, ImageFont
from wordcloud import WordCloud
from data_loader import load_data

st.set_page_config(page_title="NYC 311 Word Cloud", layout="wide")


# ─────────────────────────────────────────────
# BUILD HEART MASK
# Only the heart region is black (word fill area)
# Everything else is white (no words)
# ─────────────────────────────────────────────
@st.cache_resource
def build_heart_mask(W=400, H=400):
    """
    Creates a mask where the heart shape is black (0) = word area,
    and everything else is white (255) = background.
    Uses a parametric heart curve for a clean shape.
    """
    img = Image.new("L", (W, H), 255)  # grayscale, all white
    draw = ImageDraw.Draw(img)

    cx, cy = W // 2, H // 2 + 20
    scale = 130

    # Parametric heart: x = 16sin³t, y = 13cost - 5cos2t - 2cos3t - cos4t
    import math
    points = []
    steps = 300
    for i in range(steps + 1):
        t = 2 * math.pi * i / steps
        x = 16 * (math.sin(t) ** 3)
        y = -(13 * math.cos(t)
              - 5 * math.cos(2 * t)
              - 2 * math.cos(3 * t)
              - math.cos(4 * t))
        px = int(cx + scale * x / 16)
        py = int(cy + scale * y / 16)
        points.append((px, py))

    draw.polygon(points, fill=0)  # 0 = black = word area

    arr = np.array(img)
    # Stack to RGB so WordCloud accepts it
    return np.stack([arr, arr, arr], axis=-1).astype(np.uint8)


# ─────────────────────────────────────────────
# DRAW THE FULL I ♥ NY LOGO
# ─────────────────────────────────────────────
def draw_i_love_ny_logo(wc_image):
    """
    Takes the rendered word cloud image (PIL Image) of the heart,
    and composites it into the full I Love NY logo layout.
    Returns a matplotlib figure.
    """
    import math

    W, H = 900, 340
    logo = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    draw = ImageDraw.Draw(logo)

    # ── Draw the heart with word cloud inside ──
    heart_size = 220
    heart_img = wc_image.resize((heart_size, heart_size), Image.LANCZOS)

    # Convert heart wordcloud to RGBA
    heart_rgba = heart_img.convert("RGBA")

    # Paste heart onto logo (centered vertically, at ~1/3 from left)
    heart_x = 270
    heart_y = (H - heart_size) // 2 + 10
    logo.paste(heart_rgba, (heart_x, heart_y), heart_rgba)

    # ── Draw "I" on the left ──
    # We'll use matplotlib for text rendering (avoids font file dependency)
    fig, ax = plt.subplots(figsize=(11, 4.2), facecolor="white")
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")

    # Show the logo image
    ax.imshow(logo, extent=[0, W, 0, H], origin="upper", aspect="auto", zorder=1)

    # "I" — left side
    ax.text(
        160, H // 2 + 5,
        "I",
        fontsize=195,
        fontweight="bold",
        color="black",
        ha="center",
        va="center",
        fontfamily="serif",
        zorder=2,
    )

    # "NY" — right side
    ax.text(
        690, H // 2 + 5,
        "NY",
        fontsize=165,
        fontweight="bold",
        color="black",
        ha="center",
        va="center",
        fontfamily="serif",
        zorder=2,
    )

    plt.tight_layout(pad=0.1)
    return fig


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
max_words = st.sidebar.slider("Max Words", min_value=20, max_value=200, value=80, step=10)


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
st.markdown(f"Displaying **{len(filtered):,}** complaints — words fill the ❤️ in the I ♥ NY logo")

if filtered.empty:
    st.warning("No complaints match the current filters. Try broadening your selection.")
else:
    freq = filtered["Complaint"].value_counts().to_dict()

    # Generate word cloud shaped to heart, red bg, white words
    wc = WordCloud(
        mask=mask,
        background_color="red",
        color_func=lambda *args, **kwargs: "white",
        max_words=max_words,
        prefer_horizontal=0.80,
        contour_width=0,
        min_font_size=6,
        max_font_size=60,
        collocations=False,
    ).generate_from_frequencies(freq)

    wc_image = wc.to_image()  # PIL Image

    # Composite into full I ♥ NY logo
    fig = draw_i_love_ny_logo(wc_image)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    # Download the word cloud heart only
    from io import BytesIO
    buf = BytesIO()
    wc_image.save(buf, format="PNG")
    st.download_button(
        label="⬇️ Download Word Cloud",
        data=buf.getvalue(),
        file_name="i_love_ny_wordcloud.png",
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
