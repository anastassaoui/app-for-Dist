import pandas as pd
import os

def load_data():
    data = {}
    # Loop through all CSV files in the directory
    for file in os.listdir():
        if file.endswith('.csv'):
            # Read each CSV file
            df = pd.read_csv(file)
            # Use the second column name as the compound name
            compound = df.columns[1]
            data[compound] = df
    return data
