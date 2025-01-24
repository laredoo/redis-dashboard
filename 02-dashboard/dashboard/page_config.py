import json
import streamlit as st
import pandas as pd
import redis
import os
import time

from datetime import datetime

REDIS_HOST = os.environ['REDIS_HOST']
REDIS_PORT = os.environ['REDIS_PORT']
REDIS_INPUT_KEY = os.environ['REDIS_INPUT_KEY']

class DashboardConfig:
    def __init__(self):
        self.REDIS_HOST = REDIS_HOST
        self.REDIS_PORT = REDIS_PORT
        self.REDIS_INPUT_KEY = REDIS_INPUT_KEY
        
        self.redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
        self.data = self.get_redis_data
        
        self.set_page_config()

    def get_redis_data(self):

        data = self.redis_client.get(REDIS_INPUT_KEY)
        data = json.dumps(data)
        return data

    def set_page_config(self):
        st.set_page_config(
            page_title="System Metrics",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="expanded",
        )

        st.markdown("""
            <style>
                .stApp {
                    font-family: 'Georgia', sans-serif;
                    background-color: #000000;
                    color: white;
                }
            </style>
        """, unsafe_allow_html=True)

        st.markdown("""
            <style>
                .header-container {
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

        st.markdown("""
            <style>
                div.stProgress > div > div > div > div {
                    background-color: #ECDFCC;  
                }
            </style>
        """, unsafe_allow_html=True)

        st.markdown("""
            <style>
                div.stProgress > div > div > div {
                    font-family: 'Georgia', sans-serif;
                    height: 30px;
                    border-radius: 3px; 
                    border: 0.2px solid white;
                }
                .metric-label {
                    font-family: 'Georgia', sans-serif;
                    font-size: 18px;
                    font-weight: bold;
                }
            </style>
        """, unsafe_allow_html=True)


    def get_greeting(self, timestamp):
        """Return appropriate greeting based on time of day"""
        hour = timestamp.hour
        if hour < 12:
            return "Good Morning."
        elif hour < 18:
            return "Good Afternoon."
        else:
            return "Good Evening."
        
    def format_date(self, timestamp):
        """Format date as 'Month DDth, YYYY'"""
        dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
        day = dt.day
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10 if day not in [11, 12, 13] else 0, 'th')
        return dt.strftime(f"%B {day}{suffix}, %Y")
    
    def animate_progress(self, progress_bars, values):
        """Synchronously animate multiple progress bars"""
        max_value = max(values)
        progress_texts = progress_bars['texts']
        progress_bars = progress_bars['bars']
        
        for i in range(int(max_value) + 1):
            time.sleep(0.01)  
            for idx, (bar, value, text) in enumerate(zip(progress_bars, values, progress_texts)):
                if i <= value:
                    bar.progress(i)
                    text.markdown(f'<div class="progress-value">{i:.1f}%</div>', unsafe_allow_html=True)


