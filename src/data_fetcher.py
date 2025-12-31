"""
Data Fetcher Module
Fetches and manages Tesla stock data
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os


class DataFetcher:
    """Fetch and manage Tesla stock data"""
    
    def __init__(self, symbol='TSLA', data_dir='data'):
        """
        Initialize DataFetcher
        
        Args:
            symbol: Stock symbol (default: TSLA)
            data_dir: Directory to store data
        """
        self.symbol = symbol
        self.data_dir = data_dir
        self.data = None
        
        # Create data directory if it doesn't exist
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def fetch_data(self, start_date=None, end_date=None, period='2y', save=True):
        """
        Fetch stock data from Yahoo Finance
        
        Args:
            start_date: Start date (YYYY-MM-DD) or None
            end_date: End date (YYYY-MM-DD) or None
            period: Period to fetch if dates not specified (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            save: Whether to save data to CSV
            
        Returns:
            DataFrame with stock data
        """
        print(f"Fetching {self.symbol} data...")
        
        try:
            if start_date and end_date:
                self.data = yf.download(self.symbol, start=start_date, end=end_date, progress=False)
            else:
                self.data = yf.download(self.symbol, period=period, progress=False)
            
            if self.data.empty:
                raise ValueError("No data fetched")
            
            # Clean column names (remove multi-index if present)
            if isinstance(self.data.columns, pd.MultiIndex):
                self.data.columns = [col[0] for col in self.data.columns]
            
            # Add useful columns
            self.data['Returns'] = self.data['Close'].pct_change()
            self.data['Log_Returns'] = np.log(self.data['Close'] / self.data['Close'].shift(1))
            
            print(f"Successfully fetched {len(self.data)} rows of data")
            print(f"Date range: {self.data.index[0]} to {self.data.index[-1]}")
            
            if save:
                self.save_data()
            
            return self.data
            
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None
    
    def load_data(self, filename=None):
        """
        Load data from CSV file
        
        Args:
            filename: CSV filename (default: TSLA_data.csv)
            
        Returns:
            DataFrame with stock data
        """
        if filename is None:
            filename = f"{self.symbol}_data.csv"
        
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            self.data = pd.read_csv(filepath, index_col=0, parse_dates=True)
            print(f"Loaded data from {filepath}")
            return self.data
        except Exception as e:
            print(f"Error loading data: {e}")
            return None
    
    def save_data(self, filename=None):
        """
        Save data to CSV file
        
        Args:
            filename: CSV filename (default: TSLA_data.csv)
        """
        if self.data is None:
            print("No data to save")
            return
        
        if filename is None:
            filename = f"{self.symbol}_data.csv"
        
        filepath = os.path.join(self.data_dir, filename)
        self.data.to_csv(filepath)
        print(f"Data saved to {filepath}")
    
    def get_latest_data(self, days=1):
        """
        Get latest N days of data
        
        Args:
            days: Number of days to fetch
            
        Returns:
            DataFrame with latest data
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        return self.fetch_data(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            save=False
        )
    
    def update_data(self):
        """
        Update existing data with latest prices
        
        Returns:
            Updated DataFrame
        """
        if self.data is None:
            print("No existing data. Fetching new data...")
            return self.fetch_data()
        
        last_date = self.data.index[-1]
        latest_data = self.get_latest_data(days=7)
        
        if latest_data is not None:
            # Combine data, removing duplicates
            self.data = pd.concat([self.data, latest_data])
            self.data = self.data[~self.data.index.duplicated(keep='last')]
            self.data.sort_index(inplace=True)
            self.save_data()
            print(f"Data updated from {last_date} to {self.data.index[-1]}")
        
        return self.data
    
    def get_info(self):
        """
        Get stock information
        
        Returns:
            Dictionary with stock info
        """
        ticker = yf.Ticker(self.symbol)
        return ticker.info
    
    def summary(self):
        """Print data summary"""
        if self.data is None:
            print("No data available")
            return
        
        print("\n" + "="*50)
        print(f"TESLA ({self.symbol}) DATA SUMMARY")
        print("="*50)
        print(f"Total rows: {len(self.data)}")
        print(f"Date range: {self.data.index[0]} to {self.data.index[-1]}")
        print(f"\nLatest Close Price: ${self.data['Close'].iloc[-1]:.2f}")
        print(f"52-Week High: ${self.data['High'].tail(252).max():.2f}")
        print(f"52-Week Low: ${self.data['Low'].tail(252).min():.2f}")
        print(f"\nData columns: {list(self.data.columns)}")
        print("\nFirst 3 rows:")
        print(self.data.head(3))
        print("\nLast 3 rows:")
        print(self.data.tail(3))
        print("="*50 + "\n")


if __name__ == "__main__":
    # Test the data fetcher
    fetcher = DataFetcher()
    data = fetcher.fetch_data(period='2y')
    fetcher.summary()
