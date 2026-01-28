import dateutil.parser
import requests

import json
import os

from dotenv import load_dotenv
from pathlib import Path
from ml.runner import MLRunner


# Load .env from root directory
root_dir = Path(__file__).parent.parent.parent
b_load = load_dotenv(root_dir / '.env')

# Constants
SPACE_TRACK_LOGIN_URL = "https://www.space-track.org/ajaxauth/login"
SPACE_TRACK_BASE_URL = "https://www.space-track.org"
IDENTITY = os.getenv("ST_IDENTITY")
PASSWORD = os.getenv("ST_PASSWORD")

ml_runner = MLRunner()

class SpaceTrackClient:
    def __init__(self):
        self.session = requests.Session()
        self.LoggedIn = False

    def login(self):
        payload = {
            "identity": IDENTITY,
            "password": PASSWORD
        }
        try:
            response = self.session.post(SPACE_TRACK_LOGIN_URL, data=payload)
            if response.status_code == 200:
                self.LoggedIn = True
                print("Successfully logged in to Space-Track.")
                return True
            else:
                print(f"Login failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Login error: {str(e)}")
            return False

    def fetch_cdms(self):
        if not self.LoggedIn:
            if not self.login():
                return None

        query_url = f"{SPACE_TRACK_BASE_URL}/basicspacedata/query/class/cdm_public/orderby/CDM_ID%20asc/emptyresult/show"
        print(f"Fetching CDMs from {query_url}...")
        try:
            response = self.session.get(query_url)
            if response.status_code == 200:
                data = response.json()
                print(f"Fetched {len(data)} CDMs.")
                return data
            else:
                print(f"Fetch failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Fetch error: {str(e)}")
            return None

def process_and_export():
    client = SpaceTrackClient()
    raw_data = client.fetch_cdms()
    if not raw_data:
        return None

    # 1. Run ML Prediction (Parallel-ish)
    print("Running ML Inference...")
    ml_results = ml_runner.predict(raw_data)

    # Two-level grouping: SAT_1 -> SAT_2 encounters
    sat1_map = {}  # Key: SAT_1_ID, Value: SAT_1 event object
    sat2_encounters = {}  # Key: "{sat1}_{sat2}_{tca_key}", Value: SAT_2 encounter object

    for cdm in raw_data:
        sat1 = cdm.get('SAT_1_ID')
        sat2 = cdm.get('SAT_2_ID')
        tca_str = cdm.get('TCA')
        created = cdm.get('CREATED')

        if not (sat1 and sat2 and tca_str and created):
            continue

        # Grouping Key Logic (Matches ML Preprocessor)
        try:
            dt = dateutil.parser.parse(tca_str)
            dt_minute = dt.replace(second=0, microsecond=0)
            tca_key = dt_minute.isoformat()
        except Exception:
            tca_key = tca_str

        # Only process PAYLOAD type satellites
        sat1_obj_type = cdm.get('SAT1_OBJECT_TYPE', '')
        if sat1_obj_type != "PAYLOAD":
            continue

        encounter_key = f"{sat1}_{sat2}_{tca_key}"

        # Initialize SAT_1 entry if not exists
        if sat1 not in sat1_map:
            sat1_map[sat1] = {
                "SAT_1": {
                    "ID": int(sat1),
                    "NAME": cdm.get('SAT_1_NAME'),
                    "RCS": cdm.get('SAT1_RCS'),
                    "OBJ_TYP": cdm.get('SAT1_OBJECT_TYPE'),
                    "EXCL_VOL": float(cdm.get('SAT_1_EXCL_VOL'))
                },
                "SAT_2_OBJS": []
            }

        # sat2_map
        # Initialize SAT_2 encounter if not exists
        if encounter_key not in sat2_encounters:
            sat2_obj = {
                "SAT_2": {
                    "ID": int(sat2),
                    "NAME": cdm.get('SAT_2_NAME'),
                    "RCS": cdm.get('SAT2_RCS'),
                    "OBJ_TYP": cdm.get('SAT2_OBJECT_TYPE'),
                    "EXCL_VOL": cdm.get('SAT_2_EXCL_VOL')
                },
                "CDMS": [],
                "TCA": tca_str,
                "AI_RISK_LOG10": None,
                "AI_STATUS": "GRAY",
                "AI_CERTAINTY": 0.0,
                "AI_RISK_PROB": 0.0,
                "MAX_PC": 0.0,
                "MIN_RANGE": 0.0,
                "MSG_COUNT": 0,
                "_sat1_id": sat1  # Internal reference for grouping
            }

            # Merge ML Results if available for this encounter
            if encounter_key in ml_results:
                pred = ml_results[encounter_key]
                sat2_obj["AI_RISK_LOG10"] = pred.get("AI_RISK_LOG10")
                sat2_obj["AI_STATUS"] = pred.get("AI_STATUS", "GRAY")
                sat2_obj["AI_CERTAINTY"] = pred.get("AI_CERTAINTY", 0.0)
                sat2_obj["AI_RISK_PROB"] = pred.get("AI_RISK_PROB", 0.0)

            sat2_encounters[encounter_key] = sat2_obj

        # Parse numeric values
        try:
            min_rng_val = float(cdm.get('MIN_RNG')) if cdm.get('MIN_RNG') else None
        except ValueError:
            min_rng_val = None

        try:
            pc_val = float(cdm.get('PC')) if cdm.get('PC') else 0.0
        except ValueError:
            pc_val = 0.0

        # Add CDM to the encounter
        cdm_item = {
            "CDM_ID": cdm.get('CDM_ID'),
            "CREATED": created,
            "TCA": tca_str,
            "MIN_RNG": min_rng_val,
            "PC": pc_val,
            "RISK_LVL": '' # Placeholder, could be set based on PC or ML
        }
        sat2_encounters[encounter_key]["CDMS"].append(cdm_item)

    # Calculate aggregates and attach SAT_2_OBJS to their SAT_1
    for encounter_key, sat2_obj in sat2_encounters.items():
        # Sort CDMs by CREATED
        sat2_obj["CDMS"].sort(key=lambda x: x['CREATED'])

        # Calculate aggregates
        pcs = [c['PC'] for c in sat2_obj["CDMS"] if c['PC'] is not None]
        sat2_obj["MAX_PC"] = max(pcs) if pcs else 0.0

        rngs = [c['MIN_RNG'] for c in sat2_obj["CDMS"] if c['MIN_RNG'] is not None]
        sat2_obj["MIN_RANGE"] = min(rngs) if rngs else 0.0

        sat2_obj["MSG_COUNT"] = len(sat2_obj["CDMS"])

        # Attach to SAT_1
        sat1_id = sat2_obj.pop("_sat1_id")  # Remove internal reference
        sat1_map[sat1_id]["SAT_2_OBJS"].append(sat2_obj)

    # Sort SAT_2_OBJS by TCA for each SAT_1
    events_list = []
    for sat1_id, event in sat1_map.items():
        event["SAT_2_OBJS"].sort(key=lambda x: x['TCA'])
        events_list.append(event)

    # Sort events by SAT_1 ID
    events_list.sort(key=lambda x: x['SAT_1']['ID'])

    # Export to /data/events.json
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'events.json')

    try:
        with open(output_file, 'w') as f:
            json.dump(events_list, f, indent=4)
        print(f"Exported {len(events_list)} SAT_1 events to {output_file}")
        return events_list
    except Exception as e:
        print(f"Export error: {str(e)}")
        return None