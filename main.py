import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
from datetime import datetime, timedelta
import os
from utils.charts import plot_efficient_frontier, plot_allocation

# Page config
st.set_page_config(
    page_title="Portfolio Optimization",
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

# Model selection using checkboxes
models_selected = []
if st.sidebar.checkbox("Modern Portfolio Theory", value=True):
    models_selected.append("Modern Portfolio Theory")
if st.sidebar.checkbox("Minimum Variance", value=False):
    models_selected.append("Minimum Variance")
if st.sidebar.checkbox("Maximum Sharpe Ratio", value=False):
    models_selected.append("Maximum Sharpe Ratio")
if st.sidebar.checkbox("Equal Weight", value=False):
    models_selected.append("Equal Weight")
if st.sidebar.checkbox("Risk Parity", value=False):
    models_selected.append("Risk Parity")
if st.sidebar.checkbox("Hierarchical Risk Parity", value=False):
    models_selected.append("Hierarchical Risk Parity")

# Limit the number of selected models to a maximum of 3
if len(models_selected) > 3:
    st.sidebar.error("You can select a maximum of 3 models at the same time.")
    models_selected = models_selected[:3]

# Additional settings
rebalance_freq = st.sidebar.selectbox(
    "Rebalancing Frequency",
    ["Quarterly", "Yearly", "None"]
)

include_rf = st.sidebar.checkbox("Include Risk-Free Asset", value=False)

# Load weights based on the selected model
weights_data = None
if "Minimum Variance" in models_selected:
    weights_file = "data/minimum_variance_weights.csv"
elif "Modern Portfolio Theory" in models_selected:
    weights_file = "modern_portfolio_theory_weights.csv"
# Add more cases here for other models if needed
else:
    weights_file = None

if weights_file and os.path.exists(weights_file):
    weights_data = pd.read_csv(weights_file, index_col=0)
    # Filter weights for the first date present
    first_date_weights = weights_data.iloc[0, 1:].to_dict() if not weights_data.empty else None
    first_date_weights = pd.Series(first_date_weights)

else:
    first_date_weights = None
    if weights_file:
        st.warning(f"File {weights_file} not found. Charts for the selected model will not be displayed.")
    else:
        st.warning("No weights file specified for the selected model.")

# Main content area with tabs
tab1, tab2, tab3, tab4 = st.tabs(["Portfolio Analysis", "Backtesting", "Model Explanation", "Export Options"])

with tab1:
    st.header("Portfolio Analysis")
    st.info("Compare the efficient frontier and portfolio allocation for selected models.")

    # Display efficient frontier for the first selected model
    for model in models_selected:
        st.subheader(f"{model}: Efficient Frontier")
        if weights_data is not None and model in ["Minimum Variance", "Modern Portfolio Theory"]:
            # Ensure required columns exist
            if all(col in weights_data.columns for col in ['risk', 'return', 'sharpe_ratio']):
                st.plotly_chart(plot_efficient_frontier(weights_data, model, include_rf))
            else:
                st.warning(f"Data for {model} is missing required columns ('risk', 'return', 'sharpe_ratio').")
            break  # Only display one efficient frontier chart
        else:
            st.write(f"Efficient frontier for {model} will be displayed here.")

    # Display a single chart for the first weights
    for model in models_selected:
        st.subheader(f"{model}: Portfolio Allocation")
        if first_date_weights is not None and model in ["Minimum Variance"]:
            # Ensure weights are numeric
            if pd.api.types.is_numeric_dtype(first_date_weights):
                try:
                    st.plotly_chart(plot_allocation(first_date_weights))
                except ValueError as e:
                    st.warning(f"Unable to display portfolio allocation for {model}: {e}")
            else:
                st.warning(f"Portfolio weights for {model} contain non-numeric values and cannot be displayed.")
            break  # Only display one allocation pie chart
        else:
            st.write(f"Allocation pie chart for {model} will be displayed here.")

with tab2:
    st.header("Backtesting Results")
    st.info("Compare historical performance and risk metrics for selected models against the S&P 500.")

    # Display a single backtesting graph for all selected models
    if models_selected:
        st.subheader("Backtesting: Selected Models vs S&P 500")
        st.write("A combined backtesting chart for all selected models and the S&P 500 will be displayed here.")
    else:
        st.warning("No models selected for backtesting. Please select at least one model.")

with tab3:
    st.header("Model Information")
    st.info("Descriptions of the selected models.")

    # Display descriptions for selected models
    for model in models_selected:
        st.subheader(f"Model: {model}")
        if model == "Modern Portfolio Theory":
            st.markdown("""
            **Modern Portfolio Theory (MPT)** assumes:
            - Investors are risk-averse
            - Markets are efficient
            - Portfolio selection is based on expected return and risk
            
            MPT uses the efficient frontier to identify portfolios that offer the highest expected return for a given level of risk.
            """)
        elif model == "Minimum Variance":
            st.markdown("""
            **Minimum Variance Portfolio (MVP)** seeks to minimize portfolio volatility
            regardless of expected return.
            
            MVP is ideal for highly risk-averse investors and focuses solely on reducing risk.
            """)
        elif model == "Maximum Sharpe Ratio":
            st.markdown("""
            **Maximum Sharpe Ratio Portfolio (MSR)** maximizes risk-adjusted return.
            Often includes a risk-free asset.
            
            MSR aims to achieve the highest return per unit of risk, making it a popular choice for balanced portfolios.
            """)
        elif model == "Equal Weight":
            st.markdown("""
            **Equal Weight Portfolio** assigns equal investment to each asset.
            Simple, diversified, and easy to manage.
            
            This approach avoids over-concentration in any single asset and is often used as a benchmark.
            """)
        elif model == "Risk Parity":
            st.markdown("""
            **Risk Parity** allocates capital based on the risk contribution of each asset.
            Aims for equal risk exposure.
            
            Risk Parity is designed to balance risk across asset classes, making it robust during market volatility.
            """)
        elif model == "Hierarchical Risk Parity":
            st.markdown("""
            **Hierarchical Risk Parity (HRP)** uses machine learning to cluster assets
            and allocate based on hierarchical relationships.
            
            HRP is particularly effective in reducing portfolio risk by leveraging asset correlations and clustering techniques.
            """)

with tab4:
    st.header("Export Options")
    st.info("Download portfolio allocations or summary reports.")
    st.button("Download Allocations as CSV")
    st.button("Download Summary Report as PDF")

# Sidebar: Economic Context Panel (Optional)
if st.sidebar.checkbox("Show Economic Context", value=False):
    st.sidebar.subheader("Economic Context")
    st.sidebar.write("Fed Funds Rate, Inflation, and GDP data will be displayed here.")
