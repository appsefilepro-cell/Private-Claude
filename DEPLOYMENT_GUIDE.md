# Agent X5.0 - Complete Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Docker Deployment](#docker-deployment)
4. [Manual Deployment](#manual-deployment)
5. [Environment Setup](#environment-setup)
6. [Testing](#testing)
7. [Monitoring](#monitoring)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+), macOS, or Windows with WSL2
- **Python**: 3.9 or higher
- **Docker**: 20.10+ (for containerized deployment)
- **Docker Compose**: 1.29+ (for orchestration)
- **Memory**: Minimum 4GB RAM, 8GB recommended
- **Storage**: 10GB free space

### Required Accounts
- Anthropic API (Claude) - for AI operations
- E2B API - for sandbox execution (optional)
- Gemini API - for additional AI analysis (optional)
- Trading Exchange accounts - for live trading (Kraken, Binance, etc.)

---

## Quick Start

### Option 1: One-Command Activation (Recommended)
```bash
# Clone the repository
git clone https://github.com/appsefilepro-cell/Private-Claude.git
cd Private-Claude

# Run the activation script
chmod +x ACTIVATE_EVERYTHING.sh
./ACTIVATE_EVERYTHING.sh
```

This script will:
- ✅ Check system requirements
- ✅ Install dependencies
- ✅ Set up environment variables
- ✅ Start all 219 agents
- ✅ Launch monitoring dashboards

### Option 2: Docker (Production-Ready)
```bash
# Set up environment variables
cp config/.env.template .env
nano .env  # Edit with your API keys

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f agent-x5
```

---

## Docker Deployment

### Full Stack Deployment

The Docker Compose configuration includes:
- **agent-x5**: Main orchestrator (219 agents)
- **claude-api**: 24/7 Claude API integration
- **trading**: Paper/demo trading service
- **e2b-webhook**: Webhook server for automation
- **redis**: Caching and message queue
- **prometheus**: Metrics collection
- **grafana**: Monitoring dashboards
- **nginx**: Reverse proxy and load balancer
- **sandbox-monitor**: Trading sandbox monitoring

### Start Services
```bash
# Start all services in detached mode
docker-compose up -d

# Start specific service
docker-compose up -d agent-x5

# Scale services (e.g., multiple trading instances)
docker-compose up -d --scale trading=3
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (CAUTION: deletes data)
docker-compose down -v
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f agent-x5

# Last 100 lines
docker-compose logs --tail=100 trading
```

### Health Checks
```bash
# Check all service health
docker-compose ps

# Test specific endpoints
curl http://localhost/health
curl http://localhost:8080/health
curl http://localhost:5000/health
```

---

## Manual Deployment

### 1. Install Dependencies
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy template
cp config/.env.template .env

# Edit environment variables
nano .env
```

Required variables:
```env
# AI APIs
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here

# E2B Sandbox (optional)
E2B_API_KEY=your_key_here
E2B_WEBHOOK_SECRET=your_secret_here

# Trading (only if using live trading)
LIVE_TRADING=false
KRAKEN_API_KEY=your_key_here
BINANCE_API_KEY=your_key_here
```

### 3. Start Services

**Main Orchestrator (219 agents):**
```bash
python scripts/agent_x5_master_orchestrator.py
```

**Trading System (Paper Mode):**
```bash
python pillar-a-trading/agent-3.0/agent_3_orchestrator.py
```

**Claude API Integration:**
```bash
python core-systems/claude_api_24_7_integration.py
```

**E2B Webhook Server:**
```bash
python core-systems/e2b_webhook_server.py
```

---

## Environment Setup

### Trading Modes

**PAPER MODE (Default - No Real Money):**
```bash
export LIVE_TRADING=false
export TRADING_MODE=PAPER
```

**DEMO MODE (Exchange Demo Accounts):**
```bash
export LIVE_TRADING=false
export TRADING_MODE=DEMO
```

**LIVE MODE (Real Money - USE WITH CAUTION):**
```bash
export LIVE_TRADING=true
export TRADING_MODE=LIVE
# Requires typing: "I UNDERSTAND THE RISKS"
```

### Logging Levels
```bash
export LOG_LEVEL=INFO     # Default
export LOG_LEVEL=DEBUG    # Detailed logs
export LOG_LEVEL=WARNING  # Warnings only
export LOG_LEVEL=ERROR    # Errors only
```

---

## Testing

### Run All Tests
```bash
# Install test dependencies
pip install pytest pytest-cov pytest-asyncio

# Run test suite
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

### Run Specific Tests
```bash
# Integration tests
pytest tests/integration_test_suite.py -v

# Zapier integration tests
pytest tests/test_zapier_integrations.py -v

# Comprehensive system tests
pytest tests/comprehensive_system_test.py -v
```

### Manual Testing
```bash
# Test Agent X5 orchestrator
python scripts/agent_x5_master_orchestrator.py --test

# Test trading system (paper mode)
python pillar-a-trading/agent-3.0/agent_3_orchestrator.py --test

# Test webhook server
curl -X POST http://localhost:5000/webhook/test
```

---

## Monitoring

### Access Dashboards

**Grafana (Monitoring):**
- URL: http://localhost:3000
- Default login: admin/admin
- Dashboards: Agent performance, trading metrics, system health

**Prometheus (Metrics):**
- URL: http://localhost:9090
- Query interface for custom metrics

**NGINX Status:**
- URL: http://localhost/health
- Health check endpoint

### Key Metrics to Monitor

1. **Agent Health**
   - Active agents: 219/219
   - Response times: <500ms average
   - Error rate: <1%

2. **Trading Performance**
   - Win rate: >60% target
   - Sharpe ratio: >1.5
   - Max drawdown: <10%

3. **System Resources**
   - CPU usage: <70%
   - Memory usage: <80%
   - Disk I/O: Normal

### Logs Location
```
logs/
├── agent_x5_orchestrator.log       # Main orchestrator
├── trading_system.log               # Trading operations
├── claude_api.log                   # Claude API calls
├── e2b_webhook.log                  # Webhook events
└── system.log                       # General system logs
```

---

## Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Problem: ModuleNotFoundError
# Solution: Install dependencies
pip install -r requirements.txt
```

#### 2. Docker Permission Denied
```bash
# Problem: Permission denied accessing Docker
# Solution: Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

#### 3. Port Already in Use
```bash
# Problem: Port 8080 already in use
# Solution: Stop conflicting service or change port
docker-compose down
# Edit docker-compose.yml to use different ports
```

#### 4. API Key Errors
```bash
# Problem: Invalid API key
# Solution: Check .env file and verify keys
cat .env | grep API_KEY
# Regenerate keys from provider dashboards
```

#### 5. Redis Connection Failed
```bash
# Problem: Cannot connect to Redis
# Solution: Start Redis container
docker-compose up -d redis
# Or install locally: sudo apt-get install redis-server
```

### Debug Mode

Enable detailed logging:
```bash
export LOG_LEVEL=DEBUG
python scripts/agent_x5_master_orchestrator.py
```

Check service health:
```bash
# Docker
docker-compose ps
docker-compose logs agent-x5

# Manual
ps aux | grep python
netstat -tlnp | grep 8080
```

### Reset Everything
```bash
# Stop all services
docker-compose down -v

# Remove logs
rm -rf logs/*

# Remove cache
rm -rf __pycache__
find . -type d -name "__pycache__" -exec rm -rf {} +

# Restart
docker-compose up -d
```

---

## Security Best Practices

1. **Never commit .env files**
   - Use .env.template as reference
   - Keep API keys secret

2. **Use PAPER mode by default**
   - Only enable LIVE trading when ready
   - Test extensively in PAPER mode first

3. **Keep dependencies updated**
   ```bash
   pip list --outdated
   pip install --upgrade -r requirements.txt
   ```

4. **Monitor for security alerts**
   - Check GitHub Dependabot alerts
   - Review logs regularly

5. **Use HTTPS in production**
   - Configure SSL certificates
   - Enable nginx SSL termination

---

## Support

- **Documentation**: See `docs/` directory
- **GitHub Issues**: Report bugs and feature requests
- **System Status**: Check `AGENT_X5_STATUS_REPORT.json`

---

**Agent X5.0** - *219 Agents Working in Parallel*

*Version 5.0.0 | January 2026 | APPS Holdings WY Inc.*
