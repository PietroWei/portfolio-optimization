import pandas as pd
import yfinance as yf
from datetime import datetime

def save_selected_stock_daily_returns(tickers, start_date="2004-01-01", end_date="2024-01-01"):
    """
    Fetch historical data for selected stocks and save their daily returns.
    Args:
        tickers (list): A list of stock tickers to fetch data for.
        start_date (str): The start date for fetching data (format: YYYY-MM-DD).
        end_date (str): The end date for fetching data (format: YYYY-MM-DD).
    Returns:
        pd.DataFrame: A DataFrame containing the selected stocks and their daily returns.
    """
    # Fetch historical data with error handling
    try:
        data = yf.download(tickers, start=start_date, end=end_date, auto_adjust=False)["Adj Close"]
    except Exception as e:
        print(f"Error downloading data: {e}")
        return pd.DataFrame(columns=["Date", "Ticker", "Daily Return"])
    
    # Drop columns with all NaN values (tickers with no data)
    data = data.dropna(axis=1, how="all")
    
    # Calculate daily returns
    daily_returns = data.pct_change().dropna(how="all")
    
    # Reshape the data for saving
    daily_returns = daily_returns.reset_index().melt(id_vars=["Date"], var_name="Ticker", value_name="Daily Return")
    
    # Save daily returns to a CSV file
    daily_returns.to_csv("data/selected_stock_daily_returns.csv", index=False)
    return daily_returns

# Example usage
if __name__ == "__main__":
    # Define the list of selected tickers
    selected_tickers = [
        "AAPL", "NFLX", "MNST", "NVDA", "AMZN", "ISRG", "BKNG", "ODFL", "SBAC",
        "CPRT", "REGN", "WST", "TYL", "ORLY", "VRTX", "CACC", "TSCO", "RAI", 
        "NVR", "IDXX", "^GSPC" 
    ]
    
    # Save daily performances of selected stocks
    selected_stock_daily_returns = save_selected_stock_daily_returns(
        selected_tickers, start_date="2004-01-01", end_date="2024-01-01"
    )
    print(selected_stock_daily_returns)
