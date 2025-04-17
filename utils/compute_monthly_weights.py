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

    # Ensure all dates in the range are present, but only use dates available in the CSV
    data = data.sort_index()  # Ensure data is sorted by Date

    # Filter data for the specified range
    data = data.loc["2004-01-01":end_date]

    # Generate four-month intervals
    dates = pd.date_range(start=start_date, end=end_date, freq='4MS')  # Four-month start dates

    weights_list = []

    for date_i in dates:
        # Find the closest available date in the dataset

        # Use all data up to the closest date for training
        training_data = data.loc[:date_i]  # Ensure slicing works with Timestamp index

        for model in models:
            try:
                weights, _, _ = optimize_portfolio(training_data, model, include_rf=False)
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

if __name__ == "__main__":
    # Load historical weekly returns data
    data_path = os.path.join("data", "selected_stock_daily_returns.csv")
    data = pd.read_csv(data_path, index_col="Date", parse_dates=True)

    # Check if the data covers the required date range
    start_date = pd.Timestamp("2004-01-01")
    end_date = pd.Timestamp("2023-12-01")
    if data.index.min() > start_date or data.index.max() < end_date:
        raise ValueError(f"The data must cover the date range from {start_date} to {end_date}.")

    # Exclude the S&P500 ticker
    data = data[data["Ticker"] != "^GSPC"]

    # Deduplicate data by grouping by Date and Ticker, then aggregating (e.g., summing or averaging)
    data = data.groupby(["Date", "Ticker"]).mean().reset_index()

    # Set the Date column as the index for reindexing
    data = data.set_index("Date")

    # Ensure all dates in the range are present, but only use dates available in the CSV
    data = data.sort_index()  # Ensure data is sorted by Date

    # Define the model(s) to iterate over
    models = ["Minimum Variance"]  # Add more models to this list if needed

    # Compute weights for each model
    for model in models:
        print(f"Processing model: {model}")
        try:
            print(f"Input data: {data}")
            print(f"Calling compute_four_month_weights with include_rf=True")
            weights = compute_four_month_weights(data, models, include_rf=True)  # Pass the correct model
        except Exception as e:
            print(f"Error computing weights for model {model}: {e}")
            weights = None

        # Save weights to a separate CSV file for each model
        output_path = os.path.join("data", f"{model.lower().replace(' ', '_')}_weights.csv")
        if weights is not None:
            weights.to_csv(output_path, index=False)
            print(f"Weights saved to {output_path}")