import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
import streamlit as st

API_BASE = os.getenv("COPILOT_API_URL", "http://localhost:8000")

class SourcePortAdapter(HTTPAdapter):
    def __init__(self, source_port, *args, **kwargs):
        self.source_port = source_port
        super().__init__(*args, **kwargs)

    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        pool_kwargs['source_address'] = ('0.0.0.0', self.source_port)
        self.poolmanager = PoolManager(
            num_pools=connections, maxsize=maxsize, block=block, **pool_kwargs
        )

@st.cache_resource
def get_http_session():
    """Creates and caches a single persistent HTTP session across Streamlit reruns.
    
    This ensures connection pooling is maintained on one persistent port.
    """
    session = requests.Session()
    # Configure pool to keep up to 10 persistent connections open
    adapter = SourcePortAdapter(source_port=55556, pool_connections=10, pool_maxsize=10)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    return session

def _url(path: str) -> str:
    if not path.startswith("/"):
        path = "/" + path
    return f"{API_BASE}{path}"


def get_incidents():
    session = get_http_session()
    headers = {"Connection": "keep-alive"}
    r = session.get(_url("/incidents"), headers=headers, timeout=5)
    r.raise_for_status()
    return r.json().get("incidents", [])

def get_status():
    session = get_http_session()
    headers = {"Connection": "keep-alive"}
    r = session.get(_url("/status"), headers=headers, timeout=3)
    r.raise_for_status()
    return r.json()

def get_topology(device: str | None = None):
    params = {}
    if device:
        params["device"] = device
    session = get_http_session()
    headers = {"Connection": "keep-alive"}
    r = session.get(_url("/topology"), params=params, headers=headers, timeout=5)
    r.raise_for_status()
    return r.json()

def ask_copilot(question: str):
    session = get_http_session()
    headers = {"Connection": "keep-alive"}
    r = session.post(_url("/chat"), json={"question": question}, headers=headers, timeout=180)
    r.raise_for_status()
    return r.json()