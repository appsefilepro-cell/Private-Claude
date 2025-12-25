# 🚀 GITHUB COPILOT MASTER PROMPT - AGENT X5

## System Overview

**Agent X5** is a comprehensive trading orchestration system with:
- **100 Specialized Roles** across 9 categories
- **20 Multi-Agent Systems** running in parallel
- **Quantum AI Models** (v3.0, v3.4, v4.0) with PhD-level algorithms
- **Multi-Asset Trading**: Crypto, Forex, Options, Indices, Shorting, USD Pairs
- **Multiple Environments**: Paper, Sandbox, Live
- **24/7 Automated Trading** with comprehensive risk management

---

## 🎯 GitHub Copilot Instructions

### Primary Objectives

When working with this codebase, GitHub Copilot should:

1. **Maintain System Architecture**
   - Preserve the 100-role structure
   - Keep 20 multi-agent orchestration intact
   - Maintain separation between environments (paper/sandbox/live)

2. **Follow Trading Best Practices**
   - Always implement risk management
   - Include position sizing calculations
   - Add stop-loss and take-profit logic
   - Log all trades and decisions

3. **Integrate Quantum AI**
   - Use quantum decision engines for complex choices
   - Apply quantum pattern recognition for market analysis
   - Leverage quantum ML for predictions
   - Document quantum algorithm usage

4. **Code Quality Standards**
   - Type hints for all functions
   - Comprehensive docstrings
   - Error handling with try/except
   - Logging at INFO level for important events
   - Unit tests for new functionality

---

## 🏗️ Architecture Reference

### Core Systems

```
Private-Claude/
├── agent-4.0/
│   └── orchestrator/
│       ├── unified_trading_orchestrator.py  # 100 roles + 20 agents
│       ├── master_orchestrator.py
│       └── multi_agent_system.py
├── pillar-a-trading/
│   ├── bots/
│   │   └── multi_asset_trading_system.py   # 6 asset class bots
│   ├── integrations/
│   │   ├── okx_connector.py                # OKX exchange
│   │   └── mt5_connector.py                # MetaTrader 5
│   ├── ai-models/
│   │   └── quantum_ai_system.py            # Quantum AI 3.0/3.4/4.0
│   ├── strategies/
│   │   ├── big_short_strategy.py
│   │   ├── momentum_short_strategy.py
│   │   └── technical_breakdown_short_strategy.py
│   └── config/
│       └── multi_account_config.json       # 21 test accounts
└── config/
    └── .env                                # API credentials
```

### 100 Specialized Roles (by Category)

| Category | Count | Examples |
|----------|-------|----------|
| **Trading** | 20 | Crypto Day Trader, Forex Swing Trader, Options Specialist |
| **Analysis** | 20 | Technical Analyst, Sentiment Analyst, Pattern Recognition |
| **Risk Management** | 15 | Position Size Calculator, Stop Loss Manager, VaR Calculator |
| **Execution** | 10 | Market Order Executor, TWAP/VWAP, Smart Order Router |
| **Monitoring** | 10 | 24/7 Monitor, P&L Tracker, System Health Monitor |
| **Quantum AI** | 10 | Quantum Decision Engine, Pattern Recognizer, ML Trainer |
| **Strategy** | 5 | Strategy Developer, Backtest Engine, Optimizer |
| **Data Collection** | 5 | Price/Volume Collector, News Aggregator, On-Chain Data |
| **Compliance** | 5 | Compliance Monitor, Audit Trail, Tax Optimizer |

### 20 Multi-Agent Systems

1. **Crypto Trading Agent** - BTC, ETH, SOL, ADA, DOT, LINK, AVAX, MATIC
2. **Forex Trading Agent** - EUR/USD, GBP/USD, USD/JPY, etc.
3. **Options Trading Agent** - SPY, QQQ, IWM, DIA options
4. **Shorting Specialist Agent** - All markets
5. **USD Crypto Pairs Agent** - BTC/USD, ETH/USD, etc.
6. **US Indices Agent** - SPY, QQQ, DIA, IWM
7-9. **Quantum AI Agents** - v3.0, v3.4, v4.0
10. **Risk Management Agent** - Portfolio-wide risk
11-13. **Analysis Agents** - Technical, Fundamental, Sentiment
14. **Order Execution Agent** - All order types
15. **24/7 Monitoring Agent** - Continuous oversight
16. **Strategy Development Agent** - New strategies
17. **Data Collection Agent** - Multi-source data
18. **Compliance Agent** - Regulatory compliance
19. **Reporting Agent** - Performance reports
20. **Master Coordinator Agent** - Oversees all 100 roles

