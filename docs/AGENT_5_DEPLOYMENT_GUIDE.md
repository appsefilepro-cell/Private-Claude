# Agent 5.0 - Comprehensive Deployment Guide

## Overview

Agent 5.0 is the next-generation orchestrator for Private-Claude, combining four powerful pillars:
- **Pillar A:** Automated Trading (Kraken, MetaTrader5)
- **Pillar B:** Legal Document Processing
- **Pillar C:** Federal Contracting (SAM.gov)
- **Pillar D:** Nonprofit Automation (Forms 1023/1023-EZ)

With integrated E2B code execution, GitHub synchronization, Zapier automation, and Slack notifications.

## System Architecture

```
Agent 5.0 Orchestrator
├── E2B Code Executor (Dynamic code execution & testing)
├── GitHub Syncer (Repository sync & PR creation)
├── Zapier Integrator (Automated workflows)
├── Slack Notifier (Real-time alerts)
├── Loop Control Manager (10x execution pattern)
└── Pillar Orchestrators
    ├── Trading Automator (Kraken, MT5)
    ├── Legal Processor (Documents, Forensics)
    ├── Federal Monitor (SAM.gov, Opportunities)
    └── Nonprofit Automator (Grants, Forms)
```

## Prerequisites

### Required Software
- Python 3.9+
- Git 2.35+
- Node.js 16+ (for Replit integration)

### Required Accounts & Credentials
1. **E2B Code Interpreter**
   - API Key: `E2B_API_KEY`
   - Webhook ID: `YIyOpaJ0UMJ3Pl9Md5kVExEDdkqyDGRp`

2. **GitHub**
   - Repository: `appsefilepro-cell/Private-Claude`
   - Personal Access Token: `GITHUB_TOKEN`
   - Branch: `claude/setup-e2b-webhooks-CPFBo`

3. **Zapier MCP**
   - Bearer Token: `ZAPIER_MCP_BEARER_TOKEN`
   - Endpoint: `ZAPIER_MCP_ENDPOINT`

4. **Slack**
   - Workspace: `apps-holdings`
   - Bot Token: `SLACK_BOT_TOKEN`
   - Webhook URL: `SLACK_WEBHOOK_URL`

5. **Microsoft 365**
   - Tenant: `APPSHOLDINGSWYINC.onmicrosoft.com`
   - Client ID: `MICROSOFT_CLIENT_ID`
   - Client Secret: `MICROSOFT_CLIENT_SECRET`

6. **Trading APIs**
   - Kraken API Key: `KRAKEN_API_KEY`
   - Kraken Secret: `KRAKEN_SECRET_KEY`
   - MetaTrader5: Configured locally

7. **Federal/Nonprofit**
   - SAM.gov API Key: `SAM_GOV_API_KEY`
   - Grants.gov Account: `GRANTS_GOV_USERNAME`

## Installation & Configuration

### Step 1: Environment Setup

```bash
# Clone repository
cd /home/user/Private-Claude

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp config/.env.template config/.env
```

### Step 2: Configure Environment Variables

Edit `config/.env`:

```bash
# E2B Configuration
E2B_API_KEY=your_e2b_api_key
E2B_WEBHOOK_ID=YIyOpaJ0UMJ3Pl9Md5kVExEDdkqyDGRp

# GitHub
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_REPOSITORY=appsefilepro-cell/Private-Claude

# Zapier
ZAPIER_MCP_BEARER_TOKEN=your_zapier_bearer_token
ZAPIER_MCP_ENDPOINT=https://your_zapier_endpoint.com

# Slack
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Microsoft 365
MICROSOFT_CLIENT_ID=your_client_id
MICROSOFT_CLIENT_SECRET=your_client_secret
MICROSOFT_TENANT_ID=your_tenant_id
SHAREPOINT_SITE_URL=https://appsholdingswyinc.sharepoint.com

# Kraken
KRAKEN_API_KEY=your_kraken_api_key
KRAKEN_SECRET_KEY=your_kraken_secret

# SAM.gov
SAM_GOV_API_KEY=your_sam_gov_api_key

# Gmail
GMAIL_SERVICE_ACCOUNT_JSON=path_to_service_account.json
```

### Step 3: Verify Configuration

```bash
# Verify Agent 5.0 configuration
python3 -c "import json; config = json.load(open('config/agent_5_config.json')); print(f'Agent 5.0 v{config[\"system_metadata\"][\"version\"]} loaded successfully')"
```

## Running Agent 5.0

### Basic Execution

```bash
# Run 10x execution loop
python3 scripts/agent_5_orchestrator.py
```

### With Specific Settings

