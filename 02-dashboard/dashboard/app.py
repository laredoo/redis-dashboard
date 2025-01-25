import redis
import json
from datetime import datetime
import os
import time
import streamlit as st

REDIS_HOST = os.environ['REDIS_HOST']
REDIS_PORT = os.environ['REDIS_PORT']
REDIS_INPUT_KEY = os.environ['REDIS_INPUT_KEY']

st.set_page_config(page_title="Hamlet Dashboardh: Resource Monitoring", layout="wide")

st.markdown("""
    <style>
        .stApp {
            font-family: 'Georgia', sans-serif;
            background-color: #000000;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)


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

def update_config(
        metrics, 
        percent_network_egress, 
        percent_memory_cached,
        cpu_0,
        cpu_1,
        cpu_2
    ):
    try:
        percent_network_egress.metric("Percent Network Egress", f"{metrics.get('percent-network-egress', 0):.2f}%")
        percent_memory_cached.metric("Percent Memory Cached", f"{metrics.get('percent-memory-caching', 0):.2f}%")
        cpu_0.metric("Percent CPU-0 Usage", f"{metrics.get('avg-util-cpu0-60sec', 0):.2f}%")
        cpu_1.metric("Percent CPU-1 Usage", f"{metrics.get('avg-util-cpu1-60sec', 0):.2f}%")
        cpu_2.metric("Percent CPU-2 Usage", f"{metrics.get('avg-util-cpu2-60sec', 0):.2f}%")

    except Exception as e:
        st.error(f"Error fetching data: {e}")

def main():

    config = DashboardConfig()

    data = get_redis_data(config)

    string_timestamp = data.get("timestamp")
    if isinstance(string_timestamp, str):
        timestamp = datetime.strptime(string_timestamp, "%Y-%m-%d %H:%M:%S.%f")

    greeting = get_greeting(timestamp)

    formatted_date = format_date(string_timestamp)

    st.markdown(f"""
        <div class="header-container">
            <h1 class="greeting">{greeting}</h1>
            <h2 class="date">{formatted_date}</h2>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <style>
            .header-container{
                font-family: 'Georgia', sans-serif;
                text-align: center;
                margin-bottom: 20px;
            }
            .greeting {
                font-family: 'Georgia', sans-serif;
                font-size: 32px;
                font-weight: bold;
                color: white;
            }
            .date {
                font-family: 'Georgia', sans-serif;
                font-size: 24px;
                color: gray;
            }
        </style>
    """, unsafe_allow_html=True)

    st.header("Network Metrics")
    percent_network_egress = st.metric("Percent Network Egress", "0%")

    st.header("Memory Metrics")
    percent_memory_cached = st.metric("Percent Memory Cached", "0%")

    st.header("CPU-0 Metrics")
    cpu_0 = st.metric("Percent CPU-0 Usage", "0%")

    st.header("CPU-1 Metrics")
    cpu_1 = st.metric("Percent CPU-1 Usage", "0%")

    st.header("CPU-2 Metrics")
    cpu_2 = st.metric("Percent CPU-2 Usage", "0%")

    while True:
        update_config(
            data, 
            percent_network_egress, 
            percent_memory_cached,
            cpu_0,
            cpu_1,
            cpu_2
        )
        time.sleep(5)

if __name__ == "__main__":
    main()