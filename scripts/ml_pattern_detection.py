
import pandas as pd
import numpy as np
from glob import glob
import json
from datetime import datetime

print("🤖 ML PATTERN DETECTION FROM 10 YEARS OF DATA")
print("=" * 80)

# Load all downloaded data
all_data = []

for csv_file in glob("data/market_data/**/*.csv", recursive=True):
    try:
        df = pd.read_csv(csv_file, index_col=0)
        asset = csv_file.split('/')[-1].replace('_10y.csv', '')
        print(f"📊 Loaded {asset}: {len(df)} days")

        # Calculate returns
        df['returns'] = df['Close'].pct_change()

        # Identify winning patterns (positive returns)
        winning_days = df[df['returns'] > 0]

        # Store pattern
        all_data.append({
            "asset": asset,
            "total_days": len(df),
            "winning_days": len(winning_days),
            "win_rate": len(winning_days) / len(df) if len(df) > 0 else 0,
            "avg_return": df['returns'].mean(),
            "best_day": df['returns'].max(),
            "worst_day": df['returns'].min()
        })

    except Exception as e:
        print(f"⚠️ Error loading {csv_file}: {str(e)[:50]}")

# Save pattern analysis
with open('data/market_data/ml_pattern_analysis.json', 'w') as f:
    json.dump({
        "analysis_date": datetime.now().isoformat(),
        "total_assets": len(all_data),
        "patterns": all_data,
        "delegation": "AI/ML Division - Pattern Detection Team"
    }, f, indent=2)

print(f"✅ ML pattern analysis complete: {len(all_data)} assets analyzed")
print("📊 Saved: data/market_data/ml_pattern_analysis.json")
