import streamlit as st
import pandas as pd

def render_prediction_table(history: list):
    df = pd.DataFrame(history)
    st.dataframe(df, width="stretch", hide_index=True)
