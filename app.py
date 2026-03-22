import streamlit as st

# --- BACKEND IMPORTS ---
from backend.radar import generate_radar_alerts
from backend.ai_agent import generate_advice
from charts_video.chart import plot_stock

# --- CONFIG ---
st.set_page_config(
    page_title="Investor Guardian", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# =========================
# 🎨 WINNING TERMINAL CSS
# =========================
st.markdown("""
<style>
    /* Global Reset & Background */
    .stApp {
        background: #050A14;
        color: #E6F1FF;
    }
    .main .block-container {
        padding: 2rem 3rem !important;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0B132B;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    .sidebar-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 20px;
    }
    .status-badge {
        padding: 12px;
        border-radius: 8px;
        margin-top: 10px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .status-active {
        background-color: rgba(26, 71, 49, 0.4); color: #4ade80;
        border: 1px solid rgba(74, 222, 128, 0.2);
    }
    .status-feed {
        background-color: rgba(30, 58, 138, 0.4); color: #60a5fa;
        border: 1px solid rgba(96, 165, 250, 0.2);
    }

    /* Stat Boxes */
    .stat-box-inner {
        background: rgba(16, 28, 50, 0.8);
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-radius: 8px;
        padding: 15px;
        height: 90px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .stat-label { font-size: 0.6rem; color: #8899A6; text-transform: uppercase; letter-spacing: 1.5px; }
    .stat-value { font-size: 1rem; font-weight: 700; }

    /* Terminal Elements */
    .radar-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        height: 100px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .section-header {
        font-size: 0.75rem;
        font-weight: 700;
        color: #00D4FF;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 10px;
    }

    /* Chat Styling */
    [data-testid="stChatMessage"] {
        background-color: rgba(16, 28, 50, 0.5) !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    div.stButton > button {
        margin-top: 10px !important;
        background: transparent !important;
        border: 1px solid rgba(0, 212, 255, 0.4) !important;
        color: #00D4FF !important;
        font-weight: 600;
        font-size: 0.7rem;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# 👤 SIDEBAR
# =========================
with st.sidebar:
    st.markdown('<div class="sidebar-title">Investor Profile</div>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:0.85rem; font-weight:600; margin-bottom:0;">Sync Portfolio (CSV)</p>', unsafe_allow_html=True)
    st.file_uploader("Upload CSV", label_visibility="collapsed")
    st.button("Load Demo Portfolio", width="stretch")
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="status-badge status-active">Guardian AI: Active</div>', unsafe_allow_html=True)
    st.markdown('<div class="status-badge status-feed">Market Feed: NSE India</div>', unsafe_allow_html=True)

# =========================
# MAIN GRID
# =========================
left, right = st.columns([2.3, 1], gap="large")
target = st.session_state.get("selected_ticker", "RELIANCE")

with left:
    st.markdown('<p class="section-header">Network Status</p>', unsafe_allow_html=True)
    s_col1, s_col2, s_col3 = st.columns(3)
    with s_col1:
        st.markdown('<div class="stat-box-inner"><div class="stat-label">Portfolio</div><div class="stat-value">OPTIMAL</div></div>', unsafe_allow_html=True)
    with s_col2:
        st.markdown('<div class="stat-box-inner"><div class="stat-label">Alpha Gain</div><div class="stat-value" style="color:#00FFAB">+12,400</div></div>', unsafe_allow_html=True)
    with s_col3:
        st.markdown('<div class="stat-box-inner"><div class="stat-label">Risk Level</div><div class="stat-value" style="color:#FF4B4B">CRIT_2</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="section-header">Live Terminal</p>', unsafe_allow_html=True)
    alerts = generate_radar_alerts()
    radar_cols = st.columns(3)
    for i in range(3):
        if i < len(alerts):
            alert = alerts[i]
            ticker = alert.get("stock", "N/A")
            with radar_cols[i]:
                st.markdown(f'<div class="radar-card"><div style="font-size:0.6rem; color:#8899A6;">{alert.get("event")}</div><h3 style="margin:2px 0;">{ticker}</h3></div>', unsafe_allow_html=True)
                if st.button(f"Analyze {ticker}", key=f"btn_{ticker}", width="stretch"):
                    st.session_state.selected_ticker = ticker
                    st.rerun()

    st.markdown('<p class="section-header" style="margin-top:2rem;">Deep Neural Analysis</p>', unsafe_allow_html=True)
    fig = plot_stock(target)
    if fig:
        fig.update_layout(height=400, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#E6F1FF')
        st.plotly_chart(fig, width="stretch")

# --- COMPACT RIGHT SIDE ---
with right:
    st.markdown('<p class="section-header">Guardian Chat</p>', unsafe_allow_html=True)
    st.markdown('<p style="color:#8899A6; font-size:0.6rem; font-weight:700; margin-top:-8px; margin-bottom:12px;">AI-POWERED INSIGHTS</p>', unsafe_allow_html=True)

    # Height reduced to 350px for a smaller UI
    with st.container(height=350, border=True):
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": "Ready."}]
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

    prompt = st.chat_input("Enter command...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        advice = generate_advice(target)
        st.session_state.messages.append({"role": "assistant", "content": advice["decision"]})
        st.rerun()