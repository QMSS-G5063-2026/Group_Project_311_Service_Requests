# -*- coding: utf-8 -*-
"""
Created on Sun Apr 19 12:32:52 2026

@author: mw3595
"""

import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    df = pd.read_csv("NYC_311_Master_2024_2025.csv")

    # optional light cleaning (recommended)
    df = df.dropna(subset=["Complaint", "Borough"])

    return df