import streamlit as st
import pandas as pd
from mitosheet.streamlit.v1 import spreadsheet
from data_import import load_data
from temp import display_k_values  # Import Temp module
from frac import calculate_fractions  # Import Fractions module

# ---- PAGE CONFIGURATION ----
st.set_page_config(page_title="FUG Method - Distillation App", layout="wide")

# ---- LOAD DATA ----
raw_data = load_data()

# ---- PREPARE COMBINED DATAFRAME ----
combined_df = pd.DataFrame()
for compound, df in raw_data.items():
    df = df.rename(columns={'T': f'T_{compound}', df.columns[1]: compound})
    combined_df = pd.concat([combined_df, df], axis=1)

# ---- TITLE ----
st.title('FUG Method - Distillation App')

# ---- EDITABLE CSV IN MITO :')
final_dfs, code = spreadsheet(combined_df)

if final_dfs:
    combined_df = list(final_dfs.values())[0]


# ---- DISPLAY K-VALUES ----
display_k_values(raw_data, combined_df)

# ---- SIDEBAR INPUTS ----
st.sidebar.header("Input Flow Rates")

# ---- FEED INPUT ----
st.sidebar.subheader("Feed (lbmol/h)")
feed_components = ['iC4', 'nC4', 'iC5', 'nC5', 'C6', 'C7', 'C8', 'C9']
feed_rates = {}
col1, col2 = st.sidebar.columns(2)
for idx, component in enumerate(feed_components):
    col = col1 if idx % 2 == 0 else col2
    feed_rates[component] = col.slider(
        f'{component}', min_value=0.0, max_value=500.0, value=50.0, step=0.1, key=f'{component}_feed'
    )

# ---- TOP INPUT ----
st.sidebar.subheader("Top (lbmol/h)")
top_components = ['iC4', 'nC4', 'iC5', 'nC5']
top_rates = {}
col1, col2 = st.sidebar.columns(2)
for idx, component in enumerate(top_components):
    col = col1 if idx % 2 == 0 else col2
    top_rates[component] = col.slider(
        f'{component}', min_value=0.0, max_value=500.0, value=50.0, step=0.1, key=f'{component}_top'
    )

# ---- BOTTOM INPUT ----
st.sidebar.subheader("Bottom (lbmol/h)")
bottom_components = ['nC4', 'iC5', 'nC5', 'C6', 'C7', 'C8', 'C9']
bottom_rates = {}
col1, col2 = st.sidebar.columns(2)
for idx, component in enumerate(bottom_components):
    col = col1 if idx % 2 == 0 else col2
    bottom_rates[component] = col.slider(
        f'{component}', min_value=0.0, max_value=500.0, value=50.0, step=0.1, key=f'{component}_bottom'
    )

# ---- CALL FRACTIONS MODULE ----
calculate_fractions(feed_rates, top_rates, bottom_rates)
