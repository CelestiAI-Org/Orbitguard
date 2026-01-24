import os
import json
import string

def convert():
    json_file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'download.json')
    output_file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'satellites.json')
    
    try:
        with open(json_file_path, 'r') as f:
            raw_data = json.load(f)
        
        # Group CDMs by primary satellite (SAT_1_ID)
        satellites = {}
        
        for cdm in raw_data:
            sat_id = cdm.get("SAT_1_ID", "")
            cdm_id = cdm.get("CDM_ID", "unknown")
            sat1_type = cdm.get("SAT1_OBJECT_TYPE", "")
            
            if sat1_type != "PAYLOAD":
                continue  # Only process PAYLOAD type satellites

            # Create satellite entry if it doesn't exist
            if sat_id not in satellites:
                satellites[sat_id] = {
                    "SAT_1_ID": sat_id,
                    "SAT_1_NAME": cdm.get("SAT_1_NAME", ""),
                    "SAT1_RCS": cdm.get("SAT1_RCS", ""),
                    "SAT_1_EXCL_VOL": cdm.get("SAT_1_EXCL_VOL", ""),
                    "SAT1_OBJECT_TYPE": cdm.get("SAT1_OBJECT_TYPE", ""),
                    "EVENTS": {}
                }
            
            # Add event to satellite's EVENTS dictionary
            satellites[sat_id]["EVENTS"][cdm_id] = {
                "RISK_LEVEL": str(determine_risk_level(float(cdm.get("PC", 0)))), # Should be determined by ML model
                "CREATED": cdm.get("CREATED", ""),
                "TCA": cdm.get("TCA", ""),
                "MIN_RANGE_M": cdm.get("MIN_RNG", ""),
                "PC": cdm.get("PC", ""),
                "SAT_2_ID": cdm.get("SAT_2_ID", ""),
                "SAT_2_NAME": cdm.get("SAT_2_NAME", ""),
                "SAT2_OBJECT_TYPE": cdm.get("SAT2_OBJECT_TYPE", ""),
                "SAT2_RCS": cdm.get("SAT2_RCS", ""),
                "SAT_2_EXCL_VOL": cdm.get("SAT_2_EXCL_VOL", "")
            }
        
        # Convert satellites dict to list format matching Template.json
        satellites_list = list(satellites.values())
        
        # Write to output file
        with open(output_file_path, 'w') as f:
            json.dump(satellites_list, f, indent=4)
        
    except FileNotFoundError:
        print(f"Error: File {json_file_path} not found.")
    except json.JSONDecodeError:
        print(f"Error: File {json_file_path} is not valid JSON.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    

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

convert()