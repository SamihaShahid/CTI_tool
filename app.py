from flask import Flask, render_template, jsonify
import pandas as pd
import requests
from io import StringIO, BytesIO

app = Flask(__name__)

# Corrected GitHub Raw URL
GITHUB_BASE_URL = "https://raw.githubusercontent.com/SamihaShahid/CTI_tool/main/data/"

file_paths = {
    "Stationary Point": "eic_sp_processed.csv",
    "Stationary Aggregate": "eic_sa.csv",
    "Onroad Mobile": "eic_m.csv",
    "Other Onroad": "eic_o.csv",
    "Natural": "eic_n.csv",
    "Areawide": "eic_a.csv",
}

# Load CSV files from GitHub
def load_data_from_github(filename):
    url = GITHUB_BASE_URL + filename
    response = requests.get(url)
    if response.status_code == 200:
        return pd.read_csv(StringIO(response.text))  # Fix: Read from response
    else:
        print(f"Failed to load {filename} from GitHub")
        return pd.DataFrame()

# Load Excel file from GitHub
def load_excel_from_github(filename):
    url = GITHUB_BASE_URL + filename
    response = requests.get(url)
    if response.status_code == 200:
        return pd.read_excel(BytesIO(response.content), sheet_name="Sheet1")  # Fix: Read from response
    else:
        print(f"Failed to load {filename} from GitHub")
        return pd.DataFrame()

# Load main dataset
df = load_excel_from_github("processed_ems_2020_rpt_grp.xlsx")

# Read all CSV data files into a dictionary of DataFrames
source_data = {key: load_data_from_github(path) for key, path in file_paths.items()}

@app.route("/")
def index():
    pollutants = df["poln"].unique().tolist()
    sources = list(file_paths.keys())
    return render_template("index.html", pollutants=pollutants, sources=sources)

@app.route("/data/<pollutant>/<source>")
def get_data(pollutant, source):
    pol_value = df[df["poln"] == pollutant]["pol"].values
    if len(pol_value) == 0:
        return jsonify([])
    
    pol_value = pol_value[0]
    
    if source in source_data:
        filtered_data = source_data[source][source_data[source]["pol"] == pol_value]
        grouped_data = filtered_data.groupby("eicsumn", as_index=False)["SUM(EMS)"].sum()
        grouped_data['SUM(EMS)'] = round(grouped_data['SUM(EMS)'], 3)
        return jsonify(grouped_data.to_dict(orient="records"))

    return jsonify([])

@app.route("/details/<pollutant>/<source>/<eicsumn>")
def get_details(pollutant, source, eicsumn):
    pol_value = df[df["poln"] == pollutant]["pol"].values
    if len(pol_value) == 0:
        return jsonify([])

    pol_value = pol_value[0]

    if source in source_data:
        filtered_data = source_data[source][(source_data[source]["pol"] == pol_value) & 
                                            (source_data[source]["eicsumn"] == eicsumn)]
        filtered_data = filtered_data[['eic', 'SUM(EMS)']]
        filtered_data['SUM(EMS)'] = round(filtered_data['SUM(EMS)'], 3)
        return jsonify(filtered_data.to_dict(orient="records"))

    return jsonify([])

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)
