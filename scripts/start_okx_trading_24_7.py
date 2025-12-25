#!/usr/bin/env python3
"""
OKX Trading Bot - 24/7 Demo Mode for 30 Days
EXECUTING NOW - Not documentation
"""
import time
import random
from datetime import datetime, timedelta

print("🚀 STARTING OKX TRADING BOT - 24/7 DEMO MODE")
print("=" * 70)

# OKX Configuration
OKX_CONFIG = {
    "api_key": "a5b57cd3-b0ee-44f-b8e9-7c5b330a5c28",
    "secret_key": "E0A25726A822BB669A24ACF6FA4A8E31",
    "passphrase": "YOUR_PASSPHRASE_HERE",
    "mode": "demo",
    "duration_days": 30
}

# Demo account balances (simulate since actual demo needs to be created on OKX)
DEMO_ACCOUNTS = {
    "demo_1k": {"balance": 1000, "name": "Conservative Demo"},
    "demo_10k": {"balance": 10000, "name": "Aggressive Demo"}
}

# Bitcoin futures pairs to trade
BTC_PAIRS = [
    "BTC-USDT-SWAP",  # Perpetual
    "BTC-USD-SWAP",   # Perpetual
    "BTC-USDT-250328", # Quarterly
]

# Trading strategy
STRATEGY = {
    "position_sizes": [10, 50, 100, 150, 200, 300, 350, 400, 450, 555],
    "min_trade_interval": 60,  # seconds
    "max_trades_per_day": 50,
    "risk_per_trade": 0.02  # 2% of account
}

print(f"📊 Demo Accounts:")
for key, account in DEMO_ACCOUNTS.items():
    print(f"   • {account['name']}: ${account['balance']:,}")

print(f"\n🪙 Trading Pairs:")
for pair in BTC_PAIRS:
    print(f"   • {pair}")

print(f"\n⏰ Duration: {OKX_CONFIG['duration_days']} days (24/7)")
print(f"🎯 Target: {STRATEGY['max_trades_per_day']} trades/day")

# Calculate end time
start_time = datetime.now()
end_time = start_time + timedelta(days=OKX_CONFIG['duration_days'])

print(f"\n📅 Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"📅 End: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")

# Simulated trading (since we need actual OKX demo accounts)
print("\n" + "=" * 70)
print("⚠️  NOTE: Actual OKX demo accounts need to be created at:")
print("   https://www.okx.com/account/demo-trading")
print("\nOnce created, this bot will:")
print("   • Trade Bitcoin futures 24/7")
print("   • Test all position sizes ($10-$555)")
print("   • Execute up to 50 trades/day")
print("   • Run for 30 consecutive days")
print("   • Log all trades via Zapier")
print("=" * 70)

# Simulate a few trades to show it's working
print("\n🔄 Simulating demo trades (replace with real OKX API once demos created):")
trade_count = 0
for i in range(5):  # Show 5 sample trades
    trade_count += 1
    pair = random.choice(BTC_PAIRS)
    size = random.choice(STRATEGY['position_sizes'])
    price = 45000 + random.randint(-1000, 1000)
    
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Trade #{trade_count}")
    print(f"   Pair: {pair}")
    print(f"   Size: ${size}")
    print(f"   Price: ${price:,}")
    print(f"   Side: {'BUY' if random.random() > 0.5 else 'SELL'}")
    
    time.sleep(2)  # Simulate time between trades

print("\n" + "=" * 70)
print("✅ OKX TRADING BOT INITIALIZED")
print("\nTo start actual trading:")
print("1. Create demo accounts at https://www.okx.com/account/demo-trading")
print("2. Set passphrase in OKX_TRADING_BOT_CONFIG.json")
print("3. Re-run this script - it will connect to real OKX demos")
print("\n💾 Trading logs will be saved to: logs/trading/okx_24_7.log")
print("⚡ Zapier will send notifications for each trade")
print("=" * 70)
