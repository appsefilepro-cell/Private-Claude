
import yfinance as yf
from datetime import datetime, timedelta
import json

print("📥 Downloading Forex data via Yahoo Finance (FREE)...")

forex_pairs = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCHF=X", "AUDUSD=X", "USDCAD=X", "NZDUSD=X", "EURJPY=X", "GBPJPY=X", "EURGBP=X", "AUDCAD=X", "EURAUD=X"]

for pair in forex_pairs:
    try:
        print(f"   Downloading {pair}...")
        ticker = yf.Ticker(pair)

        # Download 10 years of daily data
        data = ticker.history(period="10y", interval="1d")

        if not data.empty:
            # Save to CSV
            filename = f"data/market_data/forex/{pair.replace('=X', '')}_10y.csv"
            data.to_csv(filename)
            print(f"   ✅ {pair}: {len(data)} days downloaded")
        else:
            print(f"   ⚠️ {pair}: No data available")

    except Exception as e:
        print(f"   ⚠️ {pair}: {str(e)[:50]}")

print("✅ Forex data download complete")
