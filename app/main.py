from pathlib import Path
import json

from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI(
    title="DepoIndex",
    description="AI-powered deposition topic index",
    version="1.0.0",
)

BASE_DIR = Path(__file__).resolve().parent.parent
INDEX_PATH = BASE_DIR / "data" / "final_topic_index.json"
DEMO_PATH = BASE_DIR / "demo" / "index.html"


@app.get("/")
def home():
    return FileResponse(DEMO_PATH)


@app.get("/api/topics")
def get_topics():
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "DepoIndex",
        "topics": len(get_topics()),
    }
