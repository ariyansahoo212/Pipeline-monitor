from flask import Flask, request, jsonify
import redis
import time
import json
from flask_cors import CORS
import threading
import requests

app = Flask(__name__)
CORS(app)
# Redis connection
r = redis.Redis(host='redis', port=6379, db=0)

# Simple in-memory buffer (optional for local fallback)
buffer = []

# Rate limiting tracker
rate_limit_tracker = {}

RATE_LIMIT = 100  # max requests per minute per source

@app.route('/ingest', methods=['POST'])
def ingest():
    source_id = request.headers.get('X-Source-ID')
    if not source_id:
        return jsonify({"error": "Missing X-Source-ID header"}), 400

    now = int(time.time() / 60)  # current minute
    key = f"{source_id}:{now}"
    rate_limit_tracker[key] = rate_limit_tracker.get(key, 0) + 1

    if rate_limit_tracker[key] > RATE_LIMIT:
        return jsonify({"error": "Rate limit exceeded"}), 429

    try:
        data = request.get_json()
        if not isinstance(data, dict):
            raise ValueError("Invalid JSON format")

        # Basic schema validation (you can improve this)
        if 'value' not in data:
            raise ValueError("Missing required 'value' field")

        # Transform example
        data['timestamp'] = time.time()

        # Publish to Redis
        try:
            r.publish('ingestion_stream', json.dumps(data))
        except redis.exceptions.ConnectionError:
            buffer.append(data)  # fallback if Redis fails
            return jsonify({"warning": "Redis unavailable, buffered locally"}), 202

        return jsonify({"status": "success"}), 200

    except ValueError as ve:
        # Permanent error → pretend to send to DLQ
        print(f"Permanent error: {ve}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        # Transient error → retry (we won't retry here but log it)
        print(f"Transient error: {e}")
        return jsonify({"error": "Transient error, please retry"}), 500
    



@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

import threading
import requests

def auto_emoji_ingest():
    while True:
        try:
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

            # IMPORTANT: use service name inside Docker, NOT localhost
            requests.post("http://data_ingestion:5000/ingest", json=payload, headers=headers)
            print(f"✅ Auto-ingested emoji: {payload['value']}")
        except Exception as e:
            print(f"❌ Auto-emoji ingestion failed: {e}")
        
        time.sleep(10)

# Start emoji ingestion background thread
threading.Thread(target=auto_emoji_ingest, daemon=True).start()



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
