import streamlit as st
import pandas as pd
from interpolation import interpolate_k


# ---- DATA LOADING AND COMBINING ----
def load_and_combine_data(raw_data):
    """Loads and combines raw data for multiple compounds into a single DataFrame."""
    combined_df = pd.DataFrame()
    for compound, df in raw_data.items():
        # Rename columns to include compound name
        df = df.rename(
            columns={
                'T': f'T_{compound}',
                df.columns[1]: compound
            }
        )
        # Concatenate data into one DataFrame
        combined_df = pd.concat([combined_df, df], axis=1)
    return combined_df


# ---- DISPLAY INTERPOLATED K-VALUES ----
def display_k_values(raw_data, combined_df):
    """Displays interpolated K-values and calculates relative volatilities (α)."""

    # ---- INPUTS ----
    st.sidebar.subheader("Select Temperatures")

    # Temperature sliders
    T_f = st.sidebar.slider(
        'Feed Temperature (T_f):',
        min_value=float(combined_df.filter(like='T_').min().min()),
        max_value=float(combined_df.filter(like='T_').max().max()),
        step=0.0001,
        value=150.0,
        key="T_f"
    )
    T_b = st.sidebar.slider(
        'Bottom Temperature (T_b):',
        min_value=float(combined_df.filter(like='T_').min().min()),
        max_value=float(combined_df.filter(like='T_').max().max()),
        step=0.0001,
        value=130.0,
        key="T_b"
    )
    T_t = st.sidebar.slider(
        'Top Temperature (T_t):',
        min_value=float(combined_df.filter(like='T_').min().min()),
        max_value=float(combined_df.filter(like='T_').max().max()),
        step=0.0001,
        value=300.0,
        key="T_t"
    )

    # ---- SELECT KEYS ----
    st.subheader("Select Keys")

    # Light and Heavy Keys Selection
    col1, col2 = st.sidebar.columns(2)

    with col1:
        light_key = st.selectbox(
            'Select Light Key:',
            options=list(raw_data.keys()),
            index=0
        )

    with col2:
        heavy_key = st.selectbox(
            'Select Heavy Key:',
            options=list(raw_data.keys()),
            index=1
        )

    # ---- FILTRATION SYSTEM ----
    st.sidebar.subheader("Filter Compounds")

    # Filter compounds for distillate and bottoms
    distillate_compounds = st.sidebar.multiselect(
        'Compounds in Distillate:',
        options=list(raw_data.keys()),
        default=list(raw_data.keys())[0:3]
    )
    bottom_compounds = st.sidebar.multiselect(
        'Compounds in Bottoms:',
        options=list(raw_data.keys()),
        default=list(raw_data.keys())[3:6]
    )

    # ---- INTERPOLATION AND RELATIVE VOLATILITY CALCULATIONS ----
    st.subheader('Interpolated K-values and Relative Volatility (α):')

    # Results table
    results = {
        "Compound": [],
        "K_FEED": [],
        "K_BOTTOM": [],
        "K_TOP": [],
        "Alpha_FEED (α)": [],
        "Alpha_BOTTOM (α)": [],
        "Alpha_TOP (α)": [],
        "Alpha_AVG (α)": []
    }

    try:
        # Calculate values for each compound
        for compound in raw_data.keys():
            temp_col = f'T_{compound}'  # Temperature column
            k_col = compound  # K-values column

            # Interpolate K-values
            k_feed = interpolate_k(combined_df[[temp_col, k_col]].dropna(), T_f)

            # Bottom and Top interpolations (check existence first)
            k_bottom = None
            k_top = None

            if compound in bottom_compounds:
                k_bottom = interpolate_k(combined_df[[temp_col, k_col]].dropna(), T_b)

            if compound in distillate_compounds:
                k_top = interpolate_k(combined_df[[temp_col, k_col]].dropna(), T_t)

            # Calculate relative volatility (α) only where valid data exists
            if compound != heavy_key:
                k_heavy_feed = interpolate_k(combined_df[[f'T_{heavy_key}', heavy_key]].dropna(), T_f)

                k_heavy_bottom = None
                k_heavy_top = None

                if compound in bottom_compounds:
                    k_heavy_bottom = interpolate_k(combined_df[[f'T_{heavy_key}', heavy_key]].dropna(), T_b)

                if compound in distillate_compounds:
                    k_heavy_top = interpolate_k(combined_df[[f'T_{heavy_key}', heavy_key]].dropna(), T_t)

                alpha_feed = k_feed / k_heavy_feed if k_heavy_feed != 0 else None
                alpha_bottom = k_bottom / k_heavy_bottom if k_bottom and k_heavy_bottom else None
                alpha_top = k_top / k_heavy_top if k_top and k_heavy_top else None
            else:
                # Heavy key has α = 1 by definition
                alpha_feed, alpha_bottom, alpha_top = 1.0, 1.0, 1.0

            # Calculate Alpha_AVG using valid α values
            alpha_values = [a for a in [alpha_feed, alpha_bottom, alpha_top] if a is not None]
            alpha_avg = sum(alpha_values) / len(alpha_values) if alpha_values else None

            # Append results
            results["Compound"].append(compound)
            results["K_FEED"].append(f"{k_feed:.2f}")
            results["K_BOTTOM"].append(f"{k_bottom:.2f}" if k_bottom else "N/A")
            results["K_TOP"].append(f"{k_top:.2f}" if k_top else "N/A")
            results["Alpha_FEED (α)"].append(f"{alpha_feed:.2f}" if alpha_feed else "N/A")
            results["Alpha_BOTTOM (α)"].append(f"{alpha_bottom:.2f}" if alpha_bottom else "N/A")
            results["Alpha_TOP (α)"].append(f"{alpha_top:.2f}" if alpha_top else "N/A")
            results["Alpha_AVG (α)"].append(f"{alpha_avg:.2f}" if alpha_avg else "N/A")

        # Display results
        results_df = pd.DataFrame(results)
        st.dataframe(results_df)

    except ValueError as e:
        st.error(str(e))

    # Return all inputs for further processing
    return T_f, T_b, T_t, light_key, heavy_key, distillate_compounds, bottom_compounds
