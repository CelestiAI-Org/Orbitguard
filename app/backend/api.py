import flask
import json
import os
import pandas as pd
import spacetrack_client as stc
from pathlib import Path
from flask_cors import CORS
from dotenv import load_dotenv

# Load .env from root directory
root_dir = Path(__file__).parent.parent.parent
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
    # Resolve to project `app/data/events.json` reliably from this file
    data = stc.process_and_export()
    
    try:
        raw_data = data
        transformed_events = []
        for cdm in raw_data:
            transformed_events.append(cdm.get("SAT_1", ""))
        
        return flask.jsonify(transformed_events)
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



# @app.route("/predictions")
# def predictions():
#     """Return ML model predictions from predictions_dashboard.csv"""
#     results_path = Path(__file__).parent.parent / "results" / "predictions_dashboard.csv"
    
#     try:
#         if not results_path.exists():
#             return flask.jsonify({"error": "No predictions available. Run inference first."}), 404
        
#         df = pd.read_csv(results_path)
#         predictions_data = df.to_dict('records')
#         return flask.jsonify(predictions_data)
#     except Exception as e:
#         return flask.jsonify({"error": str(e)}), 500
    

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