import pandas as pd

def load_sensor_data(path):
    if path.endswith("xlsx"):
        return pd.read_excel(path)
    return pd.read_csv(path)
