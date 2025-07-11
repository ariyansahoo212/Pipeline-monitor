from flask import Flask, jsonify
import requests
import threading
import time
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
status = {
    "data_ingestion": "unknown",
    "processing_engine": "unknown",
    "redis": "unknown",
    "last_checked": None
}


health_log = []

def health_check():
    while True:
        record = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        try:
            res = requests.get("http://data_ingestion:5000/health", timeout=2)
            record["data_ingestion"] = res.json().get("status", "down")
        except:
            record["data_ingestion"] = "down"

        try:
            res = requests.get("http://processing_engine:5000/health", timeout=2)
            record["processing_engine"] = res.json().get("status", "down")
        except:
            record["processing_engine"] = "down"

        try:
            import socket
            s = socket.create_connection(("redis", 6379), timeout=2)
            s.close()
            record["redis"] = "up"
        except:
            record["redis"] = "down"

        # ✅ Update current status
        # Update dashboard-friendly status object
        status["last_checked"] = record["timestamp"]
        status.update(record)

        # Store full history
        health_log.append(record)
        if len(health_log) > 100:
            health_log.pop(0)

        if len(health_log) > 100:
            health_log.pop(0)

        time.sleep(10)


@app.route('/dashboard', methods=['GET'])
def dashboard():
    return jsonify(status)

@app.route('/healthlog', methods=['GET'])
def health_log_route():
    return jsonify(health_log)


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})


if __name__ == '__main__':
    threading.Thread(target=health_check, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
