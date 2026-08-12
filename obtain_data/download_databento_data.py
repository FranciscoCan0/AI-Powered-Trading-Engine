import databento as db
import pandas as pd
from datetime import datetime, timedelta
import os


# Set the enviroment variable for the databento API key
# os.environ['DATABENTO_API_KEY'] = 'db-V7DJeDUDm5vuT3nVxPFyqaKtbMwh6'

# Initialize the historical client.
# It automatically uses the DATABENTO_API_KEY environment variable.
# client = db.Historical()

# Define the time range for 3 years, starting 3 days ago
end_time = datetime.utcnow() - timedelta(days=3)
start_time = end_time - timedelta(days=7*356)

tickers = ["AAPL", "NVDA", "AMZN", #TECH
           "AXP", "BRK-B", "JPM", #BANKING
           "JNJ", "PFE", "UNH", #HEALTHCARE
           "PG", "WMT", "KO", #RETAIL
           "GE", "CAT", "LMT", #INDUSTRIAL/AEROSPACE
           "SONY", "NVO",  #INTERNATIONAL
           "SPY", "VOO", "IVV", "QQQ"] #ETFs
# Request OHLCV-5m data
data = client.timeseries.get_range(
    dataset="XNAS.ITCH",        # Example dataset ID for CME Globex futures
    schema="ohlcv-1m",          # Requesting 5-minute OHLCV bars
    symbols=["AAPL", "NVDA", "MSFT", "META", "SPY", "NKE", "AXP", "BAC"],
    start=start_time,           # Start time (inclusive)
    end=end_time,               # End time (exclusive)
)

# Convert the results to a pandas DataFrame and the time stamp in UTC (no daylight savings)
df = data.to_df(tz="UTC")
df = df.reset_index()          # moves ts_recv/ts_event from index -> column

# Save the DataFrame to a CSV file
df.to_csv('data/market_data.csv', index=False)
print("Market data pulled and saved to 'data/market_data.csv'")


# 2021-07-07 (degraded), 2021-10-26 (degraded), 2022-09-19 (degraded). See: https://databento.com/docs/api-reference-historical/metadata/metadata-get-dataset-condition
