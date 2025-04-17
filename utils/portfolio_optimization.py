import numpy as np
import pandas as pd
from pypfopt import EfficientFrontier, risk_models, expected_returns, HRPOpt 

def optimize_portfolio(df, model, include_rf=False, max_allocation=None, no_short_selling=False):

    # Ensure the index is in datetime format
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index, errors='coerce')

    # Drop rows with missing or invalid 'Ticker' or 'Daily Return'
    df = df.dropna(subset=['Ticker', 'Daily Return'])

    # Check for duplicate rows and handle them
    df = df.reset_index().drop_duplicates(subset=['Date', 'Ticker']).set_index('Date')

    # Pivot the DataFrame
    df = df.pivot(columns='Ticker', values='Daily Return')

    # Calculate expected returns and covariance matrix
    mu = df.mean()
    S = df.cov()
    # Define hypothetical risk-free rate if flagged
    risk_free_rate = 0.02 if include_rf else None

    if model == "Modern Portfolio Theory":
        ef = EfficientFrontier(mu, S)
        weights = ef.max_sharpe() if not include_rf else ef.max_sharpe(risk_free_rate=risk_free_rate)
        if max_allocation:
            ef.add_constraint(lambda w: w <= max_allocation)
        if no_short_selling:
            ef.add_constraint(lambda w: w >= 0)
        portfolio_return, portfolio_volatility, _ = ef.portfolio_performance()
    elif model == "Minimum Variance":
        ef = EfficientFrontier(mu, S)
        weights = ef.min_volatility()
        if max_allocation:
            ef.add_constraint(lambda w: w <= max_allocation)
        if no_short_selling:
            ef.add_constraint(lambda w: w >= 0)
        portfolio_return, portfolio_volatility, _ = ef.portfolio_performance()
    elif model == "Maximum Sharpe Ratio":
        ef = EfficientFrontier(mu, S)
        weights = ef.max_sharpe(risk_free_rate=risk_free_rate if include_rf else None)
        if max_allocation:
            ef.add_constraint(lambda w: w <= max_allocation)
        if no_short_selling:
            ef.add_constraint(lambda w: w >= 0)
        portfolio_return, portfolio_volatility, _ = ef.portfolio_performance()
    elif model == "Equal Weight":
        weights = np.ones(len(df.columns)) / len(df.columns)  # Ensure weights is a numpy array
        portfolio_return = np.dot(weights, mu)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(S, weights)))
        weights = pd.Series(weights, index=df.columns)  # Convert weights to a pandas Series
    elif model == "Risk Parity":
        asset_volatility = np.sqrt(np.diag(S))
        inverse_volatility = 1 / asset_volatility
        weights = inverse_volatility / np.sum(inverse_volatility)  # Ensure weights is a numpy array
        portfolio_return = np.dot(weights, mu)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(S, weights)))
        weights = pd.Series(weights, index=df.columns)  # Convert weights to a pandas Series
    elif model == "Hierarchical Risk Parity":
        hrp = HRPOpt(df)
        weights = hrp.optimize()
        weights = pd.Series(weights)  # Ensure weights is a pandas Series
        portfolio_return = np.dot(weights, mu)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(S, weights)))
    else:
        raise ValueError(f"Unsupported model: {model}")
    
    # Ensure weights are returned as a pandas Series for consistency
    weights = pd.Series(weights, index=df.columns) if not isinstance(weights, pd.Series) else weights
    return weights, portfolio_return, portfolio_volatility
