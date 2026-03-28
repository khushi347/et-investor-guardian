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

if "risk_lvl" not in st.session_state:
    st.session_state.risk_lvl = "Balanced"

# --- FIX: ticker correction ---
def fix_ticker(ticker):
    if not ticker: return "RELIANCE.NS"
    t = str(ticker).strip().upper()
    t = t.replace(".NS", "") 
    return f"{t}.NS"

# --- HELPER: Unified Message Formatter ---
def format_guardian_msg(advice):
    return f"""
    <div style="background: #0E1621; border: 1px solid rgba(0, 212, 255, 0.3); border-top: 3px solid #00D4FF; padding: 20px; color: #E6F1FF; font-family: sans-serif; border-radius: 8px;">
        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid rgba(0, 212, 255, 0.1); padding-bottom: 8px; margin-bottom: 15px;">
            <span style="color: #00D4FF; font-size: 0.7rem; font-weight: bold;">🛡️ {advice.get('type', 'SIGNAL')}</span>
            <span style="color: #8899A6; font-size: 0.7rem;">CONFIDENCE: {advice.get('confidence', 'HIGH')}</span>
        </div>
        <div style="margin-bottom: 15px;">
            <span style="color: #00FFAB; font-size: 0.8rem; font-family: monospace;">[SIGNAL]:</span> 
            <div style="font-size: 1.1rem; font-weight: 600; margin-top: 5px;">{advice['insight']}</div>
        </div>
        <div style="background: rgba(0, 212, 255, 0.05); padding: 10px; border-radius: 4px; margin-bottom: 15px; border: 1px solid rgba(0, 212, 255, 0.1);">
            <div style="font-size: 0.6rem; color: #8899A6; text-transform: uppercase;">Calculated Impact</div>
            <div style="font-size: 1rem; font-weight: 700; color: #00FFAB;">{advice['impact']}</div>
        </div>
        <div style="color: #B0C4DE; font-size: 0.85rem; line-height: 1.5; border-left: 2px solid #00D4FF; padding-left: 10px;">
            <span style="color: #00D4FF; font-weight: bold;">EXPLANATION:</span> {advice['reason']}
        </div>
    </div>
    """

# --- CONFIG ---
st.set_page_config(page_title="Investor Guardian", layout="wide", initial_sidebar_state="expanded")

