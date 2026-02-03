import flask
import json
import os
import pandas as pd
import spacetrack_client as stc
from pathlib import Path
from flask_cors import CORS
from dotenv import load_dotenv

# Load .env from root directory
root_dir = Path(__file__).parent.parent
b_load = load_dotenv(root_dir / '.env')


app = flask.Flask(__name__)
CORS(app)  # Enable CORS for frontend access

@app.route("/")
def hello():
    return flask.redirect("/health")

@app.route("/health")
def health():
    """Health check endpoint for frontend"""
    return flask.jsonify({"status": "online"})

@app.route("/init")
def satilate_ids():
    """Return data of the satellite IDs available in the dataset"""
    # Resolve to project `app/data/events.json` reliably from this file
    data = stc.process_and_export()
    
    try:
        raw_data = data
        transformed_events = []
        for cdm in raw_data:
            sat1 = cdm.get("SAT_1", {})
            sat2_obj = cdm.get("SAT_2_OBJS", [])
            sat2_obj_count = len(sat2_obj)
            total_sat1_cdms = 0
            if sat2_obj_count >= 1:
                for obj in sat2_obj:
                    total_sat1_cdms += len(obj.get("CDMS", []))
            sat1["SAT2_OBJ_COUNT"] = sat2_obj_count
            sat1["TOTAL_CDMS"] = total_sat1_cdms
            transformed_events.append(sat1)

        
        return flask.Response(json.dumps(transformed_events), mimetype='application/json')
    except FileNotFoundError:
        return flask.jsonify({"error": "Data file not found"}), 404
    except json.JSONDecodeError:
        return flask.jsonify({"error": "Invalid JSON data"}), 500
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500

@app.route("/cdms")
def cdms():
    """Return processed CDM data from events.json"""
    sat_id = flask.request.args.get('sat_id')
    # Resolve to project `app/data/events.json` reliably from this file
    json_file_path = Path(__file__).resolve().parent.parent / 'data' / 'events.json'
    
    try:
        with open(json_file_path, 'r') as f:
            raw_data = json.load(f)
        
        event = []
        for cdm in raw_data:
            id = cdm.get("SAT_1", {}).get("ID", "")
            if str(id) == sat_id:
                event = cdm.get("SAT_2_OBJS", "")
        
        return flask.Response(json.dumps(event), mimetype='application/json')
    except FileNotFoundError:
        return flask.jsonify({"error": "Data file not found"}), 404
    except json.JSONDecodeError:
        return flask.jsonify({"error": "Invalid JSON data"}), 500
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500

    

@app.route("/risk-summary", methods=['GET'])
def risk_summary():
    """Return a summary of risk levels from the latest predictions"""
    id = flask.request.args.get('cdm_id')
    summary = f"Risk summary of CDM ID: {id}"
    return flask.jsonify({"summary": summary})
    

if __name__ == "__main__":
    port = int(os.environ.get('BACKEND_PORT', '8000')) # Default to 8000 if port not set
    app.run(host='0.0.0.0', port=port, debug=True)

# TODO:
# - /cdms needs to process data into json file. Where each CDM is categorized by satellite id (if type == PAYLOAD)
# - /predictions should return json of model predictions from predictions_dashboard.csv
# - Store results of cdms processed history to display to the graph's x-axis