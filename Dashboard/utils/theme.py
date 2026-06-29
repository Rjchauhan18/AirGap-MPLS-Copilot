import streamlit as st

def apply_theme():
    st.markdown("""
    <style>
    /* Global Typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Animated Dynamic Background */
    .stApp {
        background: radial-gradient(circle at 15% 50%, rgba(15, 23, 42, 1), rgba(11, 15, 25, 1) 50%);
        background-attachment: fixed;
        color: #e2e8f0;
    }
    
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: 
            radial-gradient(circle at 80% 20%, rgba(56, 189, 248, 0.05) 0%, transparent 40%),
            radial-gradient(circle at 20% 80%, rgba(74, 222, 128, 0.05) 0%, transparent 40%);
        pointer-events: none;
        z-index: -1;
    }

    /* Sidebar Enhancement */
    section[data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.8) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    section[data-testid="stSidebar"] hr {
        border-bottom-color: rgba(255,255,255,0.1);
    }
    
    /* Headers Customization */
    h1 {
        font-weight: 700 !important;
        background: linear-gradient(90deg, #f8fafc, #94a3b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1.5rem !important;
    }
    h2, h3 {
        color: #f1f5f9 !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em;
    }
    
    /* Modern Glassmorphic Metric Cards */
    .metric-card {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-top: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: -100%;
        width: 50%; height: 100%;
        background: linear-gradient(to right, transparent, rgba(255,255,255,0.03), transparent);
        transform: skewX(-20deg);
        transition: 0.5s;
    }
    
    .metric-card:hover::before {
        left: 150%;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    
    .metric-title {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 8px;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        line-height: 1.2;
        font-family: 'Inter', sans-serif;
    }
    
    .metric-description {
        font-size: 0.85rem; 
        color: #cbd5e1; 
        margin-top: 12px;
        background: rgba(0,0,0,0.2);
        padding: 6px 12px;
        border-radius: 6px;
        display: inline-block;
    }
    
    /* Glowing Status Colors */
    .color-healthy { color: #4ade80; text-shadow: 0 0 15px rgba(74, 222, 128, 0.4); }
    .color-warning { color: #fbbf24; text-shadow: 0 0 15px rgba(251, 191, 36, 0.4); }
    .color-critical { color: #f87171; text-shadow: 0 0 15px rgba(248, 113, 113, 0.4); }
    .color-prediction { color: #38bdf8; text-shadow: 0 0 15px rgba(56, 189, 248, 0.4); }
    
    /* Streamlit Alert/Info Boxes Upgrade */
    div[data-testid="stAlert"] {
        background-color: rgba(30, 41, 59, 0.5) !important;
        backdrop-filter: blur(8px) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
        color: #e2e8f0 !important;
    }
    
    /* Streamlit Button Upgrade */
    button[kind="secondary"] {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 14px 0 rgba(37, 99, 235, 0.39) !important;
        transition: all 0.2s ease-in-out !important;
    }
    button[kind="secondary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.23) !important;
    }
    
    /* Inputs & Selectboxes */
    div[data-baseweb="select"] > div, input[type="text"] {
        background-color: rgba(15, 23, 42, 0.6) !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: #f1f5f9 !important;
        transition: border 0.3s ease;
    }
    div[data-baseweb="select"] > div:hover, input[type="text"]:focus {
        border-color: #38bdf8 !important;
    }
    
    /* Dataframes */
    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Hide Streamlit Clutter */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {background: transparent !important;}
    
    /* Minimal Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: transparent; 
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(148, 163, 184, 0.2); 
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(148, 163, 184, 0.5); 
    }
    </style>
    """, unsafe_allow_html=True)
