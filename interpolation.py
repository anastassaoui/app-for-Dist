from scipy.interpolate import interp1d

def interpolate_k(df, temp):
    # Automatically detect temperature and K-value columns
    temp_col = df.columns[0]  # First column is temperature
    k_col = df.columns[1]     # Second column is K-value

    # Ensure temperature is within bounds
    if temp < df[temp_col].min() or temp > df[temp_col].max():
        raise ValueError(f"Temperature {temp} out of bounds ({df[temp_col].min()} - {df[temp_col].max()})")

    # Perform robust cubic spline interpolation
    interp_func = interp1d(df[temp_col], df[k_col], kind='cubic', fill_value='extrapolate')
    return interp_func(temp)
