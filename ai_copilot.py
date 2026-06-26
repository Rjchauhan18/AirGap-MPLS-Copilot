import time
import pandas as pd
import joblib
import warnings
import collections

warnings.filterwarnings('ignore')

MODEL_PATH = 'Model/predictive_brain.joblib'
TELEMETRY_PATH = 'sdwan_telemetry.csv'
rf_model = joblib.load(MODEL_PATH)

# Buffer to track last 3 latency values to perceive trends
latency_history = collections.deque(maxlen=3)

print("🤖 AI COPILOT UPGRADED: MONITORING TRENDS...")

def get_latest_telemetry():
    try:
        with open(TELEMETRY_PATH, 'r') as f:
            lines = f.readlines()
            if len(lines) > 1:
                headers = lines[0].strip().split(',')
                last_line = lines[-1].strip().split(',')
                return dict(zip(headers, last_line))
    except: return None
    return None

last_timestamp = None

while True:
    data = get_latest_telemetry()
    if data and data['timestamp'] != last_timestamp:
        last_timestamp = data['timestamp']
        latency = float(data['avg_latency_ms'])
        
        # Add to history
        latency_history.append(latency)
        
        # If we have enough history, create a 'trend' feature
        if len(latency_history) == 3:
            trend = latency_history[-1] - latency_history[0] # How much it changed in 15s
            # Pass trend to the model instead of raw latency
            live_features = pd.DataFrame({'avg_latency_ms': [trend], 'jitter_ms': [float(data['jitter_ms'])]})
            prediction = rf_model.predict(live_features)[0]
            
            status_map = {0: "🟢 HEALTHY", 1: "🟡 WARNING", 2: "🔴 CRITICAL"}
            print(f"[{data['timestamp']}] Trend: {trend:>6.3f}ms | Status: {status_map[prediction]}")
    
    time.sleep(2)