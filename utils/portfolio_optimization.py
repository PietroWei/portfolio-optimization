import numpy as np
import pandas as pd
from pypfopt import EfficientFrontier, risk_models, expected_returns, HRPOpt 

def optimize_portfolio(data, model, include_rf=False, max_allocation=None, no_short_selling=False):
    # Calculate expected returns and covariance matrix
    mu = expected_returns.mean_historical_return(data)
    S = risk_models.sample_cov(data)
    
    if model == "Modern Portfolio Theory":
        ef = EfficientFrontier(mu, S)
        weights = ef.max_sharpe() if not include_rf else ef.max_sharpe(risk_free_rate=0.01)
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
        weights = ef.max_sharpe()
        if max_allocation:
            ef.add_constraint(lambda w: w <= max_allocation)
        if no_short_selling:
            ef.add_constraint(lambda w: w >= 0)
        portfolio_return, portfolio_volatility, _ = ef.portfolio_performance()
    elif model == "Equal Weight":
        weights = pd.Series(np.ones(len(data.columns)) / len(data.columns), index=data.columns)
        portfolio_return = np.dot(weights, mu)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(S, weights)))
    elif model == "Risk Parity":
        asset_volatility = np.sqrt(np.diag(S))
        inverse_volatility = 1 / asset_volatility
        weights = inverse_volatility / np.sum(inverse_volatility)
        portfolio_return = np.dot(weights, mu)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(S, weights)))
    elif model == "Hierarchical Risk Parity":
        hrp = HRPOpt(data)
        weights = hrp.optimize()
        portfolio_return = np.dot(weights, mu)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(S, weights)))
    else:
        raise ValueError(f"Unsupported model: {model}")
    
    # Ensure weights are returned as a pandas Series for consistency
    weights = pd.Series(weights, index=data.columns) if not isinstance(weights, pd.Series) else weights
    return weights, portfolio_return, portfolio_volatility
