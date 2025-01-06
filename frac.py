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


# ---- DISPLAY RESULTS ----
def display_results(raw_data, combined_df):
    """Displays interpolated K-values, relative volatilities, and fraction calculations."""

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

    # Select Light and Heavy Keys
    st.sidebar.subheader("Select Keys")
    light_key = st.selectbox('Select Light Key:', options=list(raw_data.keys()), index=0)
    heavy_key = st.selectbox('Select Heavy Key:', options=list(raw_data.keys()), index=1)

    # Filter compounds
    st.sidebar.subheader("Filter Compounds")
    distillate_compounds = st.sidebar.multiselect('Compounds in Distillate:', options=list(raw_data.keys()), default=list(raw_data.keys())[:3])
    bottom_compounds = st.sidebar.multiselect('Compounds in Bottoms:', options=list(raw_data.keys()), default=list(raw_data.keys())[3:6])

    # ---- INTERPOLATION AND RELATIVE VOLATILITY ----
    st.subheader('Interpolated K-values and Relative Volatility (α):')

    results = {
        "Compound": [], "K_FEED": [], "K_BOTTOM": [], "K_TOP": [],
        "Alpha_FEED (α)": [], "Alpha_BOTTOM (α)": [], "Alpha_TOP (α)": [], "Alpha_AVG (α)": []
    }

    for compound in raw_data.keys():
        temp_col = f'T_{compound}'
        k_col = compound

        # Interpolated K-values
        k_feed = interpolate_k(combined_df[[temp_col, k_col]].dropna(), T_f)
        k_bottom = interpolate_k(combined_df[[temp_col, k_col]].dropna(), T_b) if compound in bottom_compounds else None
        k_top = interpolate_k(combined_df[[temp_col, k_col]].dropna(), T_t) if compound in distillate_compounds else None

        # Relative Volatility
        k_heavy_feed = interpolate_k(combined_df[[f'T_{heavy_key}', heavy_key]].dropna(), T_f)
        alpha_feed = k_feed / k_heavy_feed if k_heavy_feed != 0 else None
        alpha_bottom = (k_bottom / interpolate_k(combined_df[[f'T_{heavy_key}', heavy_key]].dropna(), T_b)) if k_bottom else None
        alpha_top = (k_top / interpolate_k(combined_df[[f'T_{heavy_key}', heavy_key]].dropna(), T_t)) if k_top else None

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

    results_df = pd.DataFrame(results)

    # ---- FRACTIONS ----
    st.sidebar.header("Input Flow Rates")
    feed_components = ['iC4', 'nC4', 'iC5', 'nC5', 'C6', 'C7', 'C8', 'C9']
    feed_rates = {comp: st.sidebar.slider(f"{comp} Feed Rate", 0.0, 500.0, 50.0) for comp in feed_components}

    top_components = ['iC4', 'nC4', 'iC5', 'nC5']
    top_rates = {comp: st.sidebar.slider(f"{comp} Top Rate", 0.0, 500.0, 50.0) for comp in top_components}

    bottom_components = ['nC4', 'iC5', 'nC5', 'C6', 'C7', 'C8', 'C9']
    bottom_rates = {comp: st.sidebar.slider(f"{comp} Bottom Rate", 0.0, 500.0, 50.0) for comp in bottom_components}

    feed_total = sum(feed_rates.values())
    top_total = sum(top_rates.values())
    bottom_total = sum(bottom_rates.values())

    feed_df = pd.DataFrame.from_dict(feed_rates, orient='index', columns=['Feed (lbmol/h)'])
    feed_df['z (fraction)'] = feed_df['Feed (lbmol/h)'] / feed_total

    top_df = pd.DataFrame.from_dict(top_rates, orient='index', columns=['Top (lbmol/h)'])
    top_df['xd (fraction)'] = top_df['Top (lbmol/h)'] / top_total

    bottom_df = pd.DataFrame.from_dict(bottom_rates, orient='index', columns=['Bottom (lbmol/h)'])
    bottom_df['xb (fraction)'] = bottom_df['Bottom (lbmol/h)'] / bottom_total

    combined_fractions_df = pd.concat([feed_df, top_df, bottom_df], axis=1)

    # ---- DISPLAY RESULTS ----
    final_results_df = pd.concat([results_df, combined_fractions_df], axis=1)
    st.dataframe(final_results_df)

    # ---- DOWNLOAD RESULTS ----
    csv = final_results_df.to_csv().encode('utf-8')
    st.download_button("Download Results", data=csv, file_name="results.csv", mime="text/csv")
