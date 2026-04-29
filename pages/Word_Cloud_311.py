# -*- coding: utf-8 -*-
"""
Word_Cloud_311.py
NYC 311 Dashboard - Word Cloud Page
I Love NY logo with complaint words filling the red heart.
"""

import math
from io import BytesIO

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
from wordcloud import WordCloud
from data_loader import load_data

st.set_page_config(page_title="NYC 311 Word Cloud", layout="wide")


# ─────────────────────────────────────────────
# HEART WORD CLOUD
# Returns RGBA PIL image: heart = red bg +
# white words, outside = transparent
# ─────────────────────────────────────────────
def build_heart_wordcloud(freq, max_words=80, size=1000):
    W = H = size

    # Parametric heart mask
    mask_img = Image.new("L", (W, H), 255)
    draw = ImageDraw.Draw(mask_img)
    cx, cy = W // 2, int(H * 0.52)
    scale = W * 0.44
    points = []
    for i in range(3000):
        t = 2 * math.pi * i / 3000
        x = 16 * math.sin(t) ** 3
        y = -(
            13 * math.cos(t)
            - 5 * math.cos(2 * t)
            - 2 * math.cos(3 * t)
            - math.cos(4 * t)
        )
        px = int(cx + scale * x / 16)
        py = int(cy + scale * y / 16)
        points.append((px, py))
    draw.polygon(points, fill=0)
    mask_arr = np.array(mask_img)

    rgb_mask = np.stack([mask_arr] * 3, axis=-1).astype(np.uint8)

    wc = WordCloud(
        mask=rgb_mask,
        background_color="red",
        color_func=lambda *a, **k: "white",
        max_words=max_words,
        prefer_horizontal=0.75,
        contour_width=0,
        min_font_size=10,
        max_font_size=90,
        collocations=False,
        relative_scaling=0.6,
    ).generate_from_frequencies(freq)

    wc_rgb = np.array(wc.to_image())

    # Transparent outside heart
    rgba = np.ones((H, W, 4), dtype=np.uint8) * 255
    rgba[:, :, :3] = wc_rgb
    rgba[mask_arr > 128, 3] = 0

    return Image.fromarray(rgba, "RGBA"), wc


# ─────────────────────────────────────────────
# COMPOSE FULL I ♥ NY LOGO
# Heart dominates center, I and NY hug edges
# ─────────────────────────────────────────────
def compose_logo(heart_img):
    # Tight layout: I=180px | gap=20 | heart=660px | gap=20 | NY=420px
    LOGO_W = 1300
    LOGO_H = 520

    canvas = Image.new("RGB", (LOGO_W, LOGO_H), (255, 255, 255))

    # Heart: 660px, starting at x=200
    heart_size = 660
    h_res = heart_img.resize((heart_size, heart_size), Image.LANCZOS)
    hx = 200
    hy = (LOGO_H - heart_size) // 2 + 5
    canvas.paste(h_res, (hx, hy), h_res)

    # Bold serif text on transparent layer
    fig_txt, ax_txt = plt.subplots(
        figsize=(LOGO_W / 100, LOGO_H / 100), facecolor="none"
    )
    fig_txt.patch.set_alpha(0)
    ax_txt.set_xlim(0, LOGO_W)
    ax_txt.set_ylim(0, LOGO_H)
    ax_txt.axis("off")

    # "I" — hugging left edge of heart
    ax_txt.text(
        95, LOGO_H // 2 + 10, "I",
        fontsize=230, fontweight="bold", color="black",
        ha="center", va="center", fontfamily="DejaVu Serif",
    )

    # "NY" — hugging right edge of heart
    ax_txt.text(
        1080, LOGO_H // 2 + 10, "NY",
        fontsize=200, fontweight="bold", color="black",
        ha="center", va="center", fontfamily="DejaVu Serif",
    )

    plt.tight_layout(pad=0)
    buf = BytesIO()
    fig_txt.savefig(buf, format="png", dpi=100,
                    bbox_inches="tight", transparent=True)
    plt.close(fig_txt)

    buf.seek(0)
    text_img = Image.open(buf).convert("RGBA")
    text_img = text_img.resize((LOGO_W, LOGO_H), Image.LANCZOS)

    canvas_rgba = canvas.convert("RGBA")
    canvas_rgba.paste(text_img, (0, 0), text_img)
    result = canvas_rgba.convert("RGB")

    # Final figure for Streamlit
    fig, ax = plt.subplots(figsize=(13, 5.2), facecolor="white")
    ax.imshow(np.array(result))
    ax.axis("off")
    plt.tight_layout(pad=0)
    return fig, result


# ─────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────
@st.cache_data(show_spinner="Loading 311 data...")
def get_data():
    df = load_data()
    df["Incident Zip"] = df["Incident Zip"].astype(str)
    df = df[
        (df["Incident Zip"].str.len() == 5)
        & (df["Incident Zip"] != "00000")
        & (df["Incident Zip"].str.isnumeric())
    ]
    df["Created Date"] = pd.to_datetime(df["Created Date"], errors="coerce")
    df = df.dropna(subset=["Created Date"])
    return df


df = get_data()


# ─────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────
st.sidebar.header("Filter Manhattan Data")

hoods = ["All Manhattan"] + sorted(df["Neighborhood"].dropna().unique().astype(str))
selected_hood = st.sidebar.selectbox("Neighborhood", hoods)

groups = ["All Categories"] + sorted(df["Complaint_Group"].dropna().unique().astype(str))
selected_group = st.sidebar.selectbox("Complaint Category", groups)

if selected_group != "All Categories":
    relevant = df[df["Complaint_Group"] == selected_group]["Complaint"].dropna().unique()
    issues = ["All in Category"] + sorted(relevant.astype(str))
    selected_issue = st.sidebar.selectbox("Specific Issue", issues)
else:
    selected_issue = "All in Category"

st.sidebar.divider()
max_words = st.sidebar.slider("Max Words in Heart", min_value=20, max_value=150, value=80, step=10)


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
st.markdown(
    f"Displaying **{len(filtered):,}** complaints — "
    "NYC 311 issues fill the ❤️ in the I ♥ NY logo"
)

if filtered.empty:
    st.warning("No complaints match the current filters. Try broadening your selection.")
else:
    freq = filtered["Complaint"].value_counts().to_dict()

    with st.spinner("Generating word cloud..."):
        heart_img, wc_obj = build_heart_wordcloud(freq, max_words=max_words, size=1000)
        fig, result_img = compose_logo(heart_img)

    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    # Download
    buf_out = BytesIO()
    result_img.save(buf_out, format="PNG")
    st.download_button(
        label="⬇️ Download I ♥ NY Word Cloud",
        data=buf_out.getvalue(),
        file_name="i_love_ny_311_wordcloud.png",
        mime="image/png",
    )


# ─────────────────────────────────────────────
# METRICS
# ─────────────────────────────────────────────
if not filtered.empty:
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    col1.metric("Hotspot Neighborhood", filtered["Neighborhood"].value_counts().idxmax())
    col2.metric("Total Reports", f"{len(filtered):,}")
    col3.metric("Top Complaint", filtered["Complaint"].value_counts().idxmax())


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
