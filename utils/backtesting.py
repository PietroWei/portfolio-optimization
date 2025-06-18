import pandas as pd
import numpy as np

def run_backtest(daily_returns, weights_df, rebalance_freq, include_rf):
    """
    daily_returns: DataFrame with columns ['Date', 'Ticker', 'Daily Return']
    weights_df: DataFrame with index as rebalance dates, columns as tickers, values as weights
    rebalance_freq: "Quarterly", "Yearly", or "None"
    include_rf: bool, whether to include risk-free rate
    Returns: DataFrame with index as trading dates, column 'Portfolio'
    """
    # Pivot returns to wide format: index=Date, columns=Ticker
    returns_wide = daily_returns.pivot(index='Date', columns='Ticker', values='Daily Return')
    # Convert index to datetime and sort
    returns_wide.index = pd.to_datetime(returns_wide.index)
    returns_wide = returns_wide.sort_index()
    returns_wide = returns_wide.fillna(0)

    # Ensure weights_df index is datetime and sorted
    weights_df = weights_df.copy()
    weights_df.index = pd.to_datetime(weights_df.index)
    weights_df = weights_df.sort_index()

    # Determine rebalancing dates
    if rebalance_freq == "Quarterly":
        rebal_dates = weights_df.index
    elif rebalance_freq == "Yearly":
        rebal_dates = weights_df.index[::4]
    else:  # "None" or buy-and-hold
        rebal_dates = pd.Index([weights_df.index[0]])

    # Map rebalance dates to trading dates
    trading_dates = returns_wide.index
    print("DEBUG trading_dates:", trading_dates, "Length:", len(trading_dates))
    if len(trading_dates) == 0:
        raise ValueError("No trading dates found in returns data. Check input DataFrame.")
    mapped_rebal_dates = []
    for d in rebal_dates:
        idx = trading_dates.searchsorted(d)
        if idx < len(trading_dates):
            mapped_rebal_dates.append(trading_dates[idx])
    mapped_rebal_dates = sorted(set(mapped_rebal_dates))
    if mapped_rebal_dates[0] != trading_dates[0]:
        mapped_rebal_dates = [trading_dates[0]] + mapped_rebal_dates
    if mapped_rebal_dates[-1] != trading_dates[-1]:
        mapped_rebal_dates.append(trading_dates[-1])

    # Prepare weights for each rebalancing period
    weights_list = []
    for d in mapped_rebal_dates[:-1]:
        # Find last available weights <= d
        valid_dates = weights_df.index[weights_df.index <= d]
        if len(valid_dates) > 0:
            last_date = valid_dates[-1]
            w = weights_df.loc[last_date].reindex(returns_wide.columns).fillna(0).values
        else:
            w = np.ones(len(returns_wide.columns)) / len(returns_wide.columns)
        weights_list.append(w)

    # Backtest loop
    portfolio = pd.Series(index=trading_dates, dtype=float)
    portfolio.iloc[0] = 1.0
    for i in range(len(mapped_rebal_dates)-1):
        start = mapped_rebal_dates[i]
        end = mapped_rebal_dates[i+1]
        w = weights_list[i]
        period_idx = trading_dates.get_loc(start)
        next_idx = trading_dates.get_loc(end)
        for j in range(period_idx+1, next_idx+1):
            prev_val = portfolio.iloc[j-1]
            ret = (returns_wide.iloc[j] * w).sum()
            if include_rf:
                ret += 0.02 / 252
            portfolio.iloc[j] = prev_val * (1 + ret)

    return pd.DataFrame({'Portfolio': portfolio})