import flask
import json
import os
import pandas as pd
from pathlib import Path
from flask_cors import CORS


app = flask.Flask(__name__)
CORS(app)  # Enable CORS for frontend access

@app.route("/")
def hello():
    return flask.jsonify({"status": "online", "message": "Collision Risk AI API"})

@app.route("/health")
def health():
    """Health check endpoint for frontend"""
    return flask.jsonify({"status": "online"})

@app.route("/cdms")
def cdms():
    """Return CDM data transformed for frontend ConjunctionEvent format"""
    json_file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'download.json')
    
    try:
        with open(json_file_path, 'r') as f:
            raw_data = json.load(f)
        
        # Transform raw CDM data to ConjunctionEvent format
        transformed_events = []
        # num = 0
        for cdm in raw_data:
            event = {
                "id": cdm.get("CDM_ID", "unknown"),
                "primaryObject": {
                    "id": cdm.get("SAT_1_ID", ""),
                    "name": cdm.get("SAT_1_NAME", "Unknown"),
                    "type": cdm.get("SAT1_OBJECT_TYPE", "PAYLOAD"),
                    "rcs": cdm.get("SAT1_RCS", "UNKNOWN")
                },
                "secondaryObject": {
                    "id": cdm.get("SAT_2_ID", ""),
                    "name": cdm.get("SAT_2_NAME", "Unknown"),
                    "type": cdm.get("SAT2_OBJECT_TYPE", "PAYLOAD"),
                    "rcs": cdm.get("SAT2_RCS", "UNKNOWN")
                },
                "tca": cdm.get("TCA", ""),
                "missDistance": float(cdm.get("MIN_RNG", 0)),
                "collisionProb": float(cdm.get("PC", 0)),
                "predictedProb": float(cdm.get("PC", 0)),  # Will be updated by ML predictions
                "riskLevel": determine_risk_level(float(cdm.get("PC", 0))),
                "trend": "STABLE",
                "probabilityHistory": [{
                    "timestamp": cdm.get("CREATED", ""),
                    "value": float(cdm.get("PC", 0)),
                    "source": "OBSERVED"
                }],
                "exclusionVolume": f"SAT1: {cdm.get('SAT_1_EXCL_VOL', 'N/A')} km | SAT2: {cdm.get('SAT_2_EXCL_VOL', 'N/A')} km"
            }
            # print(f"Transformed event {num}: {event['id']}, PC: {event['collisionProb']}")
            transformed_events.append(event)
            # num += 1
        
        return flask.jsonify(transformed_events)
    except FileNotFoundError:
        return flask.jsonify({"error": "Data file not found"}), 404
    except json.JSONDecodeError:
        return flask.jsonify({"error": "Invalid JSON data"}), 500
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500

def determine_risk_level(pc):
    """Determine risk level based on collision probability"""
    if pc >= 0.001:  # 1 in 1000
        return "CRITICAL"
    elif pc >= 0.0001:  # 1 in 10,000
        return "HIGH"
    elif pc >= 0.00001:  # 1 in 100,000
        return "MEDIUM"
    else:
        return "LOW"

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
    app.run(host='0.0.0.0', port=5000)