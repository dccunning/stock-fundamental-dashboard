import streamlit as st
from streamlit_dashboard.ui import show_yoy_financials_tab, show_live_chart_tab, show_financial_bar_chart

st.set_page_config(layout="wide")
st.title("Deep Value Dashboard")

tabs = st.tabs(["YoY Financials", "Financial Bar Chart", "Live Chart"])

with tabs[0]:
    show_yoy_financials_tab()

with tabs[1]:
    show_financial_bar_chart()

with tabs[2]:
    show_live_chart_tab()

