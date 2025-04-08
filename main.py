import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="Portfolio Optimization",
    page_icon="\ud83d\udcca",
    layout="wide"
)

# Title and description
st.title("Portfolio Optimization & Backtesting")
st.markdown("""
Explore different portfolio optimization strategies using S&P 500 stocks and bonds.
Learn how different models allocate portfolios and analyze their historical performance.
""")

# Sidebar controls
st.sidebar.header("Portfolio Settings")

# Model selection
model = st.sidebar.selectbox(
    "Optimization Model",
    ["Modern Portfolio Theory", "Minimum Variance", "Maximum Sharpe Ratio", 
     "Equal Weight", "Risk Parity", "Hierarchical Risk Parity"]
)

# Time period controls
current_year = datetime.now().year
start_year = st.sidebar.slider("Investment Start Year", 2000, current_year-1, 2015)
training_years = st.sidebar.slider("Training Window (years)", 1, 30, 10)

# Additional settings
rebalance_freq = st.sidebar.selectbox(
    "Rebalancing Frequency",
    ["Monthly", "Quarterly", "Yearly", "None"]
)

include_rf = st.sidebar.checkbox("Include Risk-Free Asset", value=False)

# Main content area with tabs
tab1, tab2, tab3 = st.tabs(["Portfolio Analysis", "Backtesting", "Model Explanation"])

with tab1:
    st.header("Portfolio Analysis")
    st.info("This section will show the efficient frontier and current portfolio allocation")

    # Placeholder for charts
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Efficient Frontier")
        st.write("Efficient frontier plot will be displayed here")

    with col2:
        st.subheader("Portfolio Allocation")
        st.write("Allocation pie chart will be displayed here")

with tab2:
    st.header("Backtesting Results")
    st.info("This section will show historical performance and risk metrics")
    st.write("Backtest charts and metrics will be displayed here")

with tab3:
    st.header("Model Information")
    st.info(f"Currently selected: {model}")

    if model == "Modern Portfolio Theory":
        st.markdown("""
        **Modern Portfolio Theory (MPT)** assumes:
        - Investors are risk-averse
        - Markets are efficient
        - Portfolio selection is based on expected return and risk
        """)
    elif model == "Minimum Variance":
        st.markdown("""
        **Minimum Variance Portfolio (MVP)** seeks to minimize portfolio volatility
        regardless of expected return.
        """)
    elif model == "Maximum Sharpe Ratio":
        st.markdown("""
        **Maximum Sharpe Ratio Portfolio (MSR)** maximizes risk-adjusted return.
        Often includes a risk-free asset.
        """)
    elif model == "Equal Weight":
        st.markdown("""
        **Equal Weight Portfolio** assigns equal investment to each asset.
        Simple, diversified, and easy to manage.
        """)
    elif model == "Risk Parity":
        st.markdown("""
        **Risk Parity** allocates capital based on the risk contribution of each asset.
        Aims for equal risk exposure.
        """)
    elif model == "Hierarchical Risk Parity":
        st.markdown("""
        **Hierarchical Risk Parity (HRP)** uses machine learning to cluster assets
        and allocate based on hierarchical relationships.
        """)