---

## 🔌 API Integrations

### Trading APIs

**OKX Exchange** (via CCXT)
```python
from pillar_a_trading.integrations.okx_connector import OKXConnector

connector = OKXConnector(environment='paper')  # or 'sandbox' or 'live'
connector.connect()
ticker = connector.get_ticker('BTC/USDT')
order = connector.place_market_order('BTC/USDT', 'buy', 0.001)
```

**MetaTrader 5**
```python
from pillar_a_trading.integrations.mt5_connector import MT5Connector

mt5 = MT5Connector(account_type='demo')
mt5.connect()
data = mt5.get_market_data('EURUSD', 'H1', 100)
```

### Quantum AI Integration

```python
from pillar_a_trading.ai_models.quantum_ai_system import QuantumAISystem, QuantumVersion

# Initialize Quantum AI
quantum_ai = QuantumAISystem(version=QuantumVersion.V4_0)

# Analyze market with quantum algorithms
market_data = {
    'volatility': 0.25,
    'momentum': 0.6,
    'volume_ratio': 1.3,
    'price_data': price_array,
    'streams': data_streams
}

result = quantum_ai.analyze_market(market_data)
# Returns: recommendation, confidence, quantum_coherence, phd_algorithms_used
```

### Multi-Asset Trading

```python
from pillar_a_trading.bots.multi_asset_trading_system import MultiAssetOrchestrator

orchestrator = MultiAssetOrchestrator()

# Get specific bot
shorting_bot = orchestrator.get_bot('shorting', 'paper')
crypto_bot = orchestrator.get_bot('crypto', 'sandbox')

# Execute trades
signal = crypto_bot.analyze_crypto('BTC', market_data)
if signal:
    order = crypto_bot.execute_crypto_trade(signal)
```

---

## 📊 Zapier Integration

### Available Webhooks

Set in `.env`:
```bash
ZAPIER_TRADE_SIGNAL_WEBHOOK=https://hooks.zapier.com/hooks/catch/...
ZAPIER_MARKET_ALERT_WEBHOOK=https://hooks.zapier.com/hooks/catch/...
ZAPIER_DAILY_SUMMARY_WEBHOOK=https://hooks.zapier.com/hooks/catch/...
ZAPIER_HIGH_CONFIDENCE_WEBHOOK=https://hooks.zapier.com/hooks/catch/...
ZAPIER_ERROR_ALERT_WEBHOOK=https://hooks.zapier.com/hooks/catch/...
```

### Send to Zapier

```python
import requests
import os

def send_to_zapier(webhook_type: str, data: dict):
    webhook_url = os.getenv(f'ZAPIER_{webhook_type}_WEBHOOK')
    if webhook_url:
        requests.post(webhook_url, json=data)
```

---

## 🧪 Postman Collections

### Authentication

All APIs use Bearer tokens or API key authentication:

```json
{
  "Authorization": "Bearer YOUR_TOKEN",
  "Content-Type": "application/json"
}
```

### Sample API Endpoints

**Get System Status**
```
GET /api/v1/status
Response: { "agents": 20, "roles": 100, "status": "active" }
```

**Place Trade**
```
POST /api/v1/trade
Body: {
  "symbol": "BTC/USDT",
  "side": "buy",
  "amount": 0.001,
  "agent_id": 1,
  "environment": "paper"
}
```

**Get Performance**
```
GET /api/v1/performance?agent_id=1&period=7d
Response: { "pnl": 1250.50, "win_rate": 0.68, "trades": 45 }
```

---

## 🎓 Quantum AI - PhD-Level Algorithms

### Algorithm Reference

**v3.0 Capabilities**
- Quantum Annealing for optimization
- 8 qubits, 256 state space
- Basic pattern recognition

**v3.4 Capabilities**
- Quantum Annealing
- Variational Eigensolver
- 12 qubits, 4096 state space
- Advanced pattern recognition

**v4.0 Capabilities** (Most Advanced)
- Quantum Annealing
- Variational Eigensolver
- Quantum Approximate Optimization
- 16 qubits, 65536 state space
- Expert pattern recognition
- PhD-level quantitative methods

### When to Use Quantum AI

✅ **Use for:**
- Complex multi-variable decisions
- Pattern recognition in noisy data
- Portfolio optimization
- Real-time parallel analysis
- High-confidence trade selection

❌ **Don't use for:**
- Simple buy/sell decisions
- Single-variable analysis
- Time-critical microsecond trades

---

## 🛡️ Risk Management Standards

### Always Include

