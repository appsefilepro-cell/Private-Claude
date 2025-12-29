# Agent X5.0 - Complete Deployment Guide
## Version 5.0.0 - Production Ready

**Last Updated:** 2025-12-29
**Author:** Agent X5 Automation System

---

## 📋 WHAT'S NEW - REAL IMPLEMENTATIONS

This update includes **REAL, WORKING implementations** (NO placeholders):

### ✅ New Core Components

1. **Claude API 24/7 Integration** (`core-systems/claude_api_24_7_integration.py`)
   - Real Anthropic API integration
   - Continuous monitoring and task analysis
   - Conversation management with context
   - Batch processing capabilities

2. **E2B Webhook Server** (`core-systems/e2b_webhook_server.py`)
   - Flask-based webhook receiver
   - Multiple endpoints (E2B, Zapier, Trading)
   - Event logging and storage
   - Health checks and monitoring

3. **Sandbox Environment Setup** (`scripts/setup_sandbox_environment.sh`)
   - Automated installation and configuration
   - Dependency installation
   - Directory structure creation
   - Service startup scripts

4. **GitHub Actions CI/CD** (`.github/workflows/agent-x5-master-automation.yml`)
   - Parallel execution across repositories
   - Automated error fixing
   - PR merging
   - Version updates
   - Docker builds
   - Continuous monitoring

5. **Production Docker Stack** (`docker-compose.yml`)
   - 9 services fully configured
   - Prometheus monitoring
   - Grafana dashboards
   - NGINX reverse proxy
   - Redis caching
   - All services interconnected

6. **Complete Requirements** (`requirements.txt`)
   - All real package versions
   - Organized by category
   - Production-tested dependencies

---

## 🚀 QUICK START - THREE WAYS TO DEPLOY

### Option 1: Automated Sandbox Setup (Recommended for First Time)

```bash
# 1. Make setup script executable
chmod +x scripts/setup_sandbox_environment.sh

# 2. Run automated setup
./scripts/setup_sandbox_environment.sh

# 3. Configure API keys (opens in editor)
nano config/.env  # Add your API keys

# 4. Start all services
./start_sandbox_24_7.sh
```

### Option 2: Docker Deployment (Recommended for Production)

```bash
# 1. Configure environment
cp config/.env.template config/.env
nano config/.env  # Add your API keys

# 2. Build and start all containers
docker-compose up -d

# 3. Check status
docker-compose ps
docker-compose logs -f

# 4. Access services
# - Agent X5: http://localhost:8080
# - E2B Webhooks: http://localhost:5000
# - Grafana: http://localhost:3000
# - Prometheus: http://localhost:9090
```

### Option 3: Manual Python Execution (Development)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp config/.env.template config/.env
nano config/.env

# 3. Start components individually

# Agent X5 Orchestrator (219 agents)
python3 scripts/agent_x5_master_orchestrator.py &

# Claude API Integration
python3 core-systems/claude_api_24_7_integration.py &

# E2B Webhook Server
python3 core-systems/e2b_webhook_server.py &

# Sandbox Monitor
python3 scripts/sandbox_trading_monitor.py &

# Trading System
python3 pillar-a-trading/agent-3.0/agent_3_orchestrator.py &
```

---

## 🔑 REQUIRED API KEYS

Add these to `config/.env`:

### CRITICAL (Required for core functionality):

```bash
# Claude API (24/7 operations)
ANTHROPIC_API_KEY=sk-ant-api03-...  # Get from: https://console.anthropic.com/

# E2B Sandbox (already configured)
E2B_API_KEY=e2b_fcc08e8c733b3eab00bdb3ad5857f5966afc2773

# Gemini (already configured)
GEMINI_API_KEY=AIzaSyBqAbzJdyg7sP5tIhCddWk4Q1EEmSZSCT4
```

### OPTIONAL (Enhanced features):

```bash
# OpenAI (ChatGPT integration)
OPENAI_API_KEY=sk-...  # Get from: https://platform.openai.com/

# Trading APIs (for live/sandbox trading)
KRAKEN_API_KEY=...
BINANCE_API_KEY=...
ALPACA_API_KEY=...

# Zapier (automation)
ZAPIER_API_KEY=...

# Microsoft 365
MICROSOFT_CLIENT_ID=...

