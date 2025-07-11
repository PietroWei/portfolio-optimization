import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from datetime import datetime, timedelta
from utils.portfolio_optimization import optimize_portfolio


def compute_four_month_weights(data, models, include_rf=False):
    """
    Compute portfolio weights for each model every four months for the specified date range.

    Args:
        data (pd.DataFrame): Historical price data for assets.
        models (list): List of optimization models to compute weights for.
        include_rf (bool): Whether to include a risk-free asset.

    Returns:
        pd.DataFrame: DataFrame with weights for all models.
    """
    # Define the date range
    start_date = pd.Timestamp("2014-01-01")
    end_date = pd.Timestamp("2024-12-01")

    # Filter data for the specified range
    data = data[(data.index >= pd.Timestamp("2004-01-01")) & (data.index <= end_date)]

    # Generate four-month intervals
    dates = pd.date_range(start=start_date, end=end_date, freq='4MS')  # Four-month start dates

    weights_list = []

    for date_i in dates:
        # Usa solo gli ultimi 4 mesi di dati per il training
        window_start = date_i - pd.DateOffset(months=12)
        training_data = data[(data.index > window_start) & (data.index <= date_i)]
        for model in models:
            try:
                weights, _, _ = optimize_portfolio(training_data, model, include_rf=include_rf)
                weights_list.append({
                    "Date": date_i,
                    "Model": model,
                    **weights
                })
            except Exception as e:
                print(f"Error optimizing for model {model} on {date_i}: {e}")

    # Convert to a single DataFrame
    weights_df = pd.DataFrame(weights_list)

    return weights_df

def compute_rolling_weights(data, models, window_months=4, start_date=None, end_date=None, include_rf=False):
    """
    Calcola i pesi usando una finestra mobile di window_months mesi.

    Args:
        data (pd.DataFrame): Historical price data for assets.
        models (list): List of optimization models to compute weights for.
        window_months (int): The number of months for the rolling window.
        start_date (str): The start date for the analysis (format: 'YYYY-MM-DD').
        end_date (str): The end date for the analysis (format: 'YYYY-MM-DD').
        include_rf (bool): Whether to include a risk-free asset.

    Returns:
        pd.DataFrame: DataFrame with weights for all models.
    """
    if start_date is None:
        start_date = pd.Timestamp("2014-01-01")
    if end_date is None:
        end_date = pd.Timestamp("2024-12-01")
    data = data[(data.index >= pd.Timestamp("2004-01-01")) & (data.index <= end_date)]
    # Intervallo di rebalance: ogni window_months mesi
    dates = pd.date_range(start=start_date, end=end_date, freq=f'{window_months}MS')
    weights_list = []
    for date_i in dates:
        window_start = date_i - pd.DateOffset(months=window_months)
        training_data = data[(data.index > window_start) & (data.index <= date_i)]
        for model in models:
            try:
                weights, _, _ = optimize_portfolio(training_data, model, include_rf=include_rf)
                weights_list.append({
                    "Date": date_i,
                    "Model": model,
                    **weights
                })
            except Exception as e:
                print(f"Error optimizing for model {model} on {date_i}: {e}")
    weights_df = pd.DataFrame(weights_list)
    return weights_df

if __name__ == "__main__":
    # Load historical daily returns data
    data_path = os.path.join("data", "selected_stock_daily_returns.csv")
    data = pd.read_csv(data_path, parse_dates=["Date"])

    # Exclude the S&P500 ticker
    data = data[data["Ticker"] != "^GSPC"]

    # Deduplicate data by grouping by Date and Ticker, then averaging
    data = data.groupby(["Date", "Ticker"], as_index=False).mean()

    # Rinomina la colonna dei rendimenti medi se necessario
    if 'Daily Return' not in data.columns:
        # Prova a trovare la colonna dei rendimenti
        for col in data.columns:
            if 'return' in col.lower():
                data = data.rename(columns={col: 'Daily Return'})
                break

    # Imposta l'indice su Date
    data = data.set_index('Date')

    # Define the model(s) to iterate over
    models = ["Minimum Variance","Modern Portfolio Theory","Maximum Sharpe Ratio","Risk Parity","Hierarchical Risk Parity"]
    # Compute weights for each model
    for model in models:
        print(f"Processing model: {model}")
        try:
            print(f"Input data: {data.head()}")
            print(f"Calling compute_four_month_weights with include_rf=False")
            weights = compute_four_month_weights(data, [model], include_rf=False)
        except Exception as e:
            print(f"Error computing weights for model {model}: {e}")
            weights = None
        # Save weights to a separate CSV file for each model
        output_path = os.path.join("data", f"{model.lower().replace(' ', '_')}_weights.csv")
        if weights is not None:
            weights.to_csv(output_path, index=False)
            print(f"Weights saved to {output_path}")