# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 16:17:41 2026

@author: mw3595
"""

import streamlit as st
import numpy as np
import pandas as pd

st.title("My First App")

df = pd.read_csv("NYC_311_Master_2025_mw2.csv")

st.write(df)