# Google Workspace
GOOGLE_CLIENT_ID=...
```

---

## 📊 SERVICE ARCHITECTURE

```
┌──────────────────────────────────────────────────────────────┐
│                      NGINX (Port 80/443)                     │
│                   Reverse Proxy & Load Balancer              │
└───────────────────────────┬──────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼───────┐   ┌──────▼──────┐   ┌───────▼────────┐
│  Agent X5     │   │   Claude    │   │   E2B Webhook  │
│ Orchestrator  │   │  API 24/7   │   │     Server     │
│  (219 Agents) │   │ Integration │   │   (Port 5000)  │
│  (Port 8080)  │   │             │   │                │
└───────┬───────┘   └──────┬──────┘   └───────┬────────┘
        │                  │                   │
        └──────────────────┼───────────────────┘
                           │
                   ┌───────▼───────┐
                   │     REDIS     │
                   │  Cache & MQ   │
                   │  (Port 6379)  │
                   └───────┬───────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼───────┐  ┌──────▼──────┐  ┌───────▼────────┐
│    Trading    │  │  Sandbox    │  │  Prometheus    │
│    System     │  │   Monitor   │  │   Monitoring   │
│  (Port 8082)  │  │             │  │  (Port 9090)   │
└───────────────┘  └─────────────┘  └───────┬────────┘
                                             │
                                     ┌───────▼────────┐
                                     │    Grafana     │
                                     │   Dashboards   │
                                     │  (Port 3000)   │
                                     └────────────────┘
```

---

## 🧪 TESTING THE DEPLOYMENT

### 1. Test Health Checks

```bash
# Agent X5
curl http://localhost:8080/health

# E2B Webhook
curl http://localhost:5000/health

# Prometheus
curl http://localhost:9090/-/healthy

# Redis
redis-cli ping
```

### 2. Test Claude API Integration

```bash
python3 core-systems/claude_api_24_7_integration.py
```

Expected output:
```
✅ Claude API is ready!
🧪 Testing API connection...
Claude: [Response confirming connection]
```

### 3. Test E2B Webhooks

```bash
# Send test webhook
curl -X POST http://localhost:5000/webhook/e2b \
  -H "Content-Type: application/json" \
  -d '{"type": "test", "data": "hello"}'

# Check received events
curl http://localhost:5000/events?limit=10
```

### 4. Test Sandbox Environment

```bash
python3 scripts/sandbox_trading_monitor.py
```

Expected output:
```
🎯 AGENT 3.0 - SANDBOX TRADING MONITOR
✅ Agent 3.0 configuration created
✅ SANDBOX TRADING PERFORMANCE REPORT
```

### 5. Test Docker Stack

```bash
# Start all services
docker-compose up -d

# Wait 30 seconds for startup
sleep 30

# Check all containers are running
docker-compose ps

# View logs
docker-compose logs --tail=50

# Check each service
docker-compose exec agent-x5 python -c "print('Agent X5 OK')"
docker-compose exec redis redis-cli ping
```

---

## 📈 MONITORING & OBSERVABILITY

### Access Dashboards

1. **Grafana** (http://localhost:3000)
   - Username: admin
   - Password: admin (default, change immediately)
   - Preconfigured dashboards for all services

2. **Prometheus** (http://localhost:9090)
   - Metrics from all services
   - Query builder
   - Alert rules

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f agent-x5
docker-compose logs -f claude-api
docker-compose logs -f e2b-webhook

# Python logs (if running manually)
tail -f logs/agents/*.log
tail -f logs/trading/*.log
tail -f logs/webhooks/*.jsonl
```

### Metrics to Monitor

- **Agent X5**: Active agents, task queue, completion rate
- **Claude API**: Requests/min, token usage, error rate
- **Trading**: Open positions, P&L, win rate
- **Webhooks**: Events/min, processing time, failures
- **Redis**: Memory usage, hit rate, connected clients

---

## 🔄 GITHUB ACTIONS AUTOMATION

The workflow automatically:

1. ✅ **Analyzes** all repositories for issues
2. ✅ **Fixes** code errors and formatting
3. ✅ **Completes** unfinished tasks in parallel
4. ✅ **Merges** approved pull requests
5. ✅ **Updates** version numbers to 5.0
6. ✅ **Deploys** to sandbox environment
7. ✅ **Builds** Docker images
8. ✅ **Monitors** 24/7 operations
9. ✅ **Generates** status reports

### Manual Trigger

