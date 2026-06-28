import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

def render_line_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str, color: str = "#3498db"):
    fig = px.line(df, x=x_col, y=y_col, title=title)
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color="#FAFAFA",
        uirevision=True,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#333')
    )
    fig.update_traces(line_color=color)
    st.plotly_chart(fig, width="stretch")

def render_area_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str, color: str = "#2ecc71"):
    fig = px.area(df, x=x_col, y=y_col, title=title)
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color="#FAFAFA",
        uirevision=True,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#333')
    )
    fig.update_traces(line_color=color)
    st.plotly_chart(fig, width="stretch")

def render_feature_importance(features: list, scores: list):
    fig = px.bar(x=scores, y=features, orientation='h', title="Feature Importance")
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color="#FAFAFA",
        yaxis={'categoryorder':'total ascending'}
    )
    fig.update_traces(marker_color='#e74c3c')
    st.plotly_chart(fig, width="stretch")