```bash
# Run with debug logging
PYTHONUNBUFFERED=1 python3 scripts/agent_5_orchestrator.py 2>&1 | tee logs/agent_5_debug.log

# Run with dry-run mode (simulations only)
export DRY_RUN=1
python3 scripts/agent_5_orchestrator.py
```

### Output & Logs

Execution logs are saved to:
- **Main Log:** `logs/agent_5_orchestrator.log`
- **Execution Report:** `logs/agent_5_report_YYYYMMDD_HHMMSS.json`
- **Activation Log:** `logs/activation_YYYYMMDD_HHMMSS.json`

## Agent Forge Replit Integration

### Setup Steps

#### 1. Connect to Replit

```bash
# Navigate to Replit
# URL: https://72f0ad6a-efdf-4560-b50f-596680549d29-00-auxmaxx8t7os.kirk.replit.dev/

# Login with account: appsefilepro@gmail.com
```

#### 2. GitHub Integration

In Replit, connect to GitHub:

1. Go to **Settings** → **GitHub**
2. Authorize with: `appsefilepro-cell/Private-Claude`
3. Set branch to: `claude/setup-e2b-webhooks-CPFBo`
4. Enable Auto-Deploy

#### 3. Environment Variables in Replit

In Replit **Secrets**:

```
E2B_API_KEY=your_value
GITHUB_TOKEN=your_value
ZAPIER_MCP_BEARER_TOKEN=your_value
SLACK_BOT_TOKEN=your_value
KRAKEN_API_KEY=your_value
MICROSOFT_CLIENT_SECRET=your_value
SAM_GOV_API_KEY=your_value
```

#### 4. Deploy Agent 5.0

```bash
# In Replit Terminal
cd /home/user/Private-Claude

# Install dependencies
pip install -r requirements.txt

# Run orchestrator
python3 scripts/agent_5_orchestrator.py
```

#### 5. Create Replit Web Server (Optional)

Create `.replit`:

```toml
run = "python3 scripts/agent_5_orchestrator.py"
modules = ["python3-pip"]
hidden = [".git", ".gitignore", "venv"]
```

## 10x Execution Loop Pattern

Agent 5.0 implements a 10x loop control pattern for systematic execution:

### Execution Flow

```
Iteration 1: Initialize → Execute All Pillars → Checkpoint (1 of 5)
Iteration 2: Execute All Pillars → Create Sync Data
Iteration 3: Execute All Pillars → Checkpoint (2 of 5)
Iteration 4: Execute All Pillars → Create Sync Data
Iteration 5: Execute All Pillars → Checkpoint (3 of 5)
Iteration 6: Execute All Pillars → Create Sync Data
Iteration 7: Execute All Pillars → Checkpoint (4 of 5)
Iteration 8: Execute All Pillars → Create Sync Data
Iteration 9: Execute All Pillars → Checkpoint (5 of 5)
Iteration 10: Execute All Pillars → Generate Final Report
```

### Loop Control Configuration

In `config/agent_5_config.json`:

```json
{
  "loop_control": {
    "execution_pattern": "10x",
    "max_iterations": 10,
    "iteration_delay_seconds": 2,
    "checkpoint_interval": 2,
    "failure_recovery": true,
    "rollback_on_critical_error": true,
    "health_check_enabled": true
  }
}
```

## Integration Details

### E2B Code Execution

E2B enables dynamic code execution with sandboxed environments:

```python
# Code executed safely in E2B sandbox
code = """
import json
results = {
    "analysis": "data_processed",
    "status": "success"
}
print(json.dumps(results))
"""
result = await e2b_executor.execute_code(code, description="Trading analysis")
```

### GitHub Synchronization

Automatic sync of execution results and reports:

- **Commits:** Iteration results committed to GitHub
- **Pull Requests:** Automated PR creation for major changes
- **Branch:** `claude/setup-e2b-webhooks-CPFBo`
- **Repository:** `appsefilepro-cell/Private-Claude`

### Zapier Automation

Triggered Zaps for workflow automation:

```python
# Trigger Zapier workflows
await zapier_integrator.trigger_zap(
    "Grant Opportunity Found",
    {"opportunity_id": "123", "amount": 50000}
)
```

### Slack Notifications

Real-time alerts to Slack channels:

- **#trading-alerts:** Trading signals and executions
- **#legal-operations:** Legal document processing
- **#federal-contracting:** SAM.gov opportunities
- **#nonprofit-automation:** Grant discoveries
- **#agent-5-execution:** Execution status
- **#errors-and-alerts:** Critical errors

## Monitoring & Troubleshooting

### Health Checks

