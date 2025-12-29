# Agent X5.0 Installation Guide

## Quick Start (5 Minutes)

### 1. Clone Repository
```bash
git clone https://github.com/appsefilepro-cell/Private-Claude.git
cd Private-Claude
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
nano .env  # Edit with your API keys
```

### 5. Run Agent X5
```bash
# Paper trading mode (safe)
python scripts/agent_x5_master_orchestrator.py

# Or use activation script
chmod +x ACTIVATE_EVERYTHING.sh
./ACTIVATE_EVERYTHING.sh
```

---

## Detailed Setup

### API Keys Required

| Service | Get Key From | Required |
|---------|--------------|----------|
| Anthropic | https://console.anthropic.com | Yes |
| OpenAI | https://platform.openai.com | Optional |
| Gemini | https://makersuite.google.com | Optional |
| OKX | https://www.okx.com/account/my-api | For trading |
| E2B | https://e2b.dev | For sandbox |

### Minimum Configuration

For basic operation, you only need:
```env
ANTHROPIC_API_KEY=your-key
TRADING_MODE=PAPER
LOG_LEVEL=INFO
```

### Trading Configuration

**PAPER MODE (Default - Safe)**
```env
TRADING_MODE=PAPER
LIVE_TRADING=false
```

**LIVE MODE (Real Money - Dangerous)**
```env
TRADING_MODE=LIVE
LIVE_TRADING=true
# Requires typing "I UNDERSTAND THE RISKS" when starting
```

---

## Docker Setup

### Build and Run
```bash
docker-compose up -d
```

### View Logs
```bash
docker-compose logs -f agent-x5
```

### Stop All Services
```bash
docker-compose down
```

---

## Verification

### Test Installation
```bash
python -c "import anthropic; print('Anthropic OK')"
python -c "import openai; print('OpenAI OK')"
python -c "import ccxt; print('CCXT OK')"
```

### Run Tests
```bash
pytest tests/ -v
```

### Check Agent Status
```bash
cat AGENT_X5_STATUS_REPORT.json
```

---

## Troubleshooting

### "Module not found" Error
```bash
pip install -r requirements.txt --upgrade
```

### API Key Invalid
1. Check .env file exists
2. Verify key format (no quotes needed)
3. Check key hasn't expired

### Trading Not Working
1. Verify TRADING_MODE is set
2. Check OKX API keys if using OKX
3. Review logs in /logs directory

---

## Support

- Issues: https://github.com/appsefilepro-cell/Private-Claude/issues
- Documentation: See /docs folder
