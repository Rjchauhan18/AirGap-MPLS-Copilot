import os
import logging
import joblib 
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class Predictor:
    def __init__(self):
        logger.info("Initializing Stateful Predictive Analytics Engine...")
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.model_path = os.path.join(base_dir, "Model", "predictive_brain.joblib")
        
        self.model = None
        self._load_model()
        
        # In-memory state to calculate rolling windows (size=3) just like the notebook
        self.device_history = {}
        self.window_size = 3

    def _load_model(self):
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                logger.info(f"Successfully loaded ML model from {self.model_path}")
            except Exception as e:
                logger.error(f"Failed to load ML model: {e}")
        else:
            logger.error("ML model not found. Running in fallback mode.")

    def analyze_telemetry(self, telemetry_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.model:
            return None

        device = telemetry_data.get("device", "Unknown-Device")
        site = telemetry_data.get("site", "Unknown-Site")
        metrics = telemetry_data.get("metrics", {})

        if not metrics:
            return None

        # 1. Update Device History for Rolling Windows
        if device not in self.device_history:
            self.device_history[device] = []
            
        self.device_history[device].append(metrics)
        
        # Keep only the last 'window_size' records
        if len(self.device_history[device]) > self.window_size:
            self.device_history[device].pop(0)

        # We need at least 3 samples to match the notebook's rolling window calculation
        if len(self.device_history[device]) < self.window_size:
            logger.debug(f"Buffering telemetry for {device}. Need {self.window_size} samples.")
            return None

        try:
            # 2. Calculate Rolling Features
            df_history = pd.DataFrame(self.device_history[device])
            
            # The exact features your notebook used:
            features = ['avg_latency_ms', 'jitter_ms', 'packet_loss_pct', 'rx_bytes_per_sec']
            
            engineered_features = {}
            for feat in features:
                # Use .get() with a default of 0.0 in case a metric is missing from the payload
                engineered_features[f'{feat}_rolling_mean'] = df_history.get(feat, pd.Series([0.0]*self.window_size)).mean()
                engineered_features[f'{feat}_rolling_std'] = df_history.get(feat, pd.Series([0.0]*self.window_size)).std()

            df_input = pd.DataFrame([engineered_features])

            # 3. Run Inference
            prediction_class = int(self.model.predict(df_input)[0])
            
            # 0.0 means normal in your notebook
            if prediction_class == 0:
                return None

            # 4. Extract Confidence
            confidence = 0.90
            if hasattr(self.model, 'predict_proba'):
                probabilities = self.model.predict_proba(df_input)[0]
                confidence = float(np.max(probabilities))

            # 5. Build Prediction Object
            prediction = {
                "site": site,
                "device": device,
                "confidence": round(confidence, 2),
                "fault_type": "Impending Critical Failure", # Binary target from notebook
                "eta": 20, # Your notebook horizon was approx 15-25 seconds
                "signals": [
                    f"Avg Latency (Rolling Mean): {round(engineered_features.get('avg_latency_ms_rolling_mean', 0), 2)}ms",
                    f"Jitter (Rolling Mean): {round(engineered_features.get('jitter_ms_rolling_mean', 0), 2)}ms"
                ]
            }
            
            logger.info(f"CRITICAL ANOMALY PREDICTED on {device} (Confidence: {prediction['confidence']}).")
            
            # Clear history after generating an alert to prevent spamming
            self.device_history[device] = [] 
            
            return prediction

        except Exception as e:
            logger.error(f"Inference failed for {device}: {str(e)}")
            return None