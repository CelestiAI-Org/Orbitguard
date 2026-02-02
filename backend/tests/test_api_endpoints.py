import requests
import subprocess
import time
import sys
import json

def test_api():
    print("Starting Flask app...")
    # Start the app in the background
    process = subprocess.Popen([sys.executable, 'app.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    try:
        # Give it a moment to startup
        time.sleep(5)
        
        url = 'http://localhost:5000/events'
        print(f"Requesting {url}...")
        
        with requests.get(url, stream=True) as r:
            if r.status_code == 200:
                print("Response received (200 OK)")
                
                # Check if it looks like JSON
                content = r.text
                try:
                    data = json.loads(content)
                    print(f"Successfully parsed JSON. Received {len(data)} events.")
                    if len(data) > 0:
                        first_event = data[0]
                        print("Sample event structure keys:", list(first_event.keys()))
                        if 'SAT_1_ID' in first_event and 'history' in first_event:
                             print("Structure looks correct.")
                        else:
                             print("Structure verification FAILED.")
                    else:
                        print("Warning: Received empty list of events.")
                except json.JSONDecodeError as e:
                    print(f"FAILED to parse JSON: {e}")
                    # print snippet
                    print(content[:500])
            else:
                print(f"Request FAILED: {r.status_code}")
                print(r.text)
                
    except Exception as e:
        print(f"Test Exception: {e}")
        
    finally:
        print("Terminating Flask app...")
        process.terminate()
        process.wait()

if __name__ == "__main__":
    test_api()
