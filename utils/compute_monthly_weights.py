import pandas as pd
import os
from datetime import datetime
from utils.portfolio_optimization import optimize_portfolio

def compute_quarterly_weights(data, models, start_date, end_date, include_rf=False):
    """
    Compute quarterly portfolio weights for each model.

    Args:
        data (pd.DataFrame): Historical price data for assets.
        models (list): List of optimization models to compute weights for.
        start_date (str): Start date for backtesting (YYYY-MM-DD).
        end_date (str): End date for backtesting (YYYY-MM-DD).
        include_rf (bool): Whether to include a risk-free asset.

    Returns:
        dict: Dictionary with model names as keys and DataFrames of weights as values.
    """
    quarterly_weights = {model: [] for model in models}
    dates = pd.date_range(start=start_date, end=end_date, freq='QS')  # Quarterly start dates

    for date in dates:
        # Use all data up to the current date for training
        training_data = data[:date]
        
        for model in models:
            try:
                weights, _, _ = optimize_portfolio(training_data, model, include_rf=include_rf)
                quarterly_weights[model].append((date, weights))
            except Exception as e:
                print(f"Error optimizing for model {model} on {date}: {e}")

    # Convert to DataFrame for each model
    for model in models:
        quarterly_weights[model] = pd.DataFrame(
            quarterly_weights[model], columns=["Date", "Weights"]
        ).set_index("Date")

    return quarterly_weights

if __name__ == "__main__":
    # Example usage
    # Load historical price data
    data_path = os.path.join("data", "historical_prices.csv")
    data = pd.read_csv(data_path, index_col="Date", parse_dates=True)

    # Define models and date range
    models = ["Modern Portfolio Theory", "Minimum Variance", "Maximum Sharpe Ratio", "Equal Weight", "Risk Parity", "Hierarchical Risk Parity"]
    start_date = "2010-01-01"
    end_date = "2020-12-31"

    # Compute weights
    weights = compute_quarterly_weights(data, models, start_date, end_date, include_rf=True)

    # Save weights to CSV files
    output_dir = "data/weights"
    os.makedirs(output_dir, exist_ok=True)
    for model, df in weights.items():
        df.to_csv(os.path.join(output_dir, f"{model.replace(' ', '_').lower()}_weights.csv"))