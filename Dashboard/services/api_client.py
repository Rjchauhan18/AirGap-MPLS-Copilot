import os
import requests

API_BASE = os.getenv("COPILOT_API_URL", "http://localhost:8000")

def _url(path: str) -> str:
    if not path.startswith("/"):
        path = "/" + path
    return f"{API_BASE}{path}"

def get_incidents():
    r = requests.get(_url("/incidents"), timeout=5)
    r.raise_for_status()
    return r.json().get("incidents", [])

def get_status():
    r = requests.get(_url("/status"), timeout=3)
    r.raise_for_status()
    return r.json()

def get_topology(device: str | None = None):
    params = {}
    if device:
        params["device"] = device
    r = requests.get(_url("/topology"), params=params, timeout=5)
    r.raise_for_status()
    return r.json()

def ask_copilot(question: str):
    r = requests.post(_url("/chat"), json={"question": question}, timeout=180)
    r.raise_for_status()
    return r.json()