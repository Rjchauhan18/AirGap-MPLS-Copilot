import pandas as pd
import os

TELEMETRY_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'Model', 'sdwan_telemetry_test.csv')

def get_telemetry_data():
    """Reads the telemetry CSV and returns a pandas DataFrame."""
    if not os.path.exists(TELEMETRY_FILE):
        # Return mock data if not found
        return pd.DataFrame({
            "timestamp": pd.date_range(start="2026-06-27", periods=100, freq="min"),
            "avg_latency_ms": [x * 0.1 for x in range(100)],
            "jitter_ms": [x * 0.01 for x in range(100)],
            "packet_loss_pct": [0.0] * 90 + [1.0, 2.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0],
            "rx_bytes_per_sec": [1000] * 100,
            "tx_bytes_per_sec": [1000] * 100,
            "status": ["UP"] * 90 + ["WARNING"] * 5 + ["DOWN"] * 5
        })
    df = pd.read_csv(TELEMETRY_FILE)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def get_latest_metrics():
    df = get_telemetry_data()
    latest = df.iloc[-1]
    return latest.to_dict()