# --- CSS (UNCHANGED) ---
st.markdown("""
<style>

.hero-title {
    font-size: 2rem;
    font-weight: 800;
    color: #00D4FF;

    text-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
    letter-spacing: 1.5px;
    text-transform: uppercase;

    display: flex;
    align-items: center;

    border-left: 3px solid #00D4FF;
    padding-left: 12px;
    margin-bottom: 10px;
}

.hero-subtitle {
    font-size: 0.75rem;
    color: #8899A6;
    letter-spacing: 1px;
    margin-left: 15px;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
div.stButton { margin-top: 20px !important; }
.chat_message-container { width: 100% !important; max-width: 1200px !important; height: auto !important; min-height: 200px; }
div.stButton > button { background: rgba(0, 212, 255, 0.05) !important; border: 1px solid rgba(0, 212, 255, 0.3) !important; color: #00D4FF !important; font-weight: 700 !important; text-transform: uppercase; letter-spacing: 1px; transition: all 0.3s ease !important; }
div.stButton > button:hover { background: rgba(0, 212, 255, 0.15) !important; border: 1px solid #00D4FF !important; box-shadow: 0 0 15px rgba(0, 212, 255, 0.2); transform: translateY(-2px); }
div.stButton > button.radar-btn { background-color: transparent !important; border: none !important; padding: 0 !important; color: inherit !important; text-align: left !important; width: 100% !important; height: 100% !important; }
.guardian-header-container { display: flex; align-items: center; border-left: 3px solid #00D4FF; padding-left: 12px; margin-top: 1.5rem; margin-bottom: 1rem; }
.guardian-header-text { font-size: 0.9rem; font-weight: 800; color: #00D4FF; text-shadow: 0 0 8px rgba(0, 212, 255, 0.4); letter-spacing: 1.5px; text-transform: uppercase; }
.header-pulse { height: 6px; width: 6px; background-color: #00D4FF; border-radius: 50%; display: inline-block; margin-right: 10px; box-shadow: 0 0 8px #00D4FF; animation: pulse-ring 2s infinite; }
@keyframes pulse-ring { 0% { opacity: 1; transform: scale(1); } 50% { opacity: 0.3; transform: scale(0.8); } 100% { opacity: 1; transform: scale(1); } }
.stat-box-inner, .radar-card { background: rgba(16, 28, 50, 0.7); border: 1px solid rgba(0, 212, 255, 0.15); border-radius: 12px; padding: 20px; height: 140px; width: 100%; display: flex; flex-direction: column; justify-content: center; align-items: flex-start; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); cursor: pointer; box-sizing: border-box; overflow: hidden; }
.stat-box-inner:hover, .radar-card:hover { transform: translateY(-5px); border: 1px solid rgba(0, 212, 255, 0.5); background: rgba(16, 28, 50, 0.9); box-shadow: 0 10px 20px rgba(0, 212, 255, 0.15); }
.stat-label { font-size: 0.65rem; color: #8899A6; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; }
.stat-value { font-size: 1.15rem; font-weight: 700; color: #FFFFFF; }
.radar-type { font-size: 0.6rem; color: #00D4FF; font-weight: 700; text-transform: uppercase; margin-bottom: 4px; }
.portfolio-header { font-size: 1rem; font-weight: 800; color: #00D4FF; text-shadow: 0 0 10px rgba(0, 212, 255, 0.3); letter-spacing: 1.5px; margin-bottom: 15px; display: flex; align-items: center; border-left: 3px solid #00D4FF; padding-left: 12px; text-transform: uppercase; }
.live-dot { height: 8px; width: 8px; background-color: #00D4FF; border-radius: 50%; display: inline-block; margin-right: 12px; box-shadow: 0 0 8px #00D4FF; animation: blink 2s infinite; }
@keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
.stApp { background: #050A14; color: #E6F1FF; }
[data-testid="stSidebar"] { background-color: #0B132B; border-right: 1px solid rgba(0, 212, 255, 0.1); }
.persona-card { background: rgba(16, 28, 50, 0.6); border: 1px solid rgba(0, 212, 255, 0.2); border-radius: 12px; padding: 20px; margin-bottom: 20px; }
.persona-name { font-size: 1.2rem; font-weight: 700; color: #FFFFFF; margin-bottom: 5px; }
.sidebar-header { font-size: 0.7rem; font-weight: 700; color: #00D4FF; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 15px; }
.status-badge { padding: 10px; border-radius: 6px; margin-top: 8px; font-size: 0.8rem; border: 1px solid rgba(255,255,255,0.05); }
.status-active { background: rgba(74, 222, 128, 0.1); color: #4ade80; border: 1px solid rgba(74, 222, 128, 0.2); }
</style>
""", unsafe_allow_html=True)

# =========================
# DATA INITIALIZATION
# =========================
demo_df = pd.DataFrame({"Ticker": ["RELIANCE", "TCS", "HDFCBANK", "INFY"], "Quantity": [15, 10, 50, 25]})
demo_dict = {"RELIANCE.NS": 15, "TCS.NS": 10, "HDFCBANK.NS": 50, "INFY.NS": 25}

if "portfolio_df" not in st.session_state:
    st.session_state.portfolio_df = demo_df
    st.session_state.portfolio_dict = demo_dict

if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = st.session_state.portfolio_df.iloc[0]["Ticker"]

