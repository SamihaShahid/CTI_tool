from flask import Flask, render_template, jsonify
import pandas as pd

app = Flask(__name__)

# Load main dataset
file_path = "/Users/samiha/Desktop/EMS_2010_2020/"
df = pd.read_excel(file_path+'/processed_ems_2020_rpt_grp.xlsx', sheet_name="Sheet1")

# Load source data files
file_paths = {
    "Stationary Point": "eic/eic_sp_processed.csv",
    "Stationary Aggregate": "eic/eic_sa.csv",
    "Onroad Mobile": "eic/eic_m.csv",
    "Other Onroad": "eic/eic_o.csv",
    "Natural": "eic/eic_n.csv",
    "Areawide": "eic/eic_a.csv",
}

# Read all data files into a dictionary of DataFrames
source_data = {key: pd.read_csv(path) for key, path in file_paths.items()}

@app.route("/")
def index():
    pollutants = df["poln"].unique().tolist()  # Get unique pollutants
    sources = list(file_paths.keys())  # Get available sources
    return render_template("index.html", pollutants=pollutants, sources=sources)

@app.route("/data/<pollutant>/<source>")
def get_data(pollutant, source):
    # Get the corresponding pol value
    pol_value = df[df["poln"] == pollutant]["pol"].values

    if len(pol_value) == 0:
        return jsonify([])  # Return empty if no matching poln

    pol_value = pol_value[0]

    # Get source data and filter by pol
    if source in source_data:
        filtered_data = source_data[source][source_data[source]["pol"] == pol_value]
        grouped_data = filtered_data.groupby("eicsumn", as_index=False)["SUM(EMS)"].sum()
        grouped_data['SUM(EMS)'] = round(grouped_data['SUM(EMS)'],3)
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
        filtered_data = source_data[source][(source_data[source]["pol"] == pol_value) & 
                                            (source_data[source]["eicsumn"] == eicsumn)]
        
        filtered_data = filtered_data[['eic', 'SUM(EMS)']]
        filtered_data['SUM(EMS)'] =  round(filtered_data['SUM(EMS)'],3)

        # Return detailed rows matching the selected eicsumn
        return jsonify(filtered_data.to_dict(orient="records"))
    
    return jsonify([])  # Return empty if source not found
    

if __name__ == "__main__":
    app.run(debug=True, port=5001)  # Change port if needed











