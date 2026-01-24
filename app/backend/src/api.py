import flask
import json
import os
import pandas as pd
from pathlib import Path
from flask_cors import CORS
from dotenv import load_dotenv

# Load .env from root directory
root_dir = Path(__file__).parent.parent.parent.parent
b_load = load_dotenv(root_dir / '.env')


app = flask.Flask(__name__)
CORS(app)  # Enable CORS for frontend access

@app.route("/")
def hello():
    return flask.jsonify({"status": "online", "message": "Collision Risk AI API"})

@app.route("/health")
def health():
    """Health check endpoint for frontend"""
    return flask.jsonify({"status": "online"})

@app.route("/init")
def satilate_ids():
    """Return data of the satellite IDs available in the dataset"""
    json_file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'satellites.json')
    
    try:
        with open(json_file_path, 'r') as f:
            raw_data = json.load(f)
        
        transformed_events = []
        for cdm in raw_data:
            event = {
                "id": cdm.get("SAT_1_ID", ""),
                "name": cdm.get("SAT_1_NAME", ""),
                "type": cdm.get("SAT1_OBJECT_TYPE", ""),
                "rcs": cdm.get("SAT1_RCS", ""),
                "excl_vol": cdm.get("SAT_1_EXCL_VOL", "")
            }
            transformed_events.append(event)
        
        return flask.jsonify(transformed_events)
    except FileNotFoundError:
        return flask.jsonify({"error": "Data file not found"}), 404
    except json.JSONDecodeError:
        return flask.jsonify({"error": "Invalid JSON data"}), 500
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500

@app.route("/cdms")
def cdms():
    """Return processed CDM data from satellites.json"""
    sat_id = flask.request.args.get('sat_id')
    json_file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'satellites.json')

    # Should be using a DB for this in production

    cdms = []

    try:
        with open(json_file_path, 'r') as f:
            events = json.load(f)
        for cdm in events:
            if sat_id == cdm["SAT_1_ID"]:
                events_dict = cdm.get("EVENTS", {})
                # TODO: Find better way to structure this. Needs less indentation
                for event_id, event_data in events_dict.items():
                    event_entry = {
                        "CDM_ID": event_id,
                        "RISK_LEVEL": event_data.get("RISK_LEVEL", ""),
                        "CREATED": event_data.get("CREATED", ""),
                        "TCA": event_data.get("TCA", ""),
                        "MIN_RANGE_M": event_data.get("MIN_RANGE_M", ""),
                        "PC": event_data.get("PC", ""),
                        "SAT_2_ID": event_data.get("SAT_2_ID", ""),
                        "SAT_2_NAME": event_data.get("SAT_2_NAME", ""),
                        "SAT2_OBJECT_TYPE": event_data.get("SAT2_OBJECT_TYPE", ""),
                        "SAT2_RCS": event_data.get("SAT2_RCS", ""),
                        "SAT_2_EXCL_VOL": event_data.get("SAT_2_EXCL_VOL", "")
                    }
                    cdms.append(event_entry)
        return flask.jsonify(cdms)
    
    except FileNotFoundError:
        return flask.jsonify({"error": "Processed CDM data not found. Run data conversion first."}), 404
    except json.JSONDecodeError:
        return flask.jsonify({"error": "Invalid JSON data in processed CDM file."}), 500
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500



@app.route("/predictions")
def predictions():
    """Return ML model predictions from predictions_dashboard.csv"""
    results_path = Path(__file__).parent.parent / "results" / "predictions_dashboard.csv"
    
    try:
        if not results_path.exists():
            return flask.jsonify({"error": "No predictions available. Run inference first."}), 404
        
        df = pd.read_csv(results_path)
        predictions_data = df.to_dict('records')
        return flask.jsonify(predictions_data)
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500
    

@app.route("/risk-summary", methods=['GET'])
def risk_summary():
    """Return a summary of risk levels from the latest predictions"""
    id = flask.request.args.get('cdm_id')
    summary = f"Risk summary of CDM ID: {id}"
    return flask.jsonify({"summary": summary})
    

if __name__ == "__main__":
    port = int(os.environ.get('BACKEND_PORT', 5000)) # Default to 5000 if port not set
    app.run(host='0.0.0.0', port=port)

# TODO:
# - /cdms needs to process data into json file. Where each CDM is categorized by satellite id (if type == PAYLOAD)
# - /predictions should return json of model predictions from predictions_dashboard.csv
# - Store results of cdms processed history to display to the graph's x-axis