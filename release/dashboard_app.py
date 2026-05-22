import streamlit as st
import random
import time

st.set_page_config(
    page_title="Tesla Robotaxi Ride-Sharing Dashboard",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark glassmorphic theme styling
st.markdown("""
<style>
    .reportview-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }
    .card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
    }
    .text-glow {
        text-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #e879f9;
    }
</style>
""", unsafe_allow_html=True)

st.title("🚕 Tesla Robotaxi Operations Dashboard")
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="card"><h3>🤖 Active Robotaxis</h3><div class="metric-value">42 Units</div><p style="color:#10b981">🔋 92% Avg Battery Charge</p></div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card"><h3>📈 Completed Rides</h3><div class="metric-value">384 Rides</div><p style="color:#38bdf8">⚡ Peak Demand System Engaged</p></div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="card"><h3>💰 Earnings Today</h3><div class="metric-value">$4,820</div><p style="color:#f59e0b">📈 Surge Factor: 1.4x Active</p></div>', unsafe_allow_html=True)