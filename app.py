import uuid
import json
from datetime import datetime, timezone
from pathlib import Path
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

AUDIT_LOG = Path("audit_log.jsonl")

def write_audit(entry: dict):
    with AUDIT_LOG.open("a") as f:
        f.write(json.dumps(entry) + "\n")

def get_log(n: int = 50) -> list:
    if not AUDIT_LOG.exists():
        return []
    lines = AUDIT_LOG.read_text().splitlines()
    return [json.loads(line) for line in lines[-n:]]

app = Flask(__name__)

@app.route("/")
def home():
    return "Provenance Guard is running."

if __name__ == "__main__":
    app.run(port=5000, debug=True)

@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json()
    text = data.get("text")
    creator_id = data.get("creator_id")

    content_id = str(uuid.uuid4())
    llm_score = 0.5        # placeholder — replace with real signal in M4
    confidence = 0.5       # placeholder — replace with scoring logic in M4
    attribution = "uncertain"

    write_audit({
        "content_id": content_id,
        "creator_id": creator_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "attribution": attribution,
        "confidence": confidence,
        "llm_score": llm_score,
        "status": "classified",
    })

    return jsonify({
        "content_id": content_id,
        "attribution": attribution,
        "confidence": confidence,
        "label": "We're not sure who wrote this.",
    })

@app.route("/log", methods=["GET"])
def log():
    return jsonify({"entries": get_log()})

@app.route("/appeal", methods=["POST"])
def appeal():
    data = request.get_json()
    content_id = data.get("content_id")
    reasoning = data.get("creator_reasoning")

    # Update the content's status and log the appeal (see section 6).
    return jsonify({
        "content_id": content_id,
        "status": "under_review",
        "message": "Your appeal was received and is under review.",
    })
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://",
)