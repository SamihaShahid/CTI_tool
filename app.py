from flask import Flask, render_template, jsonify
import pandas as pd
import requests
from io import StringIO, BytesIO

app = Flask(__name__)

# Corrected GitHub Raw URL
GITHUB_BASE_URL = "https://raw.githubusercontent.com/SamihaShahid/CTI_tool/main/data/"

file_paths = {
    "Stationary Point": "eic_sp.csv",
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
# selective compounds
selected_pol =  [74839, 108883]
df=df[df['pol'].isin(selected_pol)]
df=df.reset_index(drop=True)
# CO, AB, DIS info
df2 = load_data_from_github('eic_sp.csv')

# Read all CSV data files into a dictionary of DataFrames
source_data = {key: load_data_from_github(path) for key, path in file_paths.items()}

@app.route("/")
def index():
    pollutants = df["poln"].unique().tolist()  # Get unique pollutants
    sources = list(file_paths.keys())  # Get available sources
    county = df2['CON'].unique().tolist()
    ab = df2['ABN'].unique().tolist()
    dis = df2['DISN'].unique().tolist()
    return render_template("index.html", pollutants=pollutants, sources=sources, county=county, ab=ab, dis=dis)

@app.route("/data/<pollutant>/<source>")
def get_data(pollutant, source):
    # Get the corresponding pol value
    pol_value = df[df["poln"] == pollutant]["pol"].values

    if len(pol_value) == 0:
        return jsonify([])  # Return empty if no matching poln

    pol_value = pol_value[0]

    # Get source data and filter by pol
    if source in source_data:
        filtered_data = source_data[source][source_data[source]["POL"] == pol_value]
        grouped_data = filtered_data.groupby("EICSUM", as_index=False)[["EMS", "CANCER_TWE", "CHRONIC_TWE", "ACUTE_TWE"]].sum()
        grouped_data = grouped_data.merge(filtered_data[['EICSUMN', 'EICSUM']].drop_duplicates(), on = 'EICSUM', how='left')
        #grouped_data['SUM(EMS)'] = round(grouped_data['SUM(EMS)'],3)
        return jsonify(grouped_data.to_dict(orient="records"))        
    
    return jsonify([])  # Return empty if source not found

@app.route("/details/<pollutant>/<source>/<eicsumn>")
def get_details(pollutant, source, eicsumn):
    # Get the corresponding pol value
    pol_value = df[df["poln"] == pollutant]["pol"].values

    if len(pol_value) == 0:
        return jsonify([])  # Return empty if no matching poln

    pol_value = pol_value[0]

    # Get source data and filter by pol and eicsumn
    if source in source_data:
        filtered_data = source_data[source][(source_data[source]["POL"] == pol_value) & 
                                            (source_data[source]["EICSUMN"] == eicsumn)]
        
        filtered_data = filtered_data[['EICSUMN','EIC', 'EMS']]
        #filtered_data['SUM(EMS)'] =  round(filtered_data['SUM(EMS)'],3)

        # Return detailed rows matching the selected eicsumn
        return jsonify(filtered_data.to_dict(orient="records"))
    
    return jsonify([])  # Return empty if source not found
    

if __name__ == "__main__":
    app.run(debug=True, port=5001)  # Change port if needed











