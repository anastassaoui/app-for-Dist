import streamlit as st
import pandas as pd
from interpolation import interpolate_k


# ---- DATA LOADING AND COMBINING ----
def load_and_combine_data(raw_data):
    """Loads and combines raw data for multiple compounds into a single DataFrame."""
    combined_df = pd.DataFrame()
    for compound, df in raw_data.items():
        df = df.rename(
            columns={
                'T': f'T_{compound}',
                df.columns[1]: compound
            }
        )
        combined_df = pd.concat([combined_df, df], axis=1)
    return combined_df


# ---- DISPLAY RESULTS ----
def display_results(raw_data, combined_df):
    """Displays interpolated K-values, relative volatilities (α), and fraction calculations."""

    # ---- INPUTS ----
    st.sidebar.subheader("Select Temperatures")

    # Temperature sliders
    T_f = st.sidebar.slider('Feed Temperature (T_f):', 
                            min_value=float(combined_df.filter(like='T_').min().min()),
                            max_value=float(combined_df.filter(like='T_').max().max()),
                            step=0.0001, value=150.0)

    T_b = st.sidebar.slider('Bottom Temperature (T_b):', 
                            min_value=float(combined_df.filter(like='T_').min().min()),
                            max_value=float(combined_df.filter(like='T_').max().max()),
                            step=0.0001, value=130.0)

    T_t = st.sidebar.slider('Top Temperature (T_t):', 
                            min_value=float(combined_df.filter(like='T_').min().min()),
                            max_value=float(combined_df.filter(like='T_').max().max()),
                            step=0.0001, value=300.0)

    # ---- KEYS ----
    st.sidebar.subheader("Select Keys")

    col1 ,col2 = st.sidebar.columns(2)
    with col1:
        light_key = st.selectbox('Select Light Key:', options=list(raw_data.keys()), index=0)
    with col2:
        heavy_key = st.selectbox('Select Heavy Key:', options=list(raw_data.keys()), index=1)

    # ---- FILTERS ----
    distillate_compounds = st.sidebar.multiselect('Compounds in Distillate:', options=list(raw_data.keys()), default=list(raw_data.keys())[0:3])
    bottom_compounds = st.sidebar.multiselect('Compounds in Bottoms:', options=list(raw_data.keys()), default=list(raw_data.keys())[3:6])

    # ---- INTERPOLATION ----
    results = {
        "Compound": [], "K_F": [], "K_B": [], "K_D": [],
        "α F": [], "α B": [], "α D": [], "α AVG": []
    }

    for compound in raw_data.keys():
        temp_col = f'T_{compound}'
        k_col = compound

        # K-values
        k_feed = interpolate_k(combined_df[[temp_col, k_col]].dropna(), T_f)
        k_bottom = interpolate_k(combined_df[[temp_col, k_col]].dropna(), T_b) if compound in bottom_compounds else None
        k_top = interpolate_k(combined_df[[temp_col, k_col]].dropna(), T_t) if compound in distillate_compounds else None

        # α-values
        k_heavy_feed = interpolate_k(combined_df[[f'T_{heavy_key}', heavy_key]].dropna(), T_f)
        alpha_feed = k_feed / k_heavy_feed if k_heavy_feed != 0 else None
        alpha_bottom = k_bottom / interpolate_k(combined_df[[f'T_{heavy_key}', heavy_key]].dropna(), T_b) if k_bottom else None
        alpha_top = k_top / interpolate_k(combined_df[[f'T_{heavy_key}', heavy_key]].dropna(), T_t) if k_top else None

        alpha_values = [a for a in [alpha_feed, alpha_bottom, alpha_top] if a is not None]
        alpha_avg = sum(alpha_values) / len(alpha_values) if alpha_values else None

        # Append results
        results["Compound"].append(compound)
        results["K_F"].append(f"{k_feed:.2f}")
        results["K_B"].append(f"{k_bottom:.2f}" if k_bottom else "N/A")
        results["K_D"].append(f"{k_top:.2f}" if k_top else "N/A")
        results["α F"].append(f"{alpha_feed:.2f}" if alpha_feed else "N/A")
        results["α B"].append(f"{alpha_bottom:.2f}" if alpha_bottom else "N/A")
        results["α D"].append(f"{alpha_top:.2f}" if alpha_top else "N/A")
        results["α AVG"].append(f"{alpha_avg:.2f}" if alpha_avg else "N/A")

    results_df = pd.DataFrame(results)

    # ---- FRACTIONS ----
    st.sidebar.header("Input Flow Rates")
    components = ['iC4', 'nC4', 'iC5', 'nC5', 'C6', 'C7', 'C8', 'C9']

    # Feed Rates
    st.sidebar.subheader("Feed (lbmol/h)")
    feed_rates = {}
    cols = st.sidebar.columns(3)
    for idx, comp in enumerate(components):
        with cols[idx % 3]:
            feed_rates[comp] = st.slider(f"{comp} Feed", 0.0, 500.0, 50.0, key=f"{comp}_feed")


    st.sidebar.subheader("Top (lbmol/h)")
    top_rates = {}
    cols = st.sidebar.columns(3)
    for idx, comp in enumerate(components[:4]):
        with cols[idx % 3]:
            top_rates[comp] = st.slider(f"{comp} Top", 0.0, 500.0, 50.0, key=f"{comp}_top")


    st.sidebar.subheader("Bottom (lbmol/h)")
    bottom_rates = {}
    cols = st.sidebar.columns(3)
    for idx, comp in enumerate(components[1:]):
        with cols[idx % 3]:
            bottom_rates[comp] = st.slider(f"{comp} Bottom", 0.0, 500.0, 50.0, key=f"{comp}_bottom")


    # Fractions Calculation
    feed_total = sum(feed_rates.values())
    top_total = sum(top_rates.values())
    bottom_total = sum(bottom_rates.values())

    fraction_df = pd.DataFrame({
        "F": [feed_rates[c] for c in components],
        "z": [feed_rates[c] / feed_total for c in components],
        "D": [top_rates.get(c, 0) for c in components],
        "xd": [top_rates.get(c, 0) / top_total if c in top_rates else 0 for c in components],
        "B": [bottom_rates.get(c, 0) for c in components],
        "xb": [bottom_rates.get(c, 0) / bottom_total if c in bottom_rates else 0 for c in components],
    })

    # ---- FINAL RESULTS ----
    final_df = pd.concat([results_df, fraction_df], axis=1)
    st.dataframe(final_df)


