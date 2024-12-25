import streamlit as st
import pandas as pd
from mitosheet.streamlit.v1 import spreadsheet
from data_import import load_data
from interpolation import interpolate_k


st.set_page_config(page_title="FUG Method - Interpolation", layout="wide")

# Load raw data
raw_data = load_data()

# Prepare merged DataFrame with separate columns for each compound
combined_df = pd.DataFrame()

for compound, df in raw_data.items():
    # Rename columns: keep 'T' and compound-specific K values
    df = df.rename(columns={'T': f'T_{compound}', df.columns[1]: compound})
    # Concatenate as new columns
    combined_df = pd.concat([combined_df, df], axis=1)

# Streamlit App Title
st.title('FUG Method - K-Value Interpolation with Mito')

# Display combined data in Mito spreadsheet
st.subheader('Edit Combined CSV Data:')
final_dfs, code = spreadsheet(combined_df)

# Use edited data if available; fallback to the original combined data
if final_dfs:
    combined_df = list(final_dfs.values())[0]  # Retrieve the first edited dataframe

# Display generated Python code
st.subheader("Generated Python Code:")
st.code(code)

# Single temperature input slider for the user
global_temp = st.slider(
    'Select Temperature (T):',
    min_value=float(combined_df.filter(like='T_').min().min()),  # Minimum across all T columns
    max_value=float(combined_df.filter(like='T_').max().max()),  # Maximum across all T columns
    step=0.1
)

# Perform interpolation for each compound
st.subheader('Interpolated K-values:')
results = {}
try:
    for compound in raw_data.keys():
        temp_col = f'T_{compound}'  # Temperature column for each compound
        k_col = compound  # K-values column
        
        # Interpolate K-value for the selected temperature
        k_value = interpolate_k(combined_df[[temp_col, k_col]].dropna(), global_temp)
        results[compound] = k_value

    # Show results
    results_df = pd.DataFrame(results.items(), columns=['Compound', 'K-value'])
    st.dataframe(results_df)

    # Download results
    csv = results_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Results as CSV",
        data=csv,
        file_name='interpolated_k_values.csv',
        mime='text/csv'
    )
except ValueError as e:
    st.error(str(e))
