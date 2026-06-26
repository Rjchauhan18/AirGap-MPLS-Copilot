import time
import pandas as pd
import numpy as np
import joblib
import os
from collections import deque
import warnings

warnings.filterwarnings('ignore')

# Configuration
TELEMETRY_FILE = "Model/sdwan_telemetry_test.csv"
MODEL_FILE = "Model/predictive_brain.joblib"
WINDOW_SIZE = 3
CONFIDENCE_THRESHOLD = 0.65  # 65% probability triggers an early warning

print("=================================================================")
print("🧠 AIR-GAPPED PREDICTIVE NOC COPILOT - INFERENCE ENGINE STARTED")
print("=================================================================")

# Load the trained ML Model
if not os.path.exists(MODEL_FILE):
    print(f"❌ Error: Model {MODEL_FILE} not found. Please run the Jupyter notebook first.")
    exit(1)

model = joblib.load(MODEL_FILE)
print(f"✅ Loaded Predictive Brain (RandomForest) from {MODEL_FILE}")
print(f"📡 Tailing live telemetry from {TELEMETRY_FILE}...\n")

# Setup rolling memory buffers for Feature Engineering
history = {
    'avg_latency_ms': deque(maxlen=WINDOW_SIZE),
    'jitter_ms': deque(maxlen=WINDOW_SIZE),
    'packet_loss_pct': deque(maxlen=WINDOW_SIZE),
    'rx_bytes_per_sec': deque(maxlen=WINDOW_SIZE)
}

def tail_file(filename):
    """Generator to continuously tail the CSV file."""
    with open(filename, 'r') as f:
        # Move to the end of the file
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue
            yield line

# Start Live Inference Loop
for line in tail_file(TELEMETRY_FILE):
    # Parse the CSV line
    parts = line.strip().split(',')
    
    # Skip headers or incomplete lines
    if len(parts) < 10 or parts[0] == "timestamp":
        continue
        
    timestamp = parts[0]
    
    try:
        # Extract base metrics
        latency = float(parts[1])
        jitter = float(parts[2])
        loss = float(parts[3])
        rx_bytes = float(parts[4])
        ospf_state = int(parts[7])
        
        # If OSPF is already down, the failure has occurred. Skip prediction.
        if ospf_state == 0 or loss == 100.0:
            print(f"[{timestamp}] 🚨 CRITICAL: Network Outage Detected. Routing Protocols DOWN.")
            continue
            
        # Update rolling windows
        history['avg_latency_ms'].append(latency)
        history['jitter_ms'].append(jitter)
        history['packet_loss_pct'].append(loss)
        history['rx_bytes_per_sec'].append(rx_bytes)
        
        # We need a full window to make an accurate prediction
        if len(history['avg_latency_ms']) == WINDOW_SIZE:
            
            # Calculate rolling features
            features = []
            for metric in ['avg_latency_ms', 'jitter_ms', 'packet_loss_pct', 'rx_bytes_per_sec']:
                arr = np.array(history[metric])
                features.append(np.mean(arr)) # rolling_mean
                features.append(np.std(arr) if len(arr)>1 else 0.0) # rolling_std
                
            # Reshape for sklearn
            X_live = np.array(features).reshape(1, -1)
            
            # Predict Probability of future failure
            failure_prob = model.predict_proba(X_live)[0][1]
            
            # Output normal telemetry
            if failure_prob < CONFIDENCE_THRESHOLD:
                 print(f"[{timestamp}] 🟢 Network Stable | Outage Risk: {failure_prob*100:.1f}%")
            
            # TRIGGER EARLY WARNING
            else:
                # Dynamic signal root-cause string formulation
                rolling_lat = np.mean(history['avg_latency_ms'])
                rolling_jit = np.mean(history['jitter_ms'])
                rolling_loss = np.mean(history['packet_loss_pct'])
                
                trigger_signals = []
                if rolling_lat > 25.0: trigger_signals.append(f"Latency Drift ({rolling_lat:.1f}ms)")
                if rolling_jit > 5.0:  trigger_signals.append(f"Elevated Jitter ({rolling_jit:.1f}ms)")
                if rolling_loss > 0.0: trigger_signals.append(f"Packet Loss ({rolling_loss:.1f}%)")
                
                # Fallback text if variations are caught strictly via standard deviation matrices
                if not trigger_signals:
                    trigger_signals.append("Statistical variance in Telemetry Trend Matrix")
                
                signal_output_string = " + ".join(trigger_signals)
                
                print(f"\n=======================================================")
                print(f"⚠️  PREDICTIVE ALERT TRIGGERED at {timestamp}")
                print(f"=======================================================")
                print(f"-> FORECAST: Core Link Outage predicted within 15-30s.")
                print(f"-> CONFIDENCE: {failure_prob*100:.1f}%")
                print(f"-> SIGNALS: {signal_output_string}")
                print(f"-> ACTION REQUIRED: Shift traffic to secondary MPLS LSP immediately.")
                print(f"=======================================================\n")
                
    except ValueError:
        # Handle un-parseable data gracefully
        pass