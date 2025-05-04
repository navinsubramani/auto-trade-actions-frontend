# Create a yfinance client class to fetch stock data

import os
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class YFinanceClient:

    def __init__(self):
        pass

    def fetch_data(self, ticker):
        """
        Fetches historical stock data for a given ticker.
        """
        try:
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
            data = yf.download(ticker, start=start_date, end=end_date, interval='5m')
            data.columns = data.columns.get_level_values(0)
            data.reset_index(inplace=True)
            # drop the index column
            data = data.reset_index(drop=True)

            return data
        except Exception as e:
            print(f"An error occurred while fetching data for {ticker}: {e}")
            return None
