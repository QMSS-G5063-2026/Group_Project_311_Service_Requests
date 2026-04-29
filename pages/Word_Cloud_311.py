# -*- coding: utf-8 -*-
"""
Word_Cloud_311.py
NYC 311 Dashboard - Word Cloud Page
I Love NY logo with complaint words filling the red heart.
"""
# -*- coding: utf-8 -*-
"""

import math
from io import BytesIO

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
from wordcloud import WordCloud
from data_loader import load_data

st.set_page_config(page_title="NYC 311 Word Cloud", layout="wide")

FONT_PATH = "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf"

# ── Canvas based on original logo scaled 4x ─────────────────────────
# Original logo: 414x122px
# I:     x=11..65,   y=21..113
# Heart: x=73..180,  y=21..115
# NY:    x=192..403, y=21..113
SCALE      = 4
CANVAS_W   = 414 * SCALE          # 1656
CANVAS_H   = 122 * SCALE          # 488
I_CX       = 38  * SCALE          # 152  — center x of "I"
HEART_LX   = 73  * SCALE          # 292  — heart left x
HEART_RX   = 180 * SCALE          # 720  — heart right x
HEART_TY   = 21  * SCALE          # 84   — heart top y
HEART_BY   = 115 * SCALE          # 460  — heart bottom y
NY_CX      = 298 * SCALE          # 1192 — center x of "NY"
TEXT_TY    = 21  * SCALE          # 84   — text top y
TEXT_BY    = 113 * SCALE          # 452  — text bottom y

HEART_W    = HEART_RX - HEART_LX  # 428
HEART_H    = HEART_BY - HEART_TY  # 376
TEXT_H     = TEXT_BY  - TEXT_TY   # 368


# ─────────────────────────────────────────────
# HEART WORD CLOUD — red bg, black words
# ─────────────────────────────────────────────
def build_heart_wc(freq, max_words=60):
    size = 700
    W = H = size
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
        color_func=lambda *a, **k: "black",
        max_words=max_words,
        prefer_horizontal=0.80,
        contour_width=0,
        min_font_size=7,
        max_font_size=55,
        collocations=False,
        relative_scaling=0.5,
    ).generate_from_frequencies(freq)

    wc_rgb = np.array(wc.to_image())
    rgba = np.ones((H, W, 4), dtype=np.uint8) * 255
    rgba[:, :, :3] = wc_rgb
    rgba[mask_arr > 128, 3] = 0
    return Image.fromarray(rgba, "RGBA"), wc


# ─────────────────────────────────────────────
# RENDER LETTER — auto-sizes to exact height
# ─────────────────────────────────────────────
def render_letter(text, target_height):
    for fs in range(600, 50, -2):
        try:
            font = ImageFont.truetype(FONT_PATH, fs)
        except Exception:
            font = ImageFont.load_default()
            break
        dummy = Image.new("RGBA", (1, 1))
        bbox = ImageDraw.Draw(dummy).textbbox((0, 0), text, font=font)
        if (bbox[3] - bbox[1]) <= target_height:
            break
    pad = 6
    w = bbox[2] - bbox[0] + pad * 2
    h = bbox[3] - bbox[1] + pad * 2
    img = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    ImageDraw.Draw(img).text(
        (-bbox[0] + pad, -bbox[1] + pad),
        text, font=font, fill=(0, 0, 0, 255)
    )
    return img


# ─────────────────────────────────────────────
# COMPOSE FULL LOGO
# ─────────────────────────────────────────────
def compose_logo(heart_img):
    i_img  = render_letter("I",  TEXT_H)
    ny_img = render_letter("NY", TEXT_H)

    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (255, 255, 255, 255))

    # Heart
    h_res = heart_img.resize((HEART_W, HEART_H), Image.LANCZOS)
    canvas.paste(h_res, (HEART_LX, HEART_TY), h_res)

    # "I" — centered in its zone
    i_x = I_CX - i_img.width // 2
    i_y = (CANVAS_H - i_img.height) // 2
    canvas.paste(i_img, (i_x, i_y), i_img)

    # "NY" — centered in its zone
    ny_x = NY_CX - ny_img.width // 2
    ny_y = (CANVAS_H - ny_img.height) // 2
    canvas.paste(ny_img, (ny_x, ny_y), ny_img)

    result = canvas.convert("RGB")

    fig, ax = plt.subplots(
        figsize=(CANVAS_W / 120, CANVAS_H / 120), facecolor="white"
    )
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
max_words = st.sidebar.slider("Max Words in Heart", min_value=20, max_value=120, value=60, step=10)


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
        heart_img, wc_obj = build_heart_wc(freq, max_words=max_words)
        fig, result_img = compose_logo(heart_img)

    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

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
