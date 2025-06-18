import plotly.express as px
import plotly.graph_objects as go
import pandas as pd  # Add this import if not already present
import numpy as np

def plot_efficient_frontier(data, model, include_rf):
    # Validate input data
    required_columns = ['risk', 'return', 'sharpe_ratio']
    if not all(col in data.columns for col in required_columns):
        raise ValueError(f"Input data must contain the following columns: {required_columns}")

    # Enhanced Efficient Frontier plotting with legend
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data['risk'], 
        y=data['return'], 
        mode="markers", 
        name="Portfolios",
        marker=dict(size=8, color=data['sharpe_ratio'], colorscale="Viridis", showscale=True)
    ))
    fig.add_trace(go.Scatter(
        x=[0, 1], 
        y=[0, 1], 
        mode="lines", 
        name="Efficient Frontier"
    ))
    fig.update_layout(
        title=f"Efficient Frontier ({model})",
        xaxis_title="Risk (Standard Deviation)",
        yaxis_title="Return",
        legend_title="Legend"
    )
    return fig  # Return figure instead of showing it

def plot_allocation(weights, threshold=0.03):
    # Ensure weights are numeric
    if not isinstance(weights, pd.Series):
        raise ValueError("Weights must be a pandas Series.")
    if not pd.api.types.is_numeric_dtype(weights):
        raise ValueError("Weights must contain numeric values.")

    # Group small allocations into "Other"
    weights = weights.copy()
    small_allocations = weights[weights < threshold]
    if not small_allocations.empty:
        other_sum = small_allocations.sum()
        weights = weights[weights >= threshold]
        if other_sum > 0:
            weights["Other"] = other_sum

    # Handle case where no weights meet the threshold
    if weights.empty:
        raise ValueError("No weights meet the threshold for visualization.")

    # Enhanced pie chart with legend
    fig = px.pie(
        values=weights, 
        names=weights.index, 
        title="Portfolio Allocation",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_traces(textinfo="percent+label")
    fig.update_layout(
        legend_title="Assets",
        showlegend=True
    )
    return fig  # Return figure instead of showing it

def plot_rolling_metrics(data, window=30):
    # Enhanced rolling metrics visualization with legends
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.index, 
        y=data['rolling_volatility'], 
        mode="lines", 
        name="Rolling Volatility"
    ))
    fig.add_trace(go.Scatter(
        x=data.index, 
        y=data['rolling_sharpe'], 
        mode="lines", 
        name="Rolling Sharpe Ratio"
    ))
    fig.update_layout(
        title=f"Rolling Metrics (Window: {window} days)",
        xaxis_title="Date",
        yaxis_title="Metric Value",
        legend_title="Metrics"
    )
    fig.show()

def plot_quarterly_return_histogram(data, portfolios):
    """
    Plot a histogram of quarterly returns for up to three portfolio decisions.

    Parameters:
    - data: pd.DataFrame containing daily returns with columns ['Date', 'Ticker', 'Daily Return'].
    - portfolios: List of portfolio names to include in the histogram (max 3).

    Returns:
    - fig: Plotly figure object.
    """
    # Load minimum variance weights
    weights_df = pd.read_csv('/workspaces/portfolio-optimization/data/minimum_variance_weights.csv')
    
    # Match weights to the first date in the dataset
    first_date = data['Date'].min()
    weights = weights_df.loc[weights_df['Date'] == first_date].iloc[0, 1:].values  # Assuming weights_df has a 'Date' column

    # Compute weighted daily returns
    data['Weighted Return'] = data['Daily Return'] * weights[data['Ticker']].values

    # Resample to quarterly returns
    data['Date'] = pd.to_datetime(data['Date'])
    data.set_index('Date', inplace=True)
    quarterly_returns = data['Weighted Return'].resample('Q').sum()

    # Validate portfolios
    if not isinstance(data, pd.DataFrame):
        raise ValueError("Data must be a pandas DataFrame.")
    if len(portfolios) > 3:
        raise ValueError("A maximum of three portfolios can be plotted.")
    if not all(portfolio in data.columns for portfolio in portfolios):
        raise ValueError("All specified portfolios must exist in the data.")

    # Plot histogram of quarterly returns
    fig = go.Figure()
    for portfolio in portfolios:
        fig.add_trace(go.Histogram(
            x=quarterly_returns,
            name=portfolio,
            opacity=0.75
        ))

    fig.update_layout(
        title="Quarterly Return Histogram",
        xaxis_title="Quarterly Return",
        yaxis_title="Frequency",
        barmode="overlay",
        legend_title="Portfolios"
    )
    fig.update_traces(opacity=0.6)
    return fig  # Return figure instead of showing it



def plot_monthly_weights(weights_df):
    """
    Plot monthly portfolio weights for each model.

    Parameters:
    - weights_df: pd.DataFrame containing monthly weights with columns ['Date', 'Model', 'Ticker', 'Weight'].

    Returns:
    - fig: Plotly figure object.
    """
    # Validate input DataFrame
    if not isinstance(weights_df, pd.DataFrame):
        raise ValueError("weights_df must be a pandas DataFrame.")
    if not all(col in weights_df.columns for col in ['Date', 'Model', 'Ticker', 'Weight']):
        raise ValueError("weights_df must contain 'Date', 'Model', 'Ticker', and 'Weight' columns.")

    # Create a pivot table for plotting
    pivot_df = weights_df.pivot_table(index='Date', columns=['Model', 'Ticker'], values='Weight').fillna(0)

    # Create a line plot for each model
    fig = go.Figure()
    for model in pivot_df.columns.levels[0]:
        model_data = pivot_df[model]
        fig.add_trace(go.Scatter(
            x=model_data.index,
            y=model_data.sum(axis=1),  # Sum across tickers for each model
            mode='lines+markers',
            name=model
        ))

    fig.update_layout(
        title="Monthly Portfolio Weights by Model",
        xaxis_title="Date",
        yaxis_title="Weight",
        legend_title="Models"
    )
    
    return fig  # Return figure instead of showing it

def plot_backtesting_results(performance_dict, sp500_series=None):
    """
    Plot backtesting results for multiple models and optionally the S&P 500.

    Parameters:
    - performance_dict: dict of {model_name: pd.DataFrame} with 'Portfolio' column and DatetimeIndex.
    - sp500_series: pd.DataFrame or pd.Series for S&P 500 cumulative returns (optional).

    Returns:
    - fig: Plotly figure object.
    """
    import plotly.graph_objects as go

    fig = go.Figure()
    for model, perf in performance_dict.items():
        # Always expect perf to be a DataFrame with 'Portfolio' column
        y = perf['Portfolio'] if isinstance(perf, pd.DataFrame) and 'Portfolio' in perf.columns else perf
        fig.add_trace(go.Scatter(
            x=y.index, y=y.values, mode='lines', name=model
        ))
    if sp500_series is not None:
        y = sp500_series['Portfolio'] if isinstance(sp500_series, pd.DataFrame) and 'Portfolio' in sp500_series.columns else sp500_series
        fig.add_trace(go.Scatter(
            x=y.index, y=y.values, mode='lines', name='S&P 500', line=dict(dash='dash')
        ))
    fig.update_layout(
        title="Backtesting: Selected Models vs S&P 500",
        xaxis_title="Date",
        yaxis_title="Cumulative Return",
        legend_title="Portfolio"
    )
    return fig