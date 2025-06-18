import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
from datetime import datetime, timedelta
import os
from utils.charts import plot_efficient_frontier, plot_allocation, plot_backtesting_results
from utils.backtesting import run_backtest  # Add this import

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

## Sidebar controls
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

# Function to load precomputed weights
def load_weights(method):
    # Assumes CSVs are named as 'minimum_variance_weights.csv', etc.
    path = f"data/{method}_weights.csv"
    df = pd.read_csv(path)
    # If wide format (Date as index, tickers as columns), melt to long format
    if 'Date' not in df.columns and df.index.name == 'Date':
        df = df.reset_index()
    if 'Date' not in df.columns and 'Ticker' not in df.columns:
        # Assume first column is Date, rest are tickers
        df = df.rename(columns={df.columns[0]: 'Date'})
        df = df.melt(id_vars=['Date'], var_name='Ticker', value_name='Weight')
    elif 'Date' in df.columns and not 'Ticker' in df.columns:
        # Already has Date, but wide format
        id_vars = ['Date']
        value_vars = [col for col in df.columns if col not in id_vars]
        df = df.melt(id_vars=id_vars, var_name='Ticker', value_name='Weight')
    return df

# Function to load daily returns for selected stocks
def load_returns():
    return pd.read_csv("data/selected_stock_daily_returns.csv", parse_dates=["Date"])


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

    if models_selected:
        returns_df = load_returns()
        performance_dict = {}
        sp500_series = None

        # Try to extract S&P 500 returns if present
        if '^GSPC' in returns_df['Ticker'].unique():
            sp500_df = returns_df[returns_df['Ticker'] == '^GSPC'].copy()
            sp500_df = sp500_df.sort_values('Date')
            sp500_df.set_index('Date', inplace=True)
            sp500_cum = (1 + sp500_df['Daily Return']).cumprod()
            sp500_series = sp500_cum.rename('Portfolio').to_frame()

        for model in models_selected:
            try:
                weights_df = load_weights(model.replace(" ", "_").lower())
                # Prepare price data: pivot returns_df to wide format with Date index and Ticker columns
                price_df = returns_df.pivot(index='Date', columns='Ticker', values='Daily Return')
                # Prepare weights: use the first available date's weights
                if 'Date' in weights_df.columns:
                    first_date = weights_df['Date'].min()
                    weights = weights_df[weights_df['Date'] == first_date].set_index('Ticker')['Weight']
                else:
                    weights = weights_df.set_index('Ticker')['Weight']
                # Align weights to price_df columns
                weights = weights.reindex(price_df.columns).fillna(0).values
                # Run backtest
                perf = run_backtest(price_df, weights, rebalance_freq=rebalance_freq, include_rf=include_rf)
                performance_dict[model] = perf
            except Exception as e:
                st.warning(f"Backtest error for {model}: {e}")

        if performance_dict:
            fig = plot_backtesting_results(performance_dict, sp500_series=sp500_series)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Unable to compute backtest for selected models.")
    else:
        st.warning("No models selected for backtesting. Please select at least one model.")

