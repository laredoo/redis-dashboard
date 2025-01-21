from page_config import DashboardConfig
from datetime import datetime
import streamlit as st

def main():
    
    dashboard_config = DashboardConfig()

    data = dashboard_config.data

    timestamp = datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S.%f")

    greeting = dashboard_config.get_greeting(timestamp)

    formatted_date = dashboard_config.format_date(data["timestamp"])

    st.markdown(f"""
        <div class="header-container">
            <div class="greeting">{greeting}</div>
            <div class="date">{formatted_date}</div>
        </div>
    """, unsafe_allow_html=True)

    
    col1, col2 = st.columns(2)
    
    progress_bars = {
        'bars': [],
        'texts': []
    }

    with col1:
        st.markdown('<div class="progress-container">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Memory Caching</div>', unsafe_allow_html=True)
        progress_bars['bars'].append(st.empty())
        progress_bars['texts'].append(st.empty())
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="progress-container">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Network Egress</div>', unsafe_allow_html=True)
        progress_bars['bars'].append(st.empty())
        progress_bars['texts'].append(st.empty())
        st.markdown('</div>', unsafe_allow_html=True)
    
    dashboard_config.animate_progress(
        progress_bars,
        [data["percent-memory-caching"], data["percent-network-egress"]]
    )

