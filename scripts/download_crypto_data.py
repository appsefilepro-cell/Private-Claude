
import yfinance as yf
import json

print("📥 Downloading Crypto data via Yahoo Finance (FREE)...")

crypto_pairs = ["BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "ADA-USD", "SOL-USD", "DOT-USD", "DOGE-USD", "AVAX-USD", "MATIC-USD"]

for pair in crypto_pairs:
    try:
        print(f"   Downloading {pair}...")
        ticker = yf.Ticker(pair)

        # Download 10 years of daily data (or max available for newer coins)
        data = ticker.history(period="max", interval="1d")

        if not data.empty:
            # Save to CSV
            filename = f"data/market_data/crypto/{pair.replace('-USD', '')}_10y.csv"
            data.to_csv(filename)
            print(f"   ✅ {pair}: {len(data)} days downloaded")
        else:
            print(f"   ⚠️ {pair}: No data available")

    except Exception as e:
        print(f"   ⚠️ {pair}: {str(e)[:50]}")

print("✅ Crypto data download complete")