```bash
# Trigger workflow manually
gh workflow run agent-x5-master-automation.yml

# Check workflow status
gh run list --workflow=agent-x5-master-automation.yml

# View logs
gh run view --log
```

### Scheduled Runs

- Runs every 6 hours automatically
- Runs on every push to `main`, `master`, or `claude/**` branches
- Runs on every pull request

---

## 🐳 DOCKER COMMANDS REFERENCE

### Start Services

```bash
docker-compose up -d                 # Start in background
docker-compose up                    # Start with logs
docker-compose up -d agent-x5        # Start specific service
```

### Stop Services

```bash
docker-compose down                  # Stop all
docker-compose stop agent-x5         # Stop specific service
docker-compose restart claude-api    # Restart service
```

### View Status

```bash
docker-compose ps                    # List containers
docker-compose top                   # Show processes
docker stats                         # Resource usage
```

### Maintenance

```bash
docker-compose pull                  # Update images
docker-compose build --no-cache      # Rebuild from scratch
docker-compose logs --tail=100 -f    # Follow logs
docker system prune -a              # Clean up (careful!)
```

---

## 🔧 TROUBLESHOOTING

### Claude API Not Working

```bash
# Check API key
grep ANTHROPIC_API_KEY config/.env

# Test manually
python3 -c "from anthropic import Anthropic; print(Anthropic(api_key='YOUR_KEY').messages.create(model='claude-3-5-sonnet-20241022', max_tokens=100, messages=[{'role':'user','content':'test'}]))"
```

### E2B Webhooks Not Receiving Events

```bash
# Check server is running
curl http://localhost:5000/health

# Check logs
tail -f logs/webhooks/*.jsonl

# Test with curl
curl -X POST http://localhost:5000/webhook/e2b -H "Content-Type: application/json" -d '{"test": "data"}'
```

### Docker Containers Not Starting

```bash
# Check logs
docker-compose logs service-name

# Check resources
docker stats

# Rebuild
docker-compose build --no-cache
docker-compose up -d --force-recreate
```

### Redis Connection Issues

```bash
# Test Redis
docker-compose exec redis redis-cli ping

# Check connections
docker-compose exec redis redis-cli CLIENT LIST

# Restart Redis
docker-compose restart redis
```

---

## 📝 IMPORTANT NOTES

### Trading Safety

⚠️ **DEFAULT MODE: PAPER TRADING (SAFE)**
- No real money at risk
- All trading is simulated
- Data is real, execution is fake

To enable LIVE trading:
```bash
# Only do this when ready for real money!
export LIVE_TRADING=true
```

### API Rate Limits

- **Claude API**: Be mindful of rate limits
- **Gemini API**: 60 requests/min (FREE tier)
- **OpenAI**: Varies by plan
- **E2B**: Check your plan limits

### Resource Requirements

Minimum:
- 4 GB RAM
- 2 CPU cores
- 10 GB disk space

Recommended:
- 8 GB RAM
- 4 CPU cores
- 50 GB disk space
- SSD storage

---

## 🎯 NEXT STEPS

1. **Configure API Keys** - Add all your API keys to `config/.env`
2. **Test Each Service** - Follow the testing section above
3. **Deploy to Production** - Use Docker Compose for 24/7 operation
4. **Set Up Monitoring** - Configure Grafana dashboards
5. **Enable GitHub Actions** - Push to trigger automated workflows
6. **Review Logs** - Monitor for any issues

---

## 📞 SUPPORT

- **Issues**: Check logs in `logs/` directory
- **Errors**: Review `logs/agents/` for agent-specific issues
- **Webhooks**: Check `logs/webhooks/` for event logs
- **GitHub**: Check Actions tab for workflow runs

---

## 🎉 SUCCESS CHECKLIST

- ✅ All dependencies installed (`requirements.txt`)
- ✅ Environment configured (`.env` file)
- ✅ Docker containers running (`docker-compose ps`)
- ✅ Health checks passing (all `/health` endpoints return 200)
- ✅ Claude API connected (test script runs successfully)
- ✅ Webhooks receiving events (test with curl)
- ✅ Monitoring active (Grafana accessible)
- ✅ Logs being written (check `logs/` directory)
- ✅ GitHub Actions enabled (workflow visible in repo)

---

**Agent X5.0 - Ready for Production** 🚀

Version 5.0.0 | December 29, 2025 | APPS Holdings WY Inc.
