import pandas as pd
import os

def load_data():
    data = {}
    folder = 'data' 

    if not os.path.exists(folder):
        raise FileNotFoundError(f"The folder '{folder}' does not exist!")


    for file in os.listdir(folder):
        if file.endswith('.csv'):
            file_path = os.path.join(folder, file)  
            df = pd.read_csv(file_path)
            
            if len(df.columns) < 2:
                raise ValueError(f"File '{file}' must have at least two columns (T and K-values).")

            compound = df.columns[1]  
            data[compound] = df  

    return data
