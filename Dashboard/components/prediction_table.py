import streamlit as st
import pandas as pd

def render_prediction_table(history: list):
    """
    Renders either:
    - legacy prediction rows, OR
    - API incident reports (timestamp, incident_details, copilot_analysis, ...)
    """
    if not history:
        st.info("No incidents/predictions yet.")
        return

    rows = []
    for item in history:
        if isinstance(item, dict) and "incident_details" in item:
            d = item.get("incident_details") or {}
            rows.append(
                {
                    "timestamp": item.get("timestamp"),
                    "incident_id": d.get("incident_id"),
                    "severity": d.get("severity"),
                    "device": d.get("device"),
                    "site": d.get("site"),
                    "fault_type": d.get("fault_type"),
                    "confidence_pct": d.get("confidence"),
                    "eta_min": d.get("eta"),
                    "priority_score": d.get("priority_score"),
                }
            )
        else:
            rows.append(item)

    df = pd.DataFrame(rows)
    st.dataframe(df, width="stretch", hide_index=True)
