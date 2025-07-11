from flask import Flask, jsonify
import redis
import threading
import json
import time
import uuid
from flask_cors import CORS
import threading
import requests


app = Flask(__name__)
CORS(app)
# In-memory store for processed results
results_store = {}

# Connect to Redis
r = redis.Redis(host='redis', port=6379, db=0)
pubsub = r.pubsub()
pubsub.subscribe('ingestion_stream')


def enrich_and_store(data):
    """Enrich data and store in results_store"""
    data['enriched_at'] = time.time()
    data['validation_score'] = 100  # dummy logic
    result_id = str(uuid.uuid4())
    results_store[result_id] = data
    print(f"Stored result: {result_id}")
    return result_id

@app.route('/results', methods=['GET'])
def list_results():
    return jsonify(results_store)

def listener():
    """Background thread to listen to Redis pub/sub"""
    print("Processing Engine: Waiting for messages...")
    for message in pubsub.listen():
        if message['type'] == 'message':
            try:
                data = json.loads(message['data'].decode('utf-8'))
                enrich_and_store(data)
            except Exception as e:
                print(f"Processing failed: {e}")


@app.route('/results/<result_id>', methods=['GET'])
def get_result(result_id):
    data = results_store.get(result_id)
    if not data:
        return jsonify({'error': 'Result not found'}), 404
    return jsonify(data)


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200




def auto_emoji_ingest():
    while True:
        try:
            # Fetch emoji
            res = requests.get("https://emojihub.yurace.pro/api/random", timeout=5)
            emoji = res.json()

            payload = {
                "value": emoji.get("name", "unknown"),
                "category": emoji.get("category"),
                "group": emoji.get("group"),
                "unicode": emoji.get("unicode", []),
                "timestamp": time.time()
            }

            headers = {
                "X-Source-ID": "emoji-stream"
            }

            # Send to own /ingest API
            requests.post("http://localhost:5000/ingest", json=payload, headers=headers)
            print(f"Auto-ingested emoji: {payload['value']}")
        except Exception as e:
            print(f"❌ Auto-emoji ingestion failed: {e}")
        
        time.sleep(10)  # Wait 10 seconds

# Start the emoji auto-ingestion in a background thread
threading.Thread(target=auto_emoji_ingest, daemon=True).start()


if __name__ == '__main__':
    t = threading.Thread(target=listener, daemon=True)
    t.start()
    app.run(host='0.0.0.0', port=5000)
