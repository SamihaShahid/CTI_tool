from flask import Flask, render_template, jsonify
import pandas as pd

app = Flask(__name__)

# Load main dataset
file_path = "processed_ems_2020_rpt_grp.xlsx"
df = pd.read_excel(file_path, sheet_name="Sheet1")

# Load source data files
file_paths = {
    "SP": "eic/eic_sp_processed.csv",
    "SA": "eic/eic_sa.csv",
    "O": "eic/eic_o.csv",
    "M": "eic/eic_m.csv",
    "N": "eic/eic_n.csv",
    "A": "eic/eic_a.csv",
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
        filtered_data = source_data[source][source_data[source]["pol"] == pol_value].to_dict(orient="records")
        return jsonify(filtered_data)
    
    return jsonify([])  # Return empty if source not found

if __name__ == "__main__":
    app.run(debug=True, port=5001)  # Change port if needed
