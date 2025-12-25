# 🔌 API INTEGRATION GUIDE - AGENT X5

Complete guide for integrating Agent X5 with Zapier, Postman, JupyterLab, and other services.

---

## 📋 Table of Contents

1. [OKX API Setup](#okx-api-setup)
2. [Zapier Integration](#zapier-integration)
3. [Postman Collections](#postman-collections)
4. [JupyterLab Integration](#jupyterlab-integration)
5. [MetaTrader 5 Setup](#metatrader-5-setup)
6. [API Credentials Management](#api-credentials-management)
7. [Webhook Configuration](#webhook-configuration)
8. [Testing & Validation](#testing--validation)

---

## 🔐 OKX API Setup

### Step 1: Create OKX Account

1. Go to https://www.okx.com/
2. Sign up for account
3. Enable 2FA (required)
4. Verify identity (for higher limits)

### Step 2: Generate API Keys

**For Paper/Demo Trading:**
1. Login to OKX
2. Go to **Account** → **API** → **Create API Key**
3. Set permissions:
   - ✅ Read
   - ✅ Trade
   - ❌ Withdraw (keep disabled for safety)
4. Save: API Key, Secret, Passphrase
5. **Enable "Paper Trading" mode** in API settings

**For Sandbox Testing:**
1. Visit: https://www.okx.com/account/my-api
2. Select "Sandbox" environment
3. Create separate API keys for sandbox
4. Test with virtual funds

### Step 3: Configure in `.env`

```bash
# OKX API (Paper/Demo/Sandbox Accounts)
OKX_PAPER_API_KEY=your_paper_api_key_here
OKX_PAPER_SECRET=your_paper_secret_here
OKX_PAPER_PASSPHRASE=your_paper_passphrase_here

OKX_SANDBOX_API_KEY=your_sandbox_api_key_here
OKX_SANDBOX_SECRET=your_sandbox_secret_here
OKX_SANDBOX_PASSPHRASE=your_sandbox_passphrase_here

OKX_TESTNET=true  # Set to false for live trading
```

### Step 4: Test Connection

```bash
python3 pillar-a-trading/integrations/okx_connector.py
```

Expected output:
```
✅ Connected to OKX - PAPER
   Account Balance: $100,000.00 USDT
📈 Available markets: 500+
```

---

## ⚡ Zapier Integration

### Available Zaps

Agent X5 supports 5 main Zapier webhooks:

1. **Trade Signal Webhook** - Sends when high-confidence trade identified
2. **Market Alert Webhook** - Major market movements
3. **Daily Summary Webhook** - End-of-day performance report
4. **High Confidence Webhook** - >90% confidence trades only
5. **Error Alert Webhook** - System errors/issues

### Setup Instructions

#### 1. Create Zapier Account
- Go to https://zapier.com/
- Sign up (Free tier: 100 tasks/month)
- Or use Pro ($19.99/mo for 750 tasks/month)

#### 2. Create Webhooks

For each webhook type:

1. **In Zapier:**
   - Click "Create Zap"
   - Search for "Webhooks by Zapier"
   - Select "Catch Hook"
   - Copy the webhook URL

2. **In `.env` file:**
   ```bash
   ZAPIER_TRADE_SIGNAL_WEBHOOK=https://hooks.zapier.com/hooks/catch/12345/abcdef/
   ZAPIER_MARKET_ALERT_WEBHOOK=https://hooks.zapier.com/hooks/catch/12345/ghijkl/
   ZAPIER_DAILY_SUMMARY_WEBHOOK=https://hooks.zapier.com/hooks/catch/12345/mnopqr/
   ZAPIER_HIGH_CONFIDENCE_WEBHOOK=https://hooks.zapier.com/hooks/catch/12345/stuvwx/
   ZAPIER_ERROR_ALERT_WEBHOOK=https://hooks.zapier.com/hooks/catch/12345/yzabcd/
   ```

#### 3. Configure Zap Actions

**Example Zap #1: Trade Signal → Email**
- Trigger: Webhook received
- Action: Gmail → Send Email
- Template:
  ```
  Subject: 🎯 Trade Signal: {{symbol}} {{action}}

  Symbol: {{symbol}}
  Action: {{action}}
  Confidence: {{confidence}}%
  Entry Price: ${{price}}
  Agent: {{agent_name}}

  Quantum AI: {{quantum_enhanced}}
  ```

**Example Zap #2: Error → Slack**
- Trigger: Error webhook received
- Action: Slack → Send message
- Channel: #trading-alerts
- Template:
  ```
  ⚠️ TRADING SYSTEM ERROR

  Error: {{error_message}}
  Agent: {{agent_id}}
  Time: {{timestamp}}

  @channel please investigate
  ```

**Example Zap #3: High Confidence → Google Sheets**
- Trigger: High confidence webhook
- Action: Google Sheets → Add row
- Sheet: "High Confidence Trades"
- Columns: timestamp, symbol, action, confidence, price, agent

#### 4. Test Webhooks

```python
import requests
import os
from datetime import datetime

webhook_url = os.getenv('ZAPIER_TRADE_SIGNAL_WEBHOOK')

test_data = {
    'symbol': 'BTC/USDT',
    'action': 'BUY',
    'confidence': 0.87,
    'price': 45000,
    'agent_name': 'Crypto Trading Agent',
    'quantum_enhanced': True,
    'timestamp': datetime.now().isoformat()
}

response = requests.post(webhook_url, json=test_data)
print(f"Status: {response.status_code}")
```

### Advanced Zapier Workflows

**Multi-Step Zap: Trade Execution Flow**
1. Receive trade signal webhook
2. Log to Google Sheets
3. Send email notification
4. Post to Slack
5. Add to Trello board (for review)
6. Update Airtable database

**Filter Setup:**
- Only trigger for confidence > 80%
- Only during market hours
- Skip on weekends
- Alert only on >$1000 trades

---

## 📮 Postman Collections

### Import Agent X5 Collection

1. **Download Collection:**
   - File: `postman_collection.json` (create from template below)

2. **Import to Postman:**
   - Open Postman
   - Click "Import"
   - Select file or paste JSON
   - Collection appears in sidebar

### API Endpoints Collection

```json
{
  "info": {
    "name": "Agent X5 Trading API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "System Status",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "http://localhost:8000/api/v1/status",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["api", "v1", "status"]
        }
      }
    },
    {
      "name": "Get All Agents",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "http://localhost:8000/api/v1/agents",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["api", "v1", "agents"]
        }
      }
    },
    {
      "name": "Get Agent Performance",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "http://localhost:8000/api/v1/agents/1/performance?period=7d",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["api", "v1", "agents", "1", "performance"],
          "query": [
            {"key": "period", "value": "7d"}
          ]
        }
      }
    },
    {
      "name": "Place Trade",
      "request": {
        "method": "POST",
        "header": [
          {"key": "Content-Type", "value": "application/json"}
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"symbol\": \"BTC/USDT\",\n  \"side\": \"buy\",\n  \"amount\": 0.001,\n  \"agent_id\": 1,\n  \"environment\": \"paper\"\n}"
        },
        "url": {
          "raw": "http://localhost:8000/api/v1/trade",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["api", "v1", "trade"]
        }
      }
    },
    {
      "name": "Get Open Positions",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "http://localhost:8000/api/v1/positions?environment=paper",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["api", "v1", "positions"],
          "query": [
            {"key": "environment", "value": "paper"}
          ]
        }
      }
    }
  ]
}
```

### Environment Variables in Postman

Create environment "Agent X5 - Local":
```json
{
  "name": "Agent X5 - Local",
  "values": [
    {"key": "base_url", "value": "http://localhost:8000", "enabled": true},
    {"key": "api_version", "value": "v1", "enabled": true},
    {"key": "environment", "value": "paper", "enabled": true}
  ]
}
```

Then use: `{{base_url}}/api/{{api_version}}/status`

---

## 📊 JupyterLab Integration

### Setup JupyterLab

```bash
# Install JupyterLab
pip install jupyterlab numpy pandas matplotlib

# Start JupyterLab
jupyter lab --port=8888
```

### Create Trading Analysis Notebook

```python
# Cell 1: Import Agent X5
import sys
sys.path.append('/home/user/Private-Claude')

from pillar_a_trading.integrations.okx_connector import OKXConnector
from pillar_a_trading.ai_models.quantum_ai_system import QuantumAISystem, QuantumVersion
from pillar_a_trading.bots.multi_asset_trading_system import MultiAssetOrchestrator

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Cell 2: Connect to OKX
okx = OKXConnector(environment='paper')
okx.connect()

# Cell 3: Get market data
btc_data = okx.get_ohlcv('BTC/USDT', '1h', 168)  # 7 days
df = pd.DataFrame(btc_data)
df['timestamp'] = pd.to_datetime(df['timestamp'])
df.set_index('timestamp', inplace=True)

# Cell 4: Plot price
plt.figure(figsize=(14, 7))
plt.plot(df.index, df['close'], label='BTC/USDT')
plt.title('Bitcoin Price - Last 7 Days')
plt.xlabel('Date')
plt.ylabel('Price (USDT)')
plt.legend()
plt.grid(True)
plt.show()

# Cell 5: Quantum AI analysis
quantum_ai = QuantumAISystem(version=QuantumVersion.V4_0)

market_data = {
    'volatility': df['close'].pct_change().std(),
    'momentum': (df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0],
    'volume_ratio': df['volume'].iloc[-24:].mean() / df['volume'].mean(),
    'price_data': df['close'].values,
    'streams': []
}

result = quantum_ai.analyze_market(market_data)

print(f"🔬 Quantum AI Recommendation: {result['recommendation']}")
print(f"   Confidence: {result['confidence_level']:.2%}")
print(f"   Coherence: {result['coherence']:.2%}")

# Cell 6: Backtest performance
def simple_backtest(df, signals):
    """Simple backtest"""
    positions = []
    pnl = 0

    for i, signal in enumerate(signals):
        if signal == 'BUY':
            positions.append(df['close'].iloc[i])
        elif signal == 'SELL' and positions:
            entry = positions.pop(0)
            pnl += (df['close'].iloc[i] - entry) / entry

    return pnl * 100

# Generate sample signals
signals = ['BUY' if r > 0.6 else 'SELL' if r < 0.4 else 'HOLD' for r in np.random.random(len(df))]
backtest_result = simple_backtest(df, signals)

print(f"📈 Backtest Result: {backtest_result:.2f}% return")
```

### Share Notebooks with Team

```bash
# Export notebook
jupyter nbconvert --to html analysis.ipynb

# Or export to PDF
jupyter nbconvert --to pdf analysis.ipynb
```

---

## 🖥️ MetaTrader 5 Setup

### Download & Install MT5

1. **Download MT5:**
   - Windows: https://www.metatrader5.com/en/download
   - Mac: Use Wine or virtual machine
   - Linux: Use Wine

2. **Open Demo Account:**
   - Launch MT5
   - File → Open Account
   - Select broker (or MetaQuotes-Demo)
   - Fill in details
   - Save account number and password

3. **Configure in `.env`:**
   ```bash
   MT5_LOGIN=your_demo_account_number
   MT5_PASSWORD=your_demo_password
   MT5_SERVER=MetaQuotes-Demo
   ```

### Test MT5 Connection

```python
from pillar_a_trading.integrations.mt5_connector import MT5TradingBot

bot = MT5TradingBot(account_type='demo')
if bot.start():
    print("✅ MT5 connected!")
    bot.show_account_status()
```

---

## 🔑 API Credentials Management

### Secure Credentials Checklist

- [ ] All credentials in `.env` file
- [ ] `.env` added to `.gitignore`
- [ ] Never commit `.env` to Git
- [ ] Use separate keys for paper/sandbox/live
- [ ] Rotate keys every 90 days
- [ ] Limit API permissions (no withdrawals)
- [ ] Enable IP whitelist if available
- [ ] Use 2FA on all accounts

### Environment Variables Required

```bash
# Copy from template
cp config/.env.template config/.env

# Edit with your credentials
nano config/.env
```

### Credentials by Service

| Service | Keys Needed | Where to Get |
|---------|-------------|--------------|
| OKX | API Key, Secret, Passphrase | https://www.okx.com/account/my-api |
| Zapier | Bearer Token | https://zapier.com/app/settings/integrations |
| Alpha Vantage | API Key | https://www.alphavantage.co/support/#api-key |
| Finnhub | API Key | https://finnhub.io/dashboard |
| MT5 | Login, Password, Server | MetaTrader 5 Terminal |
| Gmail | OAuth Credentials | https://console.cloud.google.com/ |

---

## 🪝 Webhook Configuration

### Webhook Payload Formats

**Trade Signal:**
```json
{
  "webhook_type": "trade_signal",
  "timestamp": "2024-12-25T10:30:00Z",
  "agent_id": 1,
  "agent_name": "Crypto Trading Agent",
  "symbol": "BTC/USDT",
  "action": "BUY",
  "confidence": 0.87,
  "price": 45000,
  "amount": 0.001,
  "quantum_enhanced": true,
  "environment": "paper"
}
```

**Market Alert:**
```json
{
  "webhook_type": "market_alert",
  "timestamp": "2024-12-25T10:30:00Z",
  "alert_type": "volatility_spike",
  "symbol": "BTC/USDT",
  "current_price": 45000,
  "volatility": 0.35,
  "message": "Volatility spike detected - 35% above average"
}
```

**Daily Summary:**
```json
{
  "webhook_type": "daily_summary",
  "date": "2024-12-25",
  "total_trades": 45,
  "winning_trades": 31,
  "win_rate": 0.689,
  "total_pnl": 1250.50,
  "pnl_percentage": 1.25,
  "best_trade": {"symbol": "BTC/USDT", "pnl": 250},
  "worst_trade": {"symbol": "ETH/USDT", "pnl": -50}
}
```

### Test All Webhooks

```bash
# Run webhook test script
python3 scripts/test_webhooks.py
```

Expected output:
```
Testing webhooks...
✅ Trade Signal webhook: 200 OK
✅ Market Alert webhook: 200 OK
✅ Daily Summary webhook: 200 OK
✅ High Confidence webhook: 200 OK
✅ Error Alert webhook: 200 OK
```

---

## ✅ Testing & Validation

### API Connection Tests

```bash
# Test all integrations
python3 tests/test_api_integrations.py

# Test specific service
python3 tests/test_okx.py
python3 tests/test_mt5.py
python3 tests/test_zapier.py
```

### Validation Checklist

#### OKX
- [ ] Connection successful
- [ ] Can fetch ticker data
- [ ] Can fetch OHLCV data
- [ ] Can get account balance
- [ ] Can place paper trade
- [ ] Can cancel order

#### Zapier
- [ ] All 5 webhooks configured
- [ ] Test payload sent successfully
- [ ] Zap triggered correctly
- [ ] Action executed (email/Slack/etc.)

#### MT5
- [ ] MT5 terminal running
- [ ] Demo account connected
- [ ] Can fetch market data
- [ ] Can get account info
- [ ] Can place demo trade

#### JupyterLab
- [ ] Can import Agent X5 modules
- [ ] Can connect to exchanges
- [ ] Can run Quantum AI
- [ ] Can generate charts
- [ ] Can export notebooks

---

## 🚨 Troubleshooting

### Common Issues

**Issue: "OKX connection error"**
```
Solution:
1. Check API keys in .env
2. Verify API is enabled on OKX
3. Check IP whitelist (if enabled)
4. Confirm sandbox mode setting
```

**Issue: "Zapier webhook not triggering"**
```
Solution:
1. Verify webhook URL is correct
2. Check Zapier task history
3. Ensure Zap is turned ON
4. Test with Postman first
```

**Issue: "MT5 initialization failed"**
```
Solution:
1. Ensure MT5 terminal is running
2. Check login credentials
3. Verify server name is correct
4. Try restarting MT5 terminal
```

---

## 📞 Support & Resources

- **OKX API Docs**: https://www.okx.com/docs-v5/
- **Zapier Help**: https://help.zapier.com/
- **MT5 Forum**: https://www.mql5.com/en/forum
- **CCXT GitHub**: https://github.com/ccxt/ccxt
- **Agent X5 Issues**: [Create issue in repo]

---

*Keep this guide updated as new integrations are added!*