with tab3:
    st.header("Model Information")
    st.info("Below you'll find detailed descriptions, historical context, and references for each selected portfolio optimization model.")

    # Display descriptions for selected models
    for model in models_selected:
        st.subheader(f"Model: {model}")
        if model == "Modern Portfolio Theory":
            st.markdown("""
            **Modern Portfolio Theory (MPT)**  
            Developed by Harry Markowitz in 1952, MPT revolutionized investment management by introducing the concept of diversification and the efficient frontier.

            **Key Assumptions:**
            - Investors are rational and risk-averse.
            - Markets are efficient and all information is available.
            - Returns are normally distributed and risk is measured by variance.

            **How it works:**  
            MPT constructs portfolios to maximize expected return for a given level of risk, or equivalently, minimize risk for a given expected return. The set of optimal portfolios forms the *efficient frontier*.

            **Historical Note:**  
            Markowitz received the Nobel Prize in Economics in 1990 for this work.

            **References:**  
            - [Markowitz, H. (1952). Portfolio Selection. *The Journal of Finance*, 7(1), 77–91.](https://www.math.ust.hk/~maykwok/courses/ma362/07F/markowitz_JF.pdf)
            - [Investopedia: Modern Portfolio Theory](https://www.investopedia.com/terms/m/modernportfoliotheory.asp)
            """)
        elif model == "Minimum Variance":
            st.markdown("""
            **Minimum Variance Portfolio (MVP)**  
            The MVP is a special case of MPT, focusing solely on minimizing portfolio volatility, regardless of expected return.

            **Key Features:**
            - Seeks the portfolio with the lowest possible risk (variance).
            - Often used as a baseline for risk-averse investors.

            **Historical Context:**  
            The concept emerged from Markowitz's original work, and is widely used in both academic research and practical portfolio management.

            **References:**  
            - [Minimum Variance Portfolio - CFA Institute](https://www.cfainstitute.org/en/research/foundation/2010/minimum-variance-portfolios-in-the-us-equity-market)
            - [Investopedia: Minimum Variance Portfolio](https://www.investopedia.com/terms/m/minimumvarianceportfolio.asp)
            """)
        elif model == "Maximum Sharpe Ratio":
            st.markdown("""
            **Maximum Sharpe Ratio Portfolio (MSR)**  
            Also known as the Tangency Portfolio, this model seeks to maximize the Sharpe Ratio, which measures risk-adjusted return.

            **Key Features:**
            - Incorporates a risk-free asset (e.g., Treasury bills).
            - Identifies the portfolio with the highest excess return per unit of risk.

            **Historical Note:**  
            The Sharpe Ratio was introduced by William F. Sharpe in 1966, who later won the Nobel Prize in Economics.

            **References:**  
            - [Sharpe, W.F. (1966). Mutual Fund Performance. *The Journal of Business*, 39(1), 119–138.](https://www.jstor.org/stable/2351741)
            - [Investopedia: Sharpe Ratio](https://www.investopedia.com/terms/s/sharperatio.asp)
            """)
        elif model == "Equal Weight":
            st.markdown("""
            **Equal Weight Portfolio**  
            This approach assigns the same weight to each asset, regardless of its risk or expected return.

            **Key Features:**
            - Simple to implement and rebalance.
            - Provides broad diversification and avoids concentration risk.

            **Historical Context:**  
            Equal weighting is often used as a benchmark to compare more sophisticated strategies.

            **References:**  
            - [Equal Weight Portfolio - Portfolio Visualizer](https://www.portfoliovisualizer.com/faq#equal-weight)
            - [Investopedia: Equal Weight](https://www.investopedia.com/terms/e/equal-weighted-index.asp)
            """)
        elif model == "Risk Parity":
            st.markdown("""
            **Risk Parity**  
            Introduced in the late 1990s, Risk Parity allocates capital so that each asset contributes equally to overall portfolio risk.

            **Key Features:**
            - Balances risk, not capital, across assets.
            - Often leads to higher allocations to lower-risk assets (e.g., bonds).

            **Historical Note:**  
            Popularized by Bridgewater Associates, Risk Parity strategies gained prominence after the 2008 financial crisis.

            **References:**  
            - [Qian, E. (2005). Risk Parity Portfolios: Efficient Portfolios through True Diversification.](https://www.panagora.com/assets/Panagora_Risk_Parity_Portfolios.pdf)
            - [Investopedia: Risk Parity](https://www.investopedia.com/terms/r/risk-parity.asp)
            """)
        elif model == "Hierarchical Risk Parity":
            st.markdown("""
            **Hierarchical Risk Parity (HRP)**  
            Proposed by Marcos López de Prado in 2016, HRP uses hierarchical clustering to build diversified portfolios without inverting the covariance matrix.

            **Key Features:**
            - Uses machine learning to cluster assets based on correlations.
            - Allocates capital according to the hierarchical structure, improving robustness.

            **Historical Context:**  
            HRP addresses some of the limitations of traditional risk-based allocation, especially in high-dimensional settings.

            **References:**  
            - [López de Prado, M. (2016). Building Diversified Portfolios that Outperform Out-of-Sample.](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2708678)
            - [Investopedia: Hierarchical Risk Parity](https://www.investopedia.com/terms/h/hierarchical-risk-parity-hrp.asp)
            """)

with tab4:
    st.header("Export Options")
    st.info("Download portfolio allocations or summary reports.")
    st.button("Download Allocations as CSV")
    st.button("Download Summary Report as PDF")

# Sidebar: Economic Context Panel (Optional)
if st.sidebar.checkbox("Show Economic Context", value=False, key="show_econ_context"):
    st.sidebar.subheader("Economic Context")
    st.sidebar.write("Fed Funds Rate, Inflation, and GDP data will be displayed here.")

