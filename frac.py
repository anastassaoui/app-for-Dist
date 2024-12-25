# frac.py
import streamlit as st
import pandas as pd
from mitosheet.streamlit.v1 import spreadsheet

def calculate_fractions(feed_rates, top_rates, bottom_rates):
    # ---- FRACTIONS CALCULATION ----
    st.subheader("Fractions Calculation")

    # ---- TOTAL FLOWS ----
    feed_total = sum(feed_rates.values())
    top_total = sum(top_rates.values())
    bottom_total = sum(bottom_rates.values())

    # ---- FRACTIONS ----
    feed_df = pd.DataFrame.from_dict(feed_rates, orient='index', columns=['Feed (lbmol/h)'])
    feed_df['z (fraction)'] = feed_df['Feed (lbmol/h)'] / feed_total

    top_df = pd.DataFrame.from_dict(top_rates, orient='index', columns=['Top (lbmol/h)'])
    top_df['xd (fraction)'] = top_df['Top (lbmol/h)'] / top_total

    bottom_df = pd.DataFrame.from_dict(bottom_rates, orient='index', columns=['Bottom (lbmol/h)'])
    bottom_df['xb (fraction)'] = bottom_df['Bottom (lbmol/h)'] / bottom_total

    # ---- COMBINE FRACTIONS ----
    combined_fractions_df = pd.concat([feed_df, top_df, bottom_df], axis=1)

    # ---- DISPLAY FRACTIONS IN MITO ----
    st.subheader("Fractions as Mito Spreadsheet")
    final_dfs, code = spreadsheet(combined_fractions_df)

    # ---- DOWNLOAD RESULTS ----
    csv = combined_fractions_df.to_csv().encode('utf-8')
    st.download_button(
        label="Download Fractions as CSV",
        data=csv,
        file_name='fractions_data.csv',
        mime='text/csv'
    )

    return final_dfs, code
