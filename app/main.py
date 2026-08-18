import os
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

APP_NAME = os.getenv("APP_NAME", "Kubernetessss Production Demo")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0.111")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO00")
API_KEY = os.getenv("API_KEY", "demo-secrett")

app = FastAPI(title=APP_NAME, version=APP_VERSION)

# Deliberately in-memory for this teaching MVP.
# In a real production system, application state should live in a database.
items = []


class Item(BaseModel):
    name: str
    description: Optional[str] = None


def require_api_key(x_api_key: Optional[str]):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")


@app.get("/")
def root():
    return {
        "message": "FastAPI running on Kubernetes",
        "app": APP_NAME,
        "version": APP_VERSION,
        "hostname": os.getenv("HOSTNAME", "unknown"),
    }


@app.get("/health")
def health():
    return {"status": "healthy", "version": APP_VERSION}


@app.get("/config")
def config():
    return {
        "app_name": APP_NAME,
        "log_level": LOG_LEVEL,
        "version": APP_VERSION,
        "hostname": os.getenv("HOSTNAME", "unknown"),
    }


@app.get("/items")
def list_items():
    return {"count": len(items), "items": items}


@app.post("/items", status_code=201)
def create_item(item: Item, x_api_key: Optional[str] = Header(default=None)):
    require_api_key(x_api_key)
    record = {
        "id": len(items) + 1,
        "name": item.name,
        "description": item.description,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    items.append(record)
    return record


@app.get("/pod")
def pod_info():
    return {
        "pod_name": os.getenv("HOSTNAME", "unknown"),
        "app_version": APP_VERSION,
        "message": "Refresh this endpoint to see different replica pods.",
    }
