import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

    # --- BACKEND IMPORTS ---
from backend.radar import generate_radar_alerts
from backend.ai_agent import generate_advice
from backend.utils import parse_portfolio_csv
from charts_video.chart import plot_stock

    # Load environment variables
load_dotenv()

    # --- FIX: ticker correction ---
def fix_ticker(ticker):
        if ticker and ".NS" not in ticker:
            return str(ticker).strip().upper() + ".NS"
        return str(ticker).strip().upper()

    # --- CONFIG ---
st.set_page_config(
        page_title="Investor Guardian", 
        layout="wide", 
        initial_sidebar_state="expanded"
    )

    # --- CSS (Styling & Chat Height) ---
st.markdown("""
    <style>
        .stApp { background: #050A14; color: #E6F1FF; }
        .main .block-container { padding: 2rem 3rem !important; }
        [data-testid="stSidebar"] { background-color: #0B132B; border-right: 1px solid rgba(255, 255, 255, 0.05); }
        [data-testid="stDataFrame"] { background: rgba(16, 28, 50, 0.4); border: 1px solid rgba(0, 212, 255, 0.1); border-radius: 8px; }
        .sidebar-title { font-size: 1.2rem; font-weight: 700; color: #FFFFFF; margin-bottom: 20px; }
        .status-badge { padding: 12px; border-radius: 8px; margin-top: 10px; font-size: 0.85rem; font-weight: 500; }
        .status-active { background-color: rgba(26, 71, 49, 0.4); color: #4ade80; border: 1px solid rgba(74, 222, 128, 0.2); }
        .status-feed { background-color: rgba(30, 58, 138, 0.4); color: #60a5fa; border: 1px solid rgba(96, 165, 250, 0.2); }
        .stat-box-inner { background: rgba(16, 28, 50, 0.8); border: 1px solid rgba(0, 212, 255, 0.2); border-radius: 8px; padding: 15px; height: 90px; display: flex; flex-direction: column; justify-content: center; }
        .stat-label { font-size: 0.6rem; color: #8899A6; }
        .stat-value { font-size: 1rem; font-weight: 700; }
        .radar-card { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 15px; text-align: center; height: 140px; display: flex; flex-direction: column; justify-content: center; }
        .section-header { font-size: 0.75rem; font-weight: 700; color: #00D4FF; margin-bottom: 10px; }
        div.stButton > button { margin-top: 10px !important; background: transparent !important; border: 1px solid rgba(0, 212, 255, 0.4) !important; color: #00D4FF !important; font-weight: 600; font-size: 0.7rem; }
        
        /* FIX: Chat height shorter */
        [data-testid="stChatMessageContainer"] {
            max-height: 300px;
            overflow-y: auto;
        }
    </style>
    """, unsafe_allow_html=True)

    # =========================
    # SIDEBAR & DATA LOADING
    # =========================
with st.sidebar:
        st.markdown('<div class="sidebar-title">Investor Profile</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload CSV/Excel", type=["csv", "xlsx"], label_visibility="collapsed")
        
        if uploaded_file is not None:
            # Use the positional parser from utils.py
            data_dict = parse_portfolio_csv(uploaded_file)
            
            if data_dict:
                # Create a clean DataFrame from the dictionary
                st.session_state.portfolio_df = pd.DataFrame(list(data_dict.items()), columns=["Ticker", "Quantity"])
                st.success(f"Linked {len(data_dict)} Assets")
                
                # Reset selection to first item of new file if needed
                if "selected_ticker" not in st.session_state or st.session_state.selected_ticker not in st.session_state.portfolio_df["Ticker"].values:
                    st.session_state.selected_ticker = st.session_state.portfolio_df.iloc[0]["Ticker"]
            else:
                st.error("Empty or invalid data in file.")

        # Determine which data to display in the main table
        if "portfolio_df" in st.session_state:
            portfolio_df = st.session_state.portfolio_df
        else:
            # Fallback Demo Data
            portfolio_df = pd.DataFrame({
                "Ticker": ["RELIANCE", "TCS", "HDFCBANK", "INFY"],
                "Quantity": [15, 10, 50, 25],
                "Avg Price": [2450.00, 3200.50, 1650.20, 1420.00]
            })

        if st.button("Reset to Demo", width="stretch"):
            if "portfolio_df" in st.session_state:
                del st.session_state.portfolio_df
            st.rerun()

        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown('<div class="status-badge status-active">Guardian AI: Active</div>', unsafe_allow_html=True)
        st.markdown('<div class="status-badge status-feed">Market Feed: NSE India</div>', unsafe_allow_html=True)

    # =========================
    # STATE INITIALIZATION
    # =========================
if "selected_ticker" not in st.session_state:
        st.session_state.selected_ticker = portfolio_df.iloc[0]["Ticker"] if not portfolio_df.empty else "RELIANCE"

    # =========================
    # MAIN GRID
    # =========================
left, right = st.columns([2.3, 1], gap="large")

    # --- LEFT SIDE ---
with left:
        st.markdown('<p class="section-header">Network Status</p>', unsafe_allow_html=True)
        s_col1, s_col2, s_col3 = st.columns(3)
        s_col1.markdown('<div class="stat-box-inner"><div class="stat-label">Portfolio</div><div class="stat-value">OPTIMAL</div></div>', unsafe_allow_html=True)
        s_col2.markdown('<div class="stat-box-inner"><div class="stat-label">Alpha Gain</div><div class="stat-value" style="color:#00FFAB">+12,400</div></div>', unsafe_allow_html=True)
        s_col3.markdown('<div class="stat-box-inner"><div class="stat-label">Risk Level</div><div class="stat-value" style="color:#FF4B4B">CRIT_2</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<p class="section-header">Portfolio Inventory</p>', unsafe_allow_html=True)
        
        # Selection logic for the table
        event = st.dataframe(
            portfolio_df, 
            hide_index=True, 
            use_container_width=True,
            on_select="rerun", 
            selection_mode="single-row",
            key="portfolio_table" 
        )

        if event and len(event.selection.rows) > 0:
            selected_index = event.selection.rows[0]
            st.session_state.selected_ticker = portfolio_df.iloc[selected_index]["Ticker"]
            st.rerun() 

        target = fix_ticker(st.session_state.selected_ticker)

        # Radar Alerts
        st.markdown("<div style='margin-bottom:20px'></div>", unsafe_allow_html=True)
        st.markdown('<p class="section-header">Live Terminal</p>', unsafe_allow_html=True)
        alerts = generate_radar_alerts()
        radar_cols = st.columns(3, gap="small")

        for i in range(3):
            if i < len(alerts):
                alert = alerts[i]
                tick = alert.get("stock", "N/A")
                with radar_cols[i]:
                    st.markdown(f'<div class="radar-card"><div style="font-size:0.6rem;">{alert.get("event")}</div><h3>{tick}</h3></div>', unsafe_allow_html=True)
                    if st.button(f"Analyze {tick}", key=f"btn_{tick}", use_container_width=True):
                        st.session_state.selected_ticker = tick
                        st.rerun()

        # Chart Analysis
        st.markdown('<p class="section-header" style="margin-top:2rem;">Deep Neural Analysis</p>', unsafe_allow_html=True)
        st.markdown(f"<h3 style='margin-bottom:10px; color:#E6F1FF'>{target.replace('.NS', '')} - Signal Intelligence</h3>", unsafe_allow_html=True)

        fig = plot_stock(target)
        if fig:
            fig.update_layout(height=500, margin=dict(l=0, r=0, t=20, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#E6F1FF')
            st.plotly_chart(fig, use_container_width=True)

    # --- RIGHT SIDE (CHAT) ---
with right:
        st.markdown('<p class="section-header">Guardian Chat</p>', unsafe_allow_html=True)
        
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": "Ready. Command me."}]

        with st.container(height=300, border=True):
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        prompt = st.chat_input("Enter command...")
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.spinner("Analyzing signals..."):
                advice = generate_advice(target)
                full_reply = f"**{advice.get('decision', 'ANALYSIS COMPLETE')}**\n\n{advice.get('reason', 'Proceed with caution.')}"
                st.session_state.messages.append({"role": "assistant", "content": full_reply})
            st.rerun()