import json
import time
import spacetrack_client as stc
from flask import Flask, Response, stream_with_context
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Enable CORS for all routes
    
client = stc.SpaceTrackClient()

@app.route('/events')
def events():
    def generate():
        # Ideally we fetch and stream, but since we need to group/sort first, we have to process all data.
        # So we process first, then stream the result locally.
        start_time = time.time()
        print("Received request for /events")
        data = client.process_and_export()
        
        if not data:
            yield json.dumps({"error": "Failed to fetch or process data"})
            return

        yield '['
        first = True
        for event in data:
            if not first:
                yield ','
            else:
                first = False
            yield json.dumps(event)
        yield ']'
        
        duration = time.time() - start_time
        print(f"Request finished in {duration:.2f}s")

    return Response(stream_with_context(generate()), content_type='application/json')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
