import streamlit as st
import pandas as pd
import os
import time
import datetime
from dotenv import load_dotenv

# --- BACKEND IMPORTS ---
try:
    from backend.radar import generate_radar_alerts
    from backend.ai_agent import generate_advice
    from backend.utils import parse_portfolio_csv
    from charts_video.chart import plot_stock, generate_briefing_video
except ImportError as e:
    st.error(f"Mapping Error: {e}. Check folder structure!")

load_dotenv()

# --- FIX: ticker correction ---
def fix_ticker(ticker):
    if not ticker: return "RELIANCE.NS"
    # Remove any stray spaces or special characters
    t = str(ticker).strip().upper()
    # Ensure it only has ONE .NS suffix
    t = t.replace(".NS", "") 
    return f"{t}.NS"

# --- CONFIG ---
st.set_page_config(page_title="Investor Guardian", layout="wide", initial_sidebar_state="expanded")

# --- CSS (Themed Sidebar, Large Boxes & Hover Effects) ---
st.markdown("""
    <style>
/* Target ALL buttons inside radar columns */
div.stButton {
    margin-top: 20px !important;
}

/* Keep your styling */
div.stButton > button {
    background: rgba(0, 212, 255, 0.05) !important;
    border: 1px solid rgba(0, 212, 255, 0.3) !important;
    color: #00D4FF !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    transition: all 0.3s ease !important;
}

div.stButton > button:hover {
    background: rgba(0, 212, 255, 0.15) !important;
    border: 1px solid #00D4FF !important;
    box-shadow: 0 0 15px rgba(0, 212, 255, 0.2);
    transform: translateY(-2px);
}
</style>
""", unsafe_allow_html=True)
st.markdown("""
    <style>
        /* Make the invisible button fill the card */
        div.stButton > button.radar-btn {
            background-color: transparent !important;
            border: none !important;
            padding: 0 !important;
            color: inherit !important;
            text-align: left !important;
            width: 100% !important;
            height: 100% !important;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
        .guardian-header-container {
            display: flex;
            align-items: center;
            border-left: 3px solid #00D4FF; 
            padding-left: 12px;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
        }
        
        .guardian-header-text {
            font-size: 0.9rem;
            font-weight: 800;
            color: #00D4FF; 
            text-shadow: 0 0 8px rgba(0, 212, 255, 0.4); 
            letter-spacing: 1.5px;
            text-transform: uppercase;
        }

        .header-pulse {
            height: 6px;
            width: 6px;
            background-color: #00D4FF;
            border-radius: 50%;
            display: inline-block;
            margin-right: 10px;
            box-shadow: 0 0 8px #00D4FF;
            animation: pulse-ring 2s infinite;
        }
            
        @keyframes pulse-ring {
            0% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.3; transform: scale(0.8); }
            100% { opacity: 1; transform: scale(1); }
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
        /* UNIFIED BOX STYLING (Network Status & Opportunity Radar) */
        .stat-box-inner, .radar-card {
            background: rgba(16, 28, 50, 0.7); 
            border: 1px solid rgba(0, 212, 255, 0.15);
            border-radius: 12px;
            padding: 20px;
            
            /* FIXED DIMENSIONS */
            height: 140px; /* Adjust this value to your preference */
            width: 100%;   /* Ensures they fill the column width equally */
            
            display: flex;
            flex-direction: column;
            justify-content: center; /* Vertical Center */
            align-items: flex-start; /* Horizontal Left Align */
            
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
            box-sizing: border-box;
            overflow: hidden; /* Prevents text from breaking the box */
        }

        /* UNIFIED HOVER */
        .stat-box-inner:hover, .radar-card:hover {
            transform: translateY(-5px);
            border: 1px solid rgba(0, 212, 255, 0.5);
            background: rgba(16, 28, 50, 0.9);
            box-shadow: 0 10px 20px rgba(0, 212, 255, 0.15);
        }

        /* Typography consistency */
        .stat-label { font-size: 0.65rem; color: #8899A6; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; }
        .stat-value { font-size: 1.15rem; font-weight: 700; color: #FFFFFF; }
        .radar-type { font-size: 0.6rem; color: #00D4FF; font-weight: 700; text-transform: uppercase; margin-bottom: 4px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
        .portfolio-header {
            font-size: 1rem;
            font-weight: 800;
            color: #00D4FF; 
            text-shadow: 0 0 10px rgba(0, 212, 255, 0.3); 
            letter-spacing: 1.5px;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            border-left: 3px solid #00D4FF; 
            padding-left: 12px;
            text-transform: uppercase;
        }
        
        .live-dot {
            height: 8px;
            width: 8px;
            background-color: #00D4FF;
            border-radius: 50%;
            display: inline-block;
            margin-right: 12px;
            box-shadow: 0 0 8px #00D4FF;
            animation: blink 2s infinite;
        }
            
        @keyframes blink {
            0% { opacity: 1; }
            50% { opacity: 0.3; }
            100% { opacity: 1; }
        }

        .stApp { background: #050A14; color: #E6F1FF; }
        [data-testid="stSidebar"] { background-color: #0B132B; border-right: 1px solid rgba(0, 212, 255, 0.1); }
        
        .persona-card {
            background: rgba(16, 28, 50, 0.6); 
            border: 1px solid rgba(0, 212, 255, 0.2);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .persona-name { font-size: 1.2rem; font-weight: 700; color: #FFFFFF; margin-bottom: 5px; }
        .sidebar-header { font-size: 0.7rem; font-weight: 700; color: #00D4FF; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 15px; }
        
        .status-badge { padding: 10px; border-radius: 6px; margin-top: 8px; font-size: 0.8rem; border: 1px solid rgba(255,255,255,0.05); }
        .status-active { background: rgba(74, 222, 128, 0.1); color: #4ade80; border: 1px solid rgba(74, 222, 128, 0.2); }
        
        div.stButton > button { background: transparent !important; border: 1px solid rgba(0, 212, 255, 0.4) !important; color: #00D4FF !important; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# =========================
# DATA INITIALIZATION
# =========================
# =========================
# DATA & STATE INITIALIZATION
# ==========================================
# 1. DATA INITIALIZATION (CRITICAL: MUST BE AT TOP)
# ==========================================
# ==========================================
# 1. DATA INITIALIZATION (CRITICAL: MUST BE AT TOP)
# ==========================================
demo_df = pd.DataFrame({"Ticker": ["RELIANCE", "TCS", "HDFCBANK", "INFY"], "Quantity": [15, 10, 50, 25]})
demo_dict = {"RELIANCE.NS": 15, "TCS.NS": 10, "HDFCBANK.NS": 50, "INFY.NS": 25}

# Initialize Session State variables if they don't exist
if "portfolio_df" not in st.session_state:
    st.session_state.portfolio_df = demo_df
    st.session_state.portfolio_dict = demo_dict

if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = st.session_state.portfolio_df.iloc[0]["Ticker"]

# --- THE REACTIVE FIX ---
# Define these locally every rerun so they catch changes from buttons below
portfolio_df = st.session_state.portfolio_df
current_portfolio = st.session_state.portfolio_dict
target_ticker = fix_ticker(st.session_state.selected_ticker)

# Ticker Change Logic: Reset Chat if the Radar switched the focus
if "current_focus" not in st.session_state:
    st.session_state.current_focus = st.session_state.selected_ticker

if st.session_state.current_focus != st.session_state.selected_ticker:
    st.session_state.messages = [{"role": "assistant", "content": f"Neural Feed Switched. Analyzing {st.session_state.selected_ticker}..."}]
    st.session_state.current_focus = st.session_state.selected_ticker
# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown('<div class="sidebar-header">Identity Matrix</div>', unsafe_allow_html=True)
    st.markdown(f"""<div class="persona-card"><div class="persona-name">Retail Hero</div><div style="font-size: 0.7rem; color: #8899A6;">Active Session: Guardian-01</div></div>""", unsafe_allow_html=True)
    
    risk_lvl = st.select_slider("Risk Appetite", options=["Conservative", "Balanced", "Aggressive"], value="Balanced", key="risk_lvl")

    st.markdown('<div style="margin: 25px 0; height: 1px; background: linear-gradient(90deg, rgba(0,212,255,0) 0%, rgba(0,212,255,0.4) 50%, rgba(0,212,255,0) 100%);"></div>', unsafe_allow_html=True)

    if "uploader_key" not in st.session_state: st.session_state.uploader_key = 0
    uploaded_file = st.file_uploader("Upload Portfolio", type=["csv", "xlsx"], key=f"up_{st.session_state.uploader_key}")
    
    if uploaded_file:
        if "last_processed_file" not in st.session_state or st.session_state.last_processed_file != uploaded_file.name:
            with st.spinner("🧬 Synchronizing Portfolio..."):
                data = parse_portfolio_csv(uploaded_file)
                if data:
                    st.session_state.portfolio_df = pd.DataFrame(list(data.items()), columns=["Ticker", "Quantity"])
                    st.session_state.portfolio_dict = data
                    st.session_state.last_processed_file = uploaded_file.name
                    st.toast(f"✅ Connection Established: {len(data)} Assets Linked", icon="🛡️")
                    st.success(f"Linked {len(data)} Assets to Guardian Node")
                    st.session_state.selected_ticker = list(data.keys())[0].replace(".NS", "")
                    time.sleep(1) 
                    st.rerun()
    
    if st.button("Reset to Demo"):
        for k in ["portfolio_df", "portfolio_dict", "selected_ticker", "last_processed_file", "messages", "radar_alerts", "last_sync_time"]:
            if k in st.session_state: del st.session_state[k]
        st.session_state.uploader_key += 1
        st.rerun()
        
    st.markdown('<div style="margin: 25px 0; height: 1px; background: linear-gradient(90deg, rgba(0,212,255,0) 0%, rgba(0,212,255,0.4) 50%, rgba(0,212,255,0) 100%);"></div>', unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="status-badge status-active">Guardian AI: Active</div>', unsafe_allow_html=True)
    st.markdown('<div class="status-badge status-active">Market Feed: NSE India</div>', unsafe_allow_html=True)

# =========================
# MAIN DASHBOARD
# =========================
left, right = st.columns([2.3, 1], gap="large")

with left:
    st.markdown("""
        <style>
            .hero-container {
                padding: 10px 0 30px 0;
                display: flex;
                flex-direction: column;
                align-items: flex-start;
            }
            
            .hero-title {
                font-family: 'orbitron', 'Segoe UI', sans-serif;
                font-size: 2.8rem;
                font-weight: 900;
                background: linear-gradient(90deg, #FFFFFF 0%, #00D4FF 50%, #0072FF 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                letter-spacing: 4px;
                text-transform: uppercase;
                margin: 0;
                filter: drop-shadow(0 0 15px rgba(0, 212, 255, 0.4));
            }
            
            .hero-subtitle {
                font-size: 0.75rem;
                color: #8899A6;
                letter-spacing: 3px;
                text-transform: uppercase;
                margin-top: -5px;
                display: flex;
                align-items: center;
                font-weight: 600;
            }

            .hero-subtitle::before {
                content: "";
                height: 2px;
                width: 30px;
                background: #00D4FF;
                display: inline-block;
                margin-right: 10px;
                box-shadow: 0 0 8px #00D4FF;
            }

            .scan-line {
                width: 100%;
                height: 1px;
                background: linear-gradient(90deg, rgba(0,212,255,0) 0%, rgba(0,212,255,0.8) 50%, rgba(0,212,255,0) 100%);
                margin-top: 15px;
                position: relative;
                overflow: hidden;
            }

            .scan-line::after {
                content: "";
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, #FFFFFF, transparent);
                animation: scan-move 3s infinite linear;
            }

            @keyframes scan-move {
                0% { left: -100%; }
                100% { left: 100%; }
            }
        </style>
        
        <div class="hero-container">
            <h1 class="hero-title">Investor Guardian</h1>
            <div class="hero-subtitle">Advanced Neural Asset Protection </div>
            <div class="scan-line"></div>
        </div>
    """, unsafe_allow_html=True)
    # 1. Network Status
    st.markdown("""
            <div class="guardian-header-container">
                <span class="header-pulse"></span>
                <span class="guardian-header-text">Network Status</span>
            </div>
        """, unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.markdown('<div class="stat-box-inner"><div class="stat-label">Portfolio</div><div class="stat-value">OPTIMAL</div></div>', unsafe_allow_html=True)
    c2.markdown('<div class="stat-box-inner"><div class="stat-label">Alpha Gain</div><div class="stat-value" style="color:#00FFAB">+₹12.4K</div></div>', unsafe_allow_html=True)
    c3.markdown('<div class="stat-box-inner"><div class="stat-label">Threat Level</div><div class="stat-value" style="color:#FF4B4B">LOW</div></div>', unsafe_allow_html=True)

    # 2. Portfolio Table Section
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div class="portfolio-header">
            <span class="live-dot"></span>
            ACTIVE ASSETS: SECURE INVENTORY
        </div>
    """, unsafe_allow_html=True)

    # Styling the dataframe to look like a clean terminal
    # We use on_select="rerun" to catch the click event instantly
    event = st.dataframe(
        portfolio_df,
        hide_index=True,
        use_container_width=True,
        on_select="rerun",
        selection_mode="single-row",
        key="portfolio_selection_table"
    )

    # Logic to update the global selected_ticker based on table click
    if event and event.get("selection") and len(event["selection"]["rows"]) > 0:
        selected_row_index = event["selection"]["rows"][0]
        clicked_table_ticker = portfolio_df.iloc[selected_row_index]["Ticker"]
        
        if clicked_table_ticker != st.session_state.selected_ticker:
            st.session_state.selected_ticker = clicked_table_ticker
            # We don't need an extra st.rerun() here because on_select="rerun" handles it
    # 3. Opportunity Radar
    # --- Opportunity Radar Section ---
    # --- Opportunity Radar Section ---
    st.markdown("""
        <div class="guardian-header-container">
            <span class="header-pulse"></span>
            <span class="guardian-header-text">Opportunity Radar</span>
        </div>
    """, unsafe_allow_html=True)

    if "radar_alerts" not in st.session_state:
        st.session_state.radar_alerts = generate_radar_alerts()

    alerts = st.session_state.radar_alerts
    r1, r2, r3 = st.columns(3)
    cols = [r1, r2, r3]

    for i in range(3):
        with cols[i]:
            if i < len(alerts):
                a = alerts[i]
                ticker = a.get("stock", "N/A")

                # Inside your radar loop:
                is_active = (ticker == st.session_state.selected_ticker)
                active_style = "border: 1px solid #00D4FF; box-shadow: 0 0 15px rgba(0, 212, 255, 0.3);" if is_active else ""

                    # Replace the triple dots with actual data from your 'a' dictionary
                st.markdown(f"""
                    <div class="radar-card" style="{active_style}">
                        <div class="radar-type">{a.get('type','SIGNAL')}</div>
                        <div class="stat-value">{ticker} {"📡" if is_active else ""}</div>
                        <div style="font-size:0.75rem; color:#00D4FF; margin-top:8px; font-weight:600;">
                            {a.get('event', 'Monitoring Pattern...')}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # 2. Balanced Full-Width Button
                if st.button(f"Analyze {ticker}", key=f"radar_btn_{i}", use_container_width=True):
                    st.session_state.selected_ticker = ticker
                    st.toast(f"Neural Feed Updated: {ticker}", icon="📡")
                    st.rerun()
            else:
                st.markdown('<div class="radar-card" style="opacity:0.2;">Scanning...</div>', unsafe_allow_html=True)
    # 4. Neural Chart
    st.markdown(f'<p class="section-header" style="margin-top:2rem;">Neural Chart: {target_ticker}</p>', unsafe_allow_html=True)

    if "last_plotted_ticker" not in st.session_state:
        st.session_state.last_plotted_ticker = target_ticker

    if st.session_state.last_plotted_ticker != target_ticker:
        st.toast(f"Neural Feed Updated: {target_ticker}", icon="📉")
        st.session_state.last_plotted_ticker = target_ticker

    fig = plot_stock(target_ticker)
    if fig:
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(f"⚠️ Guardian Node: Connection Lost to {target_ticker}")
        st.info("The NSE Data Feed is currently throttled. Attempting reconnection...")

with right:
    # Heading for the chat section
    st.markdown('<p class="guardian-header-text" style="font-size: 0.8rem; margin-bottom:10px;">Guardian AI Chat</p>', unsafe_allow_html=True)
    
    # 1. Initialize Messages
    if "messages" not in st.session_state: 
        st.session_state.messages = [{"role": "assistant", "content": "System Ready. Analyzing " + target_ticker}]

    # 2. Chat History Container
    # 2. Chat History Container
    with st.container(height=350):
        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                # Check if the message contains our terminal HTML
                if "<div style=" in m["content"]:
                    st.components.v1.html(m["content"], height=250, scrolling=True)
                else:
                    st.markdown(m["content"])
        
    # 3. Chat Input Logic (Corrected Indentation to stay inside 'right' column)
    if prompt := st.chat_input("Ask Guardian about " + target_ticker):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.spinner("🧠 Analyzing..."):
            # Fetch current settings
            current_risk = st.session_state.get('risk_lvl', 'Balanced') 
            
            # Generate Advice from Backend
            advice = generate_advice(
                target_ticker, 
                user_query=prompt, 
                portfolio=current_portfolio, 
                risk_level=current_risk
            )
            
            # SMALL FONT FORMATTING for Chat Reply
           # --- IMPROVED TERMINAL STYLING FOR CHAT ---
           # Inside your chat input logic...
            response = f"""
            <body style="margin:0; padding:0; background-color: #050A14;">
            <div style="
                background-color: #0E1621; 
                border: 1px solid #00D4FF; 
                border-radius: 8px; 
                padding: 15px; 
                font-family: 'Courier New', Courier, monospace;
                box-shadow: inset 0 0 10px rgba(0, 212, 255, 0.1);
                color: #E6F1FF;
            ">
                <div style="color: #00D4FF; font-size: 0.85rem; font-weight: bold; border-bottom: 1px solid rgba(0, 212, 255, 0.2); padding-bottom: 5px; margin-bottom: 10px; display: flex; justify-content: space-between;">
                    <span>🛡️ GUARDIAN_INTELLIGENCE_v3.3</span>
                
                </div>
                
                <div style="color: #FFFFFF; font-size: 0.95rem; margin-bottom: 8px;">
                    <span style="color: #00FFAB;">[DECISION]:</span> {advice['insight']}
                </div>
                
                <div style="font-size: 0.75rem; color: #8899A6; margin-bottom: 12px; display: flex; gap: 15px;">
                    <span><b style="color: #00D4FF;">PROFILE:</b> {current_risk}</span>
                    <span><b style="color: #00D4FF;">IMPACT:</b> {advice.get('impact', '₹0')}</span>
                </div>

                <div style="color: #E6F1FF; font-size: 0.85rem; line-height: 1.5; border-left: 2px solid rgba(0, 212, 255, 0.3); padding-left: 10px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                    {advice['reason']}
                </div>
            </div>
            </body>
            """
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.last_advice = advice
            st.rerun()

    # 4. Video Briefing Section
    st.markdown('<div style="margin: 25px 0; height: 1px; background: linear-gradient(90deg, rgba(0,212,255,0) 0%, rgba(0,212,255,0.4) 50%, rgba(0,212,255,0) 100%);"></div>', unsafe_allow_html=True)
    if st.button("🛡️ Generate Briefing Video", use_container_width=True):
        # Determine which advice to use (latest chat or general)
        current_advice = st.session_state.get("last_advice")
        
        with st.status("Rendering Video Briefing...") as s:
            if not current_advice:
                current_advice = generate_advice(target_ticker, portfolio=current_portfolio, risk_level=risk_lvl)
            
            v_path = generate_briefing_video(target_ticker, current_advice)
            
            if v_path and os.path.exists(v_path):
                s.update(label="Briefing Secured!", state="complete")
                st.video(v_path)
            else: 
                s.update(label="Error in Rendering", state="error")