# --- GLOBAL REFRESH ---
portfolio_df = st.session_state.portfolio_df
if "initialized" not in st.session_state:

        current_ticker = st.session_state.selected_ticker

        with st.spinner(f"🧬 Initializing AI for {current_ticker}..."):
            initial_advice = generate_advice(
                fix_ticker(current_ticker),
                portfolio=st.session_state.portfolio_dict,
                risk_level=st.session_state.risk_lvl
            )

        st.session_state.messages = [
            {"role": "assistant", "content": format_guardian_msg(initial_advice)}
        ]
        st.session_state.last_advice = initial_advice

        # ✅ prevent re-run loop
        st.session_state.initialized = True

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown('<div class="sidebar-header">Identity Matrix</div>', unsafe_allow_html=True)
    st.markdown(f"""<div class="persona-card"><div class="persona-name">Retail Hero</div><div style="font-size: 0.7rem; color: #8899A6;">Active Session: Guardian-01</div></div>""", unsafe_allow_html=True)
    st.session_state.risk_lvl = st.select_slider(
        "Risk Appetite",
        options=["Conservative", "Balanced", "Aggressive"],
        value=st.session_state.risk_lvl
    )
    st.markdown('<div style="margin: 25px 0; height: 1px; background: linear-gradient(90deg, rgba(0,212,255,0) 0%, rgba(0,212,255,0.4) 50%, rgba(0,212,255,0) 100%);"></div>', unsafe_allow_html=True)

    if "uploader_key" not in st.session_state: st.session_state.uploader_key = 0
    uploaded_file = st.file_uploader("Upload Portfolio", type=["csv", "xlsx"], key=f"up_{st.session_state.uploader_key}")
    
    if uploaded_file:
        if "last_processed_file" not in st.session_state or st.session_state.last_processed_file != uploaded_file.name:
            with st.spinner("🧬 Synchronizing Portfolio..."):
                data = parse_portfolio_csv(uploaded_file)
                if data:
                    # Update State
                    st.session_state.portfolio_dict = data
                    st.session_state.portfolio_df = pd.DataFrame(list(data.items()), columns=["Ticker", "Quantity"])
                    st.session_state.last_processed_file = uploaded_file.name
                    
                    # Auto-Analyze First Stock
                    new_ticker_raw = list(data.keys())[0].replace(".NS", "")
                    st.session_state.selected_ticker = new_ticker_raw
                    
                    initial_advice = generate_advice(fix_ticker(new_ticker_raw), portfolio=data, risk_level=st.session_state.risk_lvl)
                    st.session_state.messages = [{"role": "assistant", "content": format_guardian_msg(initial_advice)}]
                    st.session_state.last_advice = initial_advice
                    st.rerun()
    
    if st.button("Reset to Demo"):
        for k in ["portfolio_df", "portfolio_dict", "selected_ticker", "last_processed_file", "messages", "radar_alerts", "last_sync_time"]:
            if k in st.session_state: del st.session_state[k]
        st.session_state.uploader_key += 1
        st.rerun()

# =========================
# MAIN DASHBOARD
# =========================
left, right = st.columns([2.3, 1], gap="large")

with left:
    # (Hero/Header UI Unchanged...)
    st.markdown("""
<div class="hero-container">
    <div class="hero-title">INVESTOR GUARDIAN</div>
    <div class="hero-subtitle">ADVANCED NEURAL ASSET PROTECTION</div>
    <div class="scan-line"></div>
</div>
""", unsafe_allow_html=True)
    st.markdown("""<div class="guardian-header-container"><span class="header-pulse"></span><span class="guardian-header-text">Network Status</span></div>""", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.markdown('<div class="stat-box-inner"><div class="stat-label">Portfolio</div><div class="stat-value">OPTIMAL</div></div>', unsafe_allow_html=True)
    c2.markdown('<div class="stat-box-inner"><div class="stat-label">Alpha Gain</div><div class="stat-value" style="color:#00FFAB">+₹12.4K</div></div>', unsafe_allow_html=True)
    c3.markdown('<div class="stat-box-inner"><div class="stat-label">Threat Level</div><div class="stat-value" style="color:#FF4B4B">LOW</div></div>', unsafe_allow_html=True)

    st.markdown('<br><div class="portfolio-header"><span class="live-dot"></span>ACTIVE ASSETS: SECURE INVENTORY</div>', unsafe_allow_html=True)

    event = st.dataframe(
        portfolio_df,
        hide_index=True,
        use_container_width=True,
        on_select="rerun",
        selection_mode="single-row",
        key="portfolio_selection_table"
    )

    # ✅ Safe extraction
    selected_rows = event.get("selection", {}).get("rows", [])

    if selected_rows:
        clicked_ticker = portfolio_df.iloc[selected_rows[0]]["Ticker"]

        # ✅ Avoid unnecessary reruns
        if clicked_ticker != st.session_state.selected_ticker:
            st.session_state.selected_ticker = clicked_ticker

            with st.spinner(f"🧬 Analyzing {clicked_ticker}..."):
                # ✅ Directly store in session (no auto_advice bug)
                st.session_state.last_advice = generate_advice(
                    fix_ticker(clicked_ticker),
                    portfolio=st.session_state.portfolio_dict,
                    risk_level=st.session_state.risk_lvl
                )

                st.session_state.messages = [
                    {
                        "role": "assistant",
                        "content": format_guardian_msg(st.session_state.last_advice)
                    }
                ]

            st.rerun()

# --- Neural Opportunity Radar ---
    st.markdown("""<div class="guardian-header-container"><span class="header-pulse"></span><span class="guardian-header-text">Neural Opportunity Radar</span></div>""", unsafe_allow_html=True)
    if "radar_alerts" not in st.session_state: st.session_state.radar_alerts = generate_radar_alerts()
        
    alerts = st.session_state.radar_alerts
    cols = st.columns(3)
    for i in range(3):
            with cols[i]:
                if i < len(alerts):
                    a = alerts[i]
                    ticker = a.get("stock", "N/A")
                    is_active = ticker.replace(".NS","").upper() == st.session_state.selected_ticker
                    active_style = "border: 1px solid #00D4FF; box-shadow: 0 0 15px rgba(0, 212, 255, 0.3);" if is_active else ""
                    
                    st.markdown(f"""<div class="radar-card" style="{active_style}"><div class="radar-type">{a.get('type','SIGNAL')}</div><div class="stat-value">{ticker} {"📡" if is_active else ""}</div><div style="font-size:0.75rem; color:#00D4FF; margin-top:8px; font-weight:600;">{a.get('event', 'Monitoring...')}</div></div>""", unsafe_allow_html=True)
                    if st.button(f"Intercept {ticker}", key=f"radar_btn_{i}", use_container_width=True):
                        
                        clean_ticker = ticker.replace(".NS", "").upper()
                        st.session_state.selected_ticker = clean_ticker

                        with st.spinner(f"🧬 Extracting {clean_ticker}..."):
                            st.session_state.last_advice = generate_advice(
                                fix_ticker(clean_ticker),
                                portfolio=st.session_state.portfolio_dict,
                                risk_level=st.session_state.risk_lvl
                            )

                            st.session_state.messages = [
                                {
                                    "role": "assistant",
                                    "content": format_guardian_msg(st.session_state.last_advice)
                                }
                            ]

                        st.rerun()

    # --- Neural Chart ---
    # --- Neural Chart ---
    current_ticker = st.session_state.selected_ticker
    query_ticker = fix_ticker(current_ticker)

    st.markdown(
        f'<p class="section-header" style="margin-top:2rem;">Neural Chart: {current_ticker}</p>',
        unsafe_allow_html=True
    )

    fig = plot_stock(query_ticker)

    if fig:
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig, use_container_width=True, key=f"chart_{current_ticker}")
    else:
        st.error(f"⚠️ Guardian Node: Connection Lost to {current_ticker}")

with right:
    st.markdown('<p class="guardian-header-text" style="font-size: 0.8rem; margin-bottom:10px;">Guardian AI Console</p>', unsafe_allow_html=True)
    if "messages" not in st.session_state: 
        st.session_state.messages = [
    {
        "role": "assistant",
        "content": f"System Ready. Analyzing {st.session_state.selected_ticker}"
    }
]

    with st.container(height=650):
        for m in st.session_state.messages:
            st.markdown('<div style="margin-top: 25px;"></div>', unsafe_allow_html=True)
            with st.chat_message(m["role"]):
                if "<div style=" in m["content"]:
                    st.components.v1.html(m["content"], height=500, scrolling=True)
                else:
                    st.markdown(f"""<div style="font-family: monospace; color: #00D4FF; font-size: 0.85rem; opacity: 0.8;">> {m["content"]}</div>""", unsafe_allow_html=True)

        current_ticker = st.session_state.selected_ticker

    prompt = st.chat_input(f"Input Command for {current_ticker}")

    if prompt and prompt != st.session_state.get("last_prompt"):
    
        st.session_state.last_prompt = prompt

        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("🧬 PROCESSING..."):
            advice = generate_advice(
                fix_ticker(current_ticker),
                user_query=prompt,
                portfolio=st.session_state.portfolio_dict,
                risk_level=st.session_state.risk_lvl
            )

            st.session_state.messages.append({
                "role": "assistant",
                "content": format_guardian_msg(advice)
            })

            st.session_state.last_advice = advice

        st.rerun()

    st.markdown('<div style="margin: 25px 0; height: 1px; background: linear-gradient(90deg, rgba(0,212,255,0) 0%, rgba(0,212,255,0.4) 50%, rgba(0,212,255,0) 100%);"></div>', unsafe_allow_html=True)
    if st.button("🛡️ Generate Briefing Video", use_container_width=True):
            current_advice = st.session_state.get("last_advice")
            with st.status("Rendering Video Briefing...") as s:
                if not current_advice:
                    current_advice = generate_advice(query_ticker, portfolio=current_portfolio, risk_level=st.session_state.risk_lvl)
                v_path = generate_briefing_video(query_ticker, current_advice)
                if v_path and os.path.exists(v_path):
                    s.update(label="Briefing Secured!", state="complete")
                    st.video(v_path)
                else: s.update(label="Error in Rendering", state="error")