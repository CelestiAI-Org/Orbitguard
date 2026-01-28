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

    events_map = {}

    for cdm in raw_data:
        sat1 = cdm.get('SAT_1_ID')
        sat2 = cdm.get('SAT_2_ID')
        tca_str = cdm.get('TCA')
        created = cdm.get('CREATED')

        if not (sat1 and sat2 and tca_str and created):
            continue

        # Grouping Key Logic (Matches ML Preprocessor)
        try:
            # Parse TCA, floor to minute, isoformat
            # Standardize format to handle potentially different inputs
            dt = dateutil.parser.parse(tca_str)
            dt_minute = dt.replace(second=0, microsecond=0)
            tca_key = dt_minute.isoformat() # e.g. 2026-01-26T16:18:00
        except Exception:
            tca_key = tca_str # Fallback

        key = f"{sat1}_{sat2}_{tca_key}"

        if key not in events_map:
            sat1_info = {}
            events_map[key] = {
                "ID": key,
                "SAT_1_ID": int(sat1),
                "SAT_1_NAME": cdm.get('SAT_1_NAME'),
                "SAT_2_ID": int(sat2),
                "SAT_2_NAME": cdm.get('SAT_2_NAME'),
                "TCA": tca_str, # Keep original string for display
                "HISTORY": [],
                # Initialize AI fields (will overwrite if exists)
                "AI_RISK_LOG10": None,
                "AI_STATUS": "GRAY",
                "AI_CERTAINTY": 0.0
            }

            # Merge ML Results if available for this key
            if key in ml_results:
                pred = ml_results[key]
                events_map[key].update(pred)

        # Prepare history item
        min_rng = cdm.get('MIN_RNG')
        pc = cdm.get('PC')

        try:
            min_rng_val = float(min_rng) if min_rng else None
        except ValueError:
            min_rng_val = None

        try:
            pc_val = float(pc) if pc else 0.0
        except ValueError:
            pc_val = 0.0

        history_item = {
            "CDM_ID": cdm.get('CDM_ID'),
            "CREATED": created,
            "MIN_RNG": min_rng_val,
            "PC": pc_val,
            "EMERGENCY_REPORTABLE": cdm.get('EMERGENCY_REPORTABLE')
        }

        events_map[key]["HISTORY"].append(history_item)

    events_list = []
    for key, event in events_map.items():
        # Sort history by CREATED
        event["HISTORY"].sort(key=lambda x: x['CREATED'])

        # Calculate aggregates
        pcs = [h['PC'] for h in event["HISTORY"] if h['PC'] is not None]
        max_pc = max(pcs) if pcs else None

        rngs = [h['MIN_RNG'] for h in event["HISTORY"] if h['MIN_RNG'] is not None]
        min_range = min(rngs) if rngs else None

        event["MAX_PC"] = max_pc
        event["MIN_RANGE"] = min_range
        event["MSG_COUNT"] = len(event["HISTORY"])

        events_list.append(event)

    events_list.sort(key=lambda x: x['TCA'])

    # 5. Export to /data/events.json
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'events.json')

    try:
        with open(output_file, 'w') as f:
            json.dump(events_list, f, indent=4)
        print(f"Exported {len(events_list)} events to {output_file}")
        return events_list
    except Exception as e:
        print(f"Export error: {str(e)}")
        return None