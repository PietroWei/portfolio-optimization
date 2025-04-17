import pandas as pd
import yfinance as yf
from datetime import datetime

def save_selected_stock_monthly_returns(tickers, start_date="2004-01-01", end_date="2024-01-01"):
    """
    Fetch historical data for selected stocks and save their monthly returns.
    Args:
        tickers (list): A list of stock tickers to fetch data for.
        start_date (str): The start date for fetching data (format: YYYY-MM-DD).
        end_date (str): The end date for fetching data (format: YYYY-MM-DD).
    Returns:
        pd.DataFrame: A DataFrame containing the selected stocks and their monthly returns.
    """
    # Fetch historical data with error handling
    try:
        data = yf.download(tickers, start=start_date, end=end_date, auto_adjust=False)["Adj Close"]
    except Exception as e:
        print(f"Error downloading data: {e}")
        return pd.DataFrame(columns=["Date", "Ticker", "Monthly Return"])
    
    # Drop columns with all NaN values (tickers with no data)
    data = data.dropna(axis=1, how="all")
    
    # Resample data to get monthly closing prices (on the 1st of each month)
    monthly_data = data.resample('MS').first()
    
    # Calculate monthly returns
    monthly_returns = monthly_data.pct_change().dropna(how="all")
    
    # Reshape the data for saving
    monthly_returns = monthly_returns.reset_index().melt(id_vars=["Date"], var_name="Ticker", value_name="Monthly Return")
    
    # Save monthly returns to a CSV file
    monthly_returns.to_csv("data/selected_stock_monthly_returns.csv", index=False)
    return monthly_returns

def save_selected_stock_weekly_returns(tickers, start_date="2004-01-01", end_date="2024-01-01"):
    """
    Fetch historical data for selected stocks and save their weekly returns.
    Args:
        tickers (list): A list of stock tickers to fetch data for.
        start_date (str): The start date for fetching data (format: YYYY-MM-DD).
        end_date (str): The end date for fetching data (format: YYYY-MM-DD).
    Returns:
        pd.DataFrame: A DataFrame containing the selected stocks and their weekly returns.
    """
    # Fetch historical data with error handling
    try:
        data = yf.download(tickers, start=start_date, end=end_date, auto_adjust=False)["Adj Close"]
    except Exception as e:
        print(f"Error downloading data: {e}")
        return pd.DataFrame(columns=["Date", "Ticker", "Weekly Return"])
    
    # Drop columns with all NaN values (tickers with no data)
    data = data.dropna(axis=1, how="all")
    
    # Resample data to get weekly closing prices (on Fridays)
    weekly_data = data.resample('W-FRI').last()
    
    # Calculate weekly returns
    weekly_returns = weekly_data.pct_change().dropna(how="all")
    
    # Reshape the data for saving
    weekly_returns = weekly_returns.reset_index().melt(id_vars=["Date"], var_name="Ticker", value_name="Weekly Return")
    
    # Save weekly returns to a CSV file
    weekly_returns.to_csv("data/selected_stock_weekly_returns.csv", index=False)
    return weekly_returns

# Example usage
if __name__ == "__main__":
    # Define the list of selected tickers
    selected_tickers = [
        "AAPL", "NFLX", "MNST", "NVDA", "AMZN", "ISRG", "BKNG", "ODFL", "SBAC",
        "CPRT", "REGN", "WST", "TYL", "ORLY", "VRTX", "CACC", "TSCO", "RAI", 
        "NVR", "IDXX", "^GSPC" 
    ]
    
    # Save monthly performances of selected stocks
    selected_stock_monthly_returns = save_selected_stock_monthly_returns(
        selected_tickers, start_date="2004-01-01", end_date="2024-01-01"
    )
    print(selected_stock_monthly_returns)
    
    # Save weekly performances of selected stocks
    selected_stock_weekly_returns = save_selected_stock_weekly_returns(
        selected_tickers, start_date="2004-01-01", end_date="2024-01-01"
    )
    print(selected_stock_weekly_returns)
