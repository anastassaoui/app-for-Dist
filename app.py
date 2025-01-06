import streamlit as st
from data_import import load_data
from temp import load_and_combine_data, display_results

st.set_page_config(page_title="FUG Method - Distillation App", layout="wide")

raw_data = load_data()
combined_df = load_and_combine_data(raw_data)

st.title('FUG Method')

display_results(raw_data, combined_df)
