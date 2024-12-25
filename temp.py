import streamlit as st
import pandas as pd
from interpolation import interpolate_k


def display_k_values(raw_data, combined_df):
    # ---- TEMPERATURE INPUTS ----
    st.sidebar.subheader("Select Temperatures")

    # Feed Temperature (T_f)
    T_f = st.sidebar.slider(
        'Feed Temperature (T_f):',
        min_value=float(combined_df.filter(like='T_').min().min()),
        max_value=float(combined_df.filter(like='T_').max().max()),
        step=0.1,
        value=150.0,  # Default value
        key="T_f"  # Unique key
    )

    # Bottom Temperature (T_b)
    T_b = st.sidebar.slider(
        'Bottom Temperature (T_b):',
        min_value=float(combined_df.filter(like='T_').min().min()),
        max_value=float(combined_df.filter(like='T_').max().max()),
        step=0.1,
        value=130.0,  # Default value
        key="T_b"  # Unique key
    )

    # Top Temperature (T_t)
    T_t = st.sidebar.slider(
        'Top Temperature (T_t):',
        min_value=float(combined_df.filter(like='T_').min().min()),
        max_value=float(combined_df.filter(like='T_').max().max()),
        step=0.1,
        value=160.0,  # Default value
        key="T_t"  # Unique key
    )

    # ---- INTERPOLATION CALCULATIONS ----
    st.subheader('Interpolated K-values:')
    results = {}
    try:
        # Use the global temperature slider for calculations
        for compound in raw_data.keys():
            temp_col = f'T_{compound}'  # Temperature column
            k_col = compound  # K-values column

            # Interpolate K-value for the selected temperature
            k_value = interpolate_k(combined_df[[temp_col, k_col]].dropna(), T_f)
            results[compound] = k_value

        # Show results
        results_df = pd.DataFrame(results.items(), columns=['Compound', 'K-value'])
        st.dataframe(results_df)

        # Download results
        csv = results_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download K-values as CSV",
            data=csv,
            file_name='interpolated_k_values.csv',
            mime='text/csv'
        )
    except ValueError as e:
        st.error(str(e))

    # Return the temperatures for further processing later
    return T_f, T_b, T_t
