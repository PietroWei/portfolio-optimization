import pandas as pd
import numpy as np

def run_backtest(data, model, weights, rebalance_freq, include_rf):
    # Simulate returns
    daily_returns = data.pct_change()
    weighted_returns = daily_returns.dot(weights)
    
    # Include risk-free asset if specified
    if include_rf:
        risk_free_rate = 0.02 / 252  # Approximate daily risk-free rate
        weighted_returns += risk_free_rate

    # Apply rebalancing logic
    if rebalance_freq == "Monthly":
        rebalance_dates = data.resample('M').first().index
    elif rebalance_freq == "Quarterly":
        rebalance_dates = data.resample('Q').first().index
    elif rebalance_freq == "Yearly":
        rebalance_dates = data.resample('A').first().index
    else:
        rebalance_dates = []

    # Adjust weights on rebalancing dates
    if rebalance_dates:
        for date in rebalance_dates:
            weights = model.optimize(data.loc[:date])  # Hypothetical optimization logic
            weighted_returns.loc[date:] = daily_returns.loc[date:].dot(weights)

    # Backtest portfolio performance
    performance = pd.DataFrame(index=data.index)
    performance['Portfolio'] = (1 + weighted_returns).cumprod()

    # Calculate additional metrics (e.g., Sharpe Ratio, Volatility)
    performance['Rolling Sharpe Ratio'] = (
        weighted_returns.rolling(window=252).mean() / weighted_returns.rolling(window=252).std()
    ) * np.sqrt(252)
    performance['Rolling Volatility'] = weighted_returns.rolling(window=252).std() * np.sqrt(252)

    # Display final portfolio performance
    return performance