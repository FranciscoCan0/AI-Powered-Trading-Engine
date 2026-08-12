import yfinance as yf
import pandas as pd
from pathlib import Path
from datetime import date, datetime, timedelta
import os
import subprocess


lookback_window_days = 7  # max 1m interval range yfinance/Yahoo supports per call (allows backfills)
csv_path = Path("/Users/lil_lawnmower/Documents/Code/Model Projects/AI_Powered_Trading_Engine/data/yfinance/1m_interval_trading_data.csv")
datetime_col = "Datetime" 

max_size_bytes = 1000 * 1024 * 1024  # 1 GB

max_span = timedelta(days=365 * 2)  # 2 years

SCRIPT_PATH = str(Path(__file__).resolve())  # absolute path to THIS script


stock_tickers = ["AAPL", "NVDA", "AMZN",           # TECH
                "AXP", "BRK-B", "JPM",           # BANKING
                "JNJ", "PFE", "UNH",             # HEALTHCARE
                "PG", "WMT", "KO",                # RETAIL
                "GE", "CAT", "LMT",               # INDUSTRIAL/AEROSPACE
                "XOM", "CVX", "SHEL",              # ENERGY
                "SONY", "BABA", "NVO",           # INTERNATIONAL
                "SPY", "VOO", "IVV", "QQQ"]       # ETFs

LAUNCHD_LABEL = "com.lil_lawnmower.aitradingengine"
PLIST_PATH = Path.home() / "Library" / "LaunchAgents" / f"{LAUNCHD_LABEL}.plist"

def remove_launchd_job():
    """Unload and delete the launchd job that runs this script."""
    result = subprocess.run(
        ["launchctl", "bootout", f"gui/{os.getuid()}/{LAUNCHD_LABEL}"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"[INFO] Unloaded launchd job {LAUNCHD_LABEL}")
    else:
        print(f"[WARN] launchctl bootout failed (may already be unloaded): {result.stderr.strip()}")

    if PLIST_PATH.exists():
        PLIST_PATH.unlink()
        print(f"[INFO] Deleted plist {PLIST_PATH}")
    else:
        print(f"[WARN] Plist not found at {PLIST_PATH}")

def obtain_1_min_data():
    new_data = []
    today = date.today()

    #Tells Schedueler to cancel this job if file size too large or we have 2 years of data 
    if csv_path.exists():
        size = csv_path.stat().st_size
        if size >= max_size_bytes:
            print(f"[STOP] {csv_path} reached {size / (1024*1024):.1f} MB — cancelling launchd job.")
            remove_launchd_job()
            return

        existing = pd.read_csv(csv_path, parse_dates=["Datetime"])
        if not existing.empty:
            span = existing["Datetime"].max() - existing["Datetime"].min()
            if span >= max_span:
                print(f"[STOP] Data spans {span.days} days (>= {max_span.days}) — cancelling launchd job.")
                remove_launchd_job()
                return
    else: 
        existing = pd.DataFrame()

    for ticker in stock_tickers:
        ticker_object = yf.Ticker(ticker)
        temp = ticker_object.history(period=f"{lookback_window_days}d", interval="1m")

        if temp.empty:
            print(f"[WARN] No 1m data returned for {ticker} in last {lookback_window_days}d from {today}")
            continue

        temp["Ticker"] = ticker
        temp = temp.reset_index()  # pulls the datetime index into a column
        new_data.append(temp)

    #Check if no ticker returned any data 
    if not new_data:
        print("[WARN] No data returned for any ticker this run — skipping save.")
        return
    
    new_data = pd.concat(new_data, ignore_index=True)

    combined = pd.concat([existing, new_data], ignore_index=True)

    combined = combined.drop_duplicates(subset=[datetime_col, "Ticker"], keep="last")
    combined = combined.sort_values(["Ticker", datetime_col])

    combined.to_csv(csv_path, index=False)

    print(f"Saved {len(combined)} total rows to {csv_path}")
    print(f"[DATE: {today}]This run added {len(new_data)} rows, deduped down to {len(combined) - len(existing)} new unique rows")


if __name__ == "__main__":
    obtain_1_min_data()