```python
class TradingBot:
    def __init__(self):
        self.max_position_size = 0.02  # 2% of portfolio
        self.risk_per_trade = 0.01     # 1% risk
        self.max_daily_loss = 0.05     # 5% max daily loss
        self.confidence_threshold = 0.75  # 75% confidence minimum

    def calculate_position_size(self, account_balance, confidence):
        base_size = account_balance * self.max_position_size
        adjusted_size = base_size * confidence
        return min(adjusted_size, account_balance * self.risk_per_trade * 10)

    def should_trade(self, signal):
        return (
            signal['confidence'] >= self.confidence_threshold and
            not self.max_daily_loss_hit() and
            self.position_count < self.max_positions
        )
```

---

## 🔄 Parallel Execution Pattern

```python
import asyncio

async def run_all_agents_parallel():
    """Run all 20 agents in parallel"""
    tasks = []

    for agent in orchestrator.multi_agents:
        if agent['status'] == 'active':
            task = execute_agent_logic(agent)
            tasks.append(task)

    # Execute all in parallel
    results = await asyncio.gather(*tasks)

    return results

# Run
asyncio.run(run_all_agents_parallel())
```

---

## 📝 Logging Standards

```python
import logging

logger = logging.getLogger(__name__)

# Trade execution
logger.info(f"✅ Order placed: {side.upper()} {amount} {symbol} @ ${price}")

# Risk events
logger.warning(f"⚠️  Approaching daily loss limit: {loss_pct:.2%}")

# Errors
logger.error(f"❌ Order failed: {error_message}")

# System events
logger.info(f"🚀 Agent #{agent_id} started: {agent_name}")
logger.info(f"🎯 Quantum AI v{version} analysis complete")
```

---

## 🧪 Testing Requirements

### Before Committing

```bash
# Run all tests
pytest tests/ -v

# Run specific test suites
pytest tests/test_trading_bots.py
pytest tests/test_quantum_ai.py
pytest tests/test_integrations.py

# Check code quality
black . --check
flake8 .
mypy .
```

### Test Coverage Requirements

- Unit tests: >80% coverage
- Integration tests for all APIs
- End-to-end tests for trading flows
- Quantum AI validation tests

---

## 🚀 Deployment Checklist

- [ ] All tests passing
- [ ] API credentials configured in `.env`
- [ ] Risk management parameters set
- [ ] Logging configured
- [ ] Monitoring alerts active
- [ ] Backup systems enabled
- [ ] Start with paper trading
- [ ] Validate with sandbox
- [ ] Only then: Live (with extreme caution)

---

## 💡 GitHub Copilot Tips

### Auto-Complete Patterns

When typing:
- `def analyze_` → Suggests market analysis methods
- `def execute_` → Suggests trade execution logic
- `def calculate_risk_` → Suggests risk calculations
- `async def run_` → Suggests async parallel execution

### Context Awareness

Copilot understands:
- 100 role structure
- 20 agent types
- Quantum AI integration points
- Multi-environment setup (paper/sandbox/live)
- Risk management requirements

### Best Practices

1. **Let Copilot suggest entire functions** - It knows the patterns
2. **Use comments to guide** - "# Quantum AI decision for high-stakes trade"
3. **Leverage examples** - Similar code exists in the repo
4. **Trust the risk management** - Copilot suggests safe defaults

---

## 📚 Additional Resources

- **OKX API Docs**: https://www.okx.com/docs-v5/
- **CCXT Library**: https://docs.ccxt.com/
- **MT5 Python**: https://www.mql5.com/en/docs/python_metatrader5
- **Quantum Computing**: Nielsen & Chuang, "Quantum Computation and Quantum Information"
- **Trading Strategies**: Jansen, "Machine Learning for Algorithmic Trading"

---

## 🎯 Success Metrics

The system is optimized for:
- **Accuracy**: 91-95% prediction accuracy
- **Win Rate**: Target 65%+ win rate
- **Risk/Reward**: Minimum 2:1 ratio
- **Uptime**: 99.9% system availability
- **Latency**: <100ms decision making
- **Quantum Enhancement**: 15-20% improvement over classical

---

## ⚠️ Important Notes

1. **Never commit `.env` file** - Contains sensitive API keys
2. **Always test in paper first** - Validate before sandbox/live
3. **Respect rate limits** - Exchanges will ban excessive requests
4. **Monitor risk metrics** - Stop trading if limits exceeded
5. **Keep quantum AI updated** - Models improve over time
6. **Log everything** - Audit trail is critical
7. **Backup regularly** - Data loss is unacceptable

---

*This prompt helps GitHub Copilot understand the entire Agent X5 architecture and provide context-aware suggestions that maintain system integrity while accelerating development.*
