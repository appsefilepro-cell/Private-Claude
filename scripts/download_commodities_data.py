
import yfinance as yf

print("📥 Downloading Commodities data via Yahoo Finance (FREE)...")

commodities = ["GC=F", "SI=F", "CL=F"]

for commodity in commodities:
    try:
        print(f"   Downloading {commodity}...")
        ticker = yf.Ticker(commodity)
        data = ticker.history(period="10y", interval="1d")

        if not data.empty:
            filename = f"data/market_data/commodities/{commodity.replace('=F', '')}_10y.csv"
            data.to_csv(filename)
            print(f"   ✅ {commodity}: {len(data)} days downloaded")
    except Exception as e:
        print(f"   ⚠️ {commodity}: {str(e)[:50]}")

print("✅ Commodities data download complete")
