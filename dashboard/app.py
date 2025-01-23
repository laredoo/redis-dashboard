import redis
import json
from datetime import datetime
import os
import time
import streamlit as st

REDIS_HOST = os.environ['REDIS_HOST']
REDIS_PORT = os.environ['REDIS_PORT']
REDIS_INPUT_KEY = os.environ['REDIS_INPUT_KEY']

config = {
    "timestamp": "2025-01-23 14:29:25.694864",
    "percent-memory-caching": 68.9197342004972, 
    "percent-network-egress": 32.298898723669225
}

st.set_page_config(page_title="Hamlet Dashboardh: Resource Monitoring", layout="wide")

st.header("Network Metrics")
percent_network_egress = st.metric("Percent Network Egress", "0%")

st.header("Memory Metrics")
percent_memory_cached = st.metric("Percent Memory Cached", "0%")

class DashboardConfig:
    def __init__(self):
        self.REDIS_HOST = REDIS_HOST
        self.REDIS_PORT = REDIS_PORT
        self.REDIS_INPUT_KEY = REDIS_INPUT_KEY
        
        self.redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

def get_redis_data(config: DashboardConfig):
    try:
        data = config.redis_client.get(REDIS_INPUT_KEY)
        
        if data is None:
            st.error("Nenhum dado encontrado no Redis para a chave especificada.")
            return None
        
        data = data.decode('utf-8')
        
        data = json.loads(data)

        return data
    except redis.exceptions.ConnectionError as e:
        st.error(f"Erro de conexão com o Redis: {e}")
        return None
    except json.JSONDecodeError as e:
        st.error(f"Erro ao decodificar JSON: {e}")
        return None
    except Exception as e:
        st.error(f"Erro ao acessar o Redis: {e}")
        return None

def get_greeting(timestamp):
    hour = timestamp.hour
    if hour < 12:
        return "Good Morning."
    elif hour < 18:
        return "Good Afternoon."
    else:
        return "Good Evening."
    
def format_date(timestamp):
    dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
    day = dt.day
    suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10 if day not in [11, 12, 13] else 0, 'th')
    return dt.strftime(f"%B {day}{suffix}, %Y")

def update_config(metrics):
    try:
        percent_network_egress.metric("Percent Network Egress", f"{metrics.get('percent-network-egress', 0):.2f}%")
        percent_memory_cached.metric("Percent Memory Cached", f"{metrics.get('percent-memory-caching', 0):.2f}%")

        timestamp = metrics.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")


        greeting = get_greeting(timestamp)

        formatted_date = format_date(timestamp)

        st.markdown(f"""
            <div class="header-container">
                <div class="greeting">{greeting}</div>
                <div class="date">{formatted_date}</div>
            </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error fetching data: {e}")

def main():

    config = DashboardConfig()
    while True:
        data = get_redis_data(config)
        update_config(data)
        time.sleep(5)

if __name__ == "__main__":
    main()