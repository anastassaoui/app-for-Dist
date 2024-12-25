import pandas as pd
import os

def load_data():
    data = {}
    folder = 'data'  # Folder containing the CSV files

    # Ensure the folder exists
    if not os.path.exists(folder):
        raise FileNotFoundError(f"The folder '{folder}' does not exist!")

    # Loop through all CSV files in the 'data' folder
    for file in os.listdir(folder):
        if file.endswith('.csv'):
            # Read each CSV file
            file_path = os.path.join(folder, file)  # Full path to the file
            df = pd.read_csv(file_path)
            
            # Use the second column name as the compound name
            if len(df.columns) < 2:
                raise ValueError(f"File '{file}' must have at least two columns (T and K-values).")

            compound = df.columns[1]  # Second column as compound name
            data[compound] = df  # Store the DataFrame in the dictionary

    return data