```bash
# Check system status
python3 scripts/api_manager.py check_health

# Verify all integrations
python3 -c "
import json
from pathlib import Path
config = json.load(open('config/agent_5_config.json'))
for key in ['e2b_integration', 'github_integration', 'zapier_integration', 'slack_integration']:
    status = config.get(key, {}).get('enabled', False)
    print(f'{key}: {\"ENABLED\" if status else \"DISABLED\"}')"
```

### Common Issues

#### 1. E2B API Errors
```
Error: "API key invalid"
Solution: Verify E2B_API_KEY in config/.env
```

#### 2. GitHub Authentication
```
Error: "GitHub token expired"
Solution: Regenerate GITHUB_TOKEN, update config/.env
```

#### 3. Zapier Integration
```
Error: "Zapier endpoint unreachable"
Solution: Verify ZAPIER_MCP_ENDPOINT is correct and accessible
```

#### 4. Slack Connection
```
Error: "Slack bot token invalid"
Solution: Regenerate SLACK_BOT_TOKEN in Slack workspace
```

### Logs & Debugging

View real-time logs:

```bash
# Main orchestrator log
tail -f logs/agent_5_orchestrator.log

# Latest report
cat logs/agent_5_report_*.json | tail -1 | python3 -m json.tool
```

## Performance Optimization

### Data Efficiency

Agent 5.0 implements several optimization techniques:

1. **Payload Compression:** Gzip compression for API payloads
2. **Connection Pooling:** Reuse HTTP connections (pool_size: 20)
3. **Batch Processing:** Process data in batches (batch_size: 100)
4. **Caching:** Redis-compatible caching (TTL: 3600s)
5. **Async/Await:** Non-blocking operations throughout

### Configuration for Optimization

```json
{
  "performance_optimization": {
    "caching_enabled": true,
    "cache_ttl_seconds": 3600,
    "batch_processing": true,
    "batch_size": 100,
    "parallel_execution": true,
    "max_concurrent_tasks": 10,
    "compression": {
      "enabled": true,
      "algorithm": "gzip",
      "min_size_bytes": 1024
    }
  }
}
```

## Security Best Practices

1. **Never commit credentials:**
   ```bash
   git config core.hooksPath .git-hooks
   ```

2. **Rotate API keys regularly:**
   - Update in config/.env
   - Regenerate in respective platforms
   - Test connections after rotation

3. **Enable MFA on critical accounts:**
   - GitHub
   - Microsoft 365
   - Zapier
   - AWS/Cloud accounts

4. **Audit access logs:**
   ```bash
   tail -f logs/agent_5_orchestrator.log | grep -i "error\|unauthorized"
   ```

5. **Use environment variables:**
   - Never hardcode credentials in code
   - Use .env file locally, Replit Secrets for deployment

## Maintenance & Updates

### Daily Tasks

```bash
# Check execution status
tail -20 logs/agent_5_orchestrator.log

# Verify GitHub sync
git status
git log --oneline -5
```

### Weekly Tasks

```bash
# Review execution reports
ls -lrt logs/agent_5_report_*.json | tail -7

# Check integration health
python3 scripts/api_manager.py check_all_integrations
```

### Monthly Tasks

1. Review and rotate API keys
2. Update dependencies: `pip install --upgrade -r requirements.txt`
3. Audit access logs and permissions
4. Test disaster recovery procedures

## Advanced Configuration

### Custom Loop Control

```python
from scripts.agent_5_orchestrator import Agent5Orchestrator

orchestrator = Agent5Orchestrator()
orchestrator.loop_control.max_iterations = 20  # 20x loop
orchestrator.loop_control.checkpoint_interval = 3  # Every 3 iterations

# Run extended execution
report = await orchestrator.run_10x_loop()
```

### Pillar-Specific Configuration

Edit `config/agent_5_config.json` for pillar-specific settings:

```json
{
  "pillar_a_trading": {
    "trading_pairs": ["BTC/USD", "ETH/USD"],
    "risk_management": {
      "max_position_size": 0.02,
      "risk_per_trade": 0.01
    }
  }
}
```

## Support & Documentation

- **Configuration:** `/home/user/Private-Claude/config/agent_5_config.json`
- **Scripts:** `/home/user/Private-Claude/scripts/`
- **Logs:** `/home/user/Private-Claude/logs/`
- **Tests:** `/home/user/Private-Claude/tests/`

## Version History

- **v5.0.0** (2025-12-21): Initial release with full pillar integration
  - E2B code execution
  - GitHub synchronization
  - Zapier automation
  - 10x loop control pattern
  - Multi-service integration

---

**Agent 5.0** - *Advanced Enterprise Automation*
*Deployed: December 21, 2025 | APPS Holdings WY Inc.*
