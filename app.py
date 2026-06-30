import re
import uuid
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

AUDIT_LOG = Path("audit_log.jsonl")

def stylometric_score(text: str) -> float:
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    words = re.findall(r'\b\w+\b', text.lower())
    if len(sentences) < 2 or not words:
        return 0.5

    # Low sentence-length variance → uniform → AI-like → score near 1
    sent_lengths = [len(re.findall(r'\b\w+\b', s)) for s in sentences]
    slv = statistics.variance(sent_lengths)
    slv_score = 1 / (1 + slv)

    # Low type-token ratio → repetitive vocabulary → AI-like → score near 1
    ttr_score = 1 - (len(set(words)) / len(words))

    # Low punctuation-count variation across sentences → uniform → AI-like → score near 1
    punct_counts = [len(re.findall(r'[^\w\s]', s)) for s in sentences]
    mean_punct = statistics.mean(punct_counts)
    if mean_punct > 0:
        cv = statistics.stdev(punct_counts) / mean_punct
        punct_score = 1 / (1 + cv)
    else:
        punct_score = 0.5

    return round((slv_score + ttr_score + punct_score) / 3, 4)

def confidence_score(llm_score: float, style_score: float) -> float:
    return round(0.6 * llm_score + 0.4 * style_score, 4)

def attribution_from_confidence(confidence: float) -> str:
    if confidence >= 0.75:
        return "likely_ai"
    if confidence >= 0.40:
        return "uncertain"
    return "likely_human"

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
    llm_score = 0.5        # placeholder — replace with Groq classifier in M5
    style_score = stylometric_score(text)
    confidence = confidence_score(llm_score, style_score)
    attribution = attribution_from_confidence(confidence)

    write_audit({
        "content_id": content_id,
        "creator_id": creator_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "attribution": attribution,
        "confidence": confidence,
        "llm_score": llm_score,
        "style_score": style_score,
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