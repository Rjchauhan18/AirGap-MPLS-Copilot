from backend.api import get_latest_prediction, get_prediction_history

def load_prediction_summary():
    return get_latest_prediction()

def load_prediction_history():
    return get_prediction_history()
