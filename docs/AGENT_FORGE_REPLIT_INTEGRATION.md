# Agent 5.0 - Agent Forge Replit Integration Guide

## Overview

Agent Forge Replit provides a cloud-hosted environment for running Agent 5.0 orchestrator with:
- **Replit URL:** https://72f0ad6a-efdf-4560-b50f-596680549d29-00-auxmaxx8t7os.kirk.replit.dev/
- **Account:** appsefilepro@gmail.com
- **GitHub Repository:** appsefilepro-cell/Private-Claude
- **Branch:** claude/setup-e2b-webhooks-CPFBo

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Replit Environment                     │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐│
│  │         Agent 5.0 Orchestrator                      ││
│  │  ┌──────────────────────────────────────────────┐  ││
│  │  │  10x Loop Control Manager                    │  ││
│  │  └──────────────────────────────────────────────┘  ││
│  │  ┌──────────────────────────────────────────────┐  ││
│  │  │  Pillar Orchestrators                        │  ││
│  │  │  - Trading (A)                               │  ││
│  │  │  - Legal (B)                                 │  ││
│  │  │  - Federal (C)                               │  ││
│  │  │  - Nonprofit (D)                             │  ││
│  │  └──────────────────────────────────────────────┘  ││
│  └─────────────────────────────────────────────────────┘│
│                                                         │
│  ┌─────────────────────────────────────────────────────┐│
│  │         Integration Managers                        ││
│  ├─────────────────────────────────────────────────────┤│
│  │ E2B Executor │ GitHub Syncer │ Zapier │ Slack       ││
│  └─────────────────────────────────────────────────────┘│
│                                                         │
│  ┌─────────────────────────────────────────────────────┐│
│  │         External Integrations                       ││
│  ├─────────────────────────────────────────────────────┤│
│  │ GitHub │ Zapier │ E2B │ Slack │ M365 │ Kraken       ││
│  └─────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

## Setup Instructions

### Step 1: Access Replit

1. Navigate to: https://72f0ad6a-efdf-4560-b50f-596680549d29-00-auxmaxx8t7os.kirk.replit.dev/
2. Sign in with: appsefilepro@gmail.com
3. Create password if first time

### Step 2: Clone Repository in Replit

In Replit terminal:

```bash
# Clone the repository
git clone https://github.com/appsefilepro-cell/Private-Claude.git
cd Private-Claude

# Checkout correct branch
git checkout claude/setup-e2b-webhooks-CPFBo

# Verify configuration
ls -la config/agent_5_config.json
```

### Step 3: Set Environment Variables

In Replit **Secrets** (Shield icon in left sidebar):

```
# E2B Configuration
E2B_API_KEY=your_e2b_api_key
E2B_WEBHOOK_ID=YIyOpaJ0UMJ3Pl9Md5kVExEDdkqyDGRp

# GitHub Integration
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_REPOSITORY=appsefilepro-cell/Private-Claude

# Zapier Integration
ZAPIER_MCP_BEARER_TOKEN=your_zapier_bearer_token
ZAPIER_MCP_ENDPOINT=https://your_zapier_endpoint.com

# Slack Integration
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Microsoft 365
MICROSOFT_CLIENT_ID=your_client_id
MICROSOFT_CLIENT_SECRET=your_client_secret
MICROSOFT_TENANT_ID=your_tenant_id
SHAREPOINT_SITE_URL=https://appsholdingswyinc.sharepoint.com

# Trading APIs
KRAKEN_API_KEY=your_kraken_api_key
KRAKEN_SECRET_KEY=your_kraken_secret

# Federal/Nonprofit
SAM_GOV_API_KEY=your_sam_gov_api_key
GRANTS_GOV_USERNAME=your_grants_gov_username
```

### Step 4: Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Verify installation
python3 -c "import json; print('Dependencies installed successfully')"
```

### Step 5: Configure .env File

```bash
# Copy template
cp config/.env.template config/.env

# Edit with Replit environment variables
# The .env will automatically use Replit Secrets
```

### Step 6: Verify Configuration

```bash
# Check Agent 5.0 config
python3 << 'EOF'
import json
with open('config/agent_5_config.json', 'r') as f:
    config = json.load(f)

print(f"Agent Version: {config['system_metadata']['version']}")
print(f"Status: {config['system_metadata']['status']}")
print(f"Pillars Enabled:")
print(f"  - Trading: {config['pillar_a_trading']['enabled']}")
print(f"  - Legal: {config['pillar_b_legal']['enabled']}")
print(f"  - Federal: {config['pillar_c_federal']['enabled']}")
print(f"  - Nonprofit: {config['pillar_d_nonprofit']['enabled']}")
print(f"E2B Integration: {config['e2b_integration']['enabled']}")
print(f"Loop Control: {config['loop_control']['max_iterations']}x pattern")
EOF
```

## Running Agent 5.0 in Replit

### Method 1: Direct Execution

```bash
python3 scripts/agent_5_orchestrator.py
```

### Method 2: Using .replit Configuration

Create/edit `.replit` file:

```toml
run = "python3 scripts/agent_5_orchestrator.py"
entrypoint = "scripts/agent_5_orchestrator.py"

modules = ["python3-10"]

hidden = [".git", ".gitignore", "*.pyc", "__pycache__", "venv", "*.log"]

[env]
PYTHONUNBUFFERED = "1"

[nix]
channel = "unstable"

[packager]
language = "python3"
ignoredPaths = ["*/__pycache__"]

[[ports]]
localPort = 3000
externalPort = 3000

[gitHubIntegration]
owner = "appsefilepro-cell"
repo = "Private-Claude"
branch = "claude/setup-e2b-webhooks-CPFBo"
autoSync = true
```

### Method 3: Web Server with HTTP Interface

Create `replit_server.py`:

```python
#!/usr/bin/env python3
"""
Replit Web Server for Agent 5.0
Provides HTTP interface for orchestration
"""

import json
import asyncio
from flask import Flask, jsonify, request
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from scripts.agent_5_orchestrator import Agent5Orchestrator

app = Flask(__name__)
orchestrator = None

@app.route('/', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Agent 5.0 Orchestrator",
        "version": "5.0.0"
    })

@app.route('/config', methods=['GET'])
def get_config():
    """Get Agent 5.0 configuration"""
    try:
        with open('config/agent_5_config.json', 'r') as f:
            config = json.load(f)
        return jsonify(config)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/execute', methods=['POST'])
def execute_agent():
    """Execute Agent 5.0 orchestration"""
    try:
        async def run():
            orchestrator = Agent5Orchestrator()
            report = await orchestrator.run_10x_loop()
            return report

        # Run async task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        report = loop.run_until_complete(run())

        return jsonify(report)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    """Get current orchestration status"""
    try:
        with open('logs/agent_5_orchestrator.log', 'r') as f:
            lines = f.readlines()[-20:]  # Last 20 lines
        return jsonify({
            "status": "running",
            "recent_logs": lines
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/report/latest', methods=['GET'])
def get_latest_report():
    """Get latest execution report"""
    try:
        log_dir = Path('logs')
        reports = list(log_dir.glob('agent_5_report_*.json'))
        if reports:
            latest = sorted(reports)[-1]
            with open(latest, 'r') as f:
                report = json.load(f)
            return jsonify(report)
        return jsonify({"error": "No reports found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=False)
```

Run web server:

```bash
pip install flask
python3 replit_server.py
```

## GitHub Auto-Sync Configuration

### Enable GitHub Integration in Replit

1. Click **Source Control** (Git icon) in left sidebar
2. Click **Connect Repository**
3. Authorize with GitHub account
4. Select repository: `appsefilepro-cell/Private-Claude`
5. Select branch: `claude/setup-e2b-webhooks-CPFBo`

### Auto-Commit Execution Results

Add to `.replit`:

```toml
[gitHubIntegration]
owner = "appsefilepro-cell"
repo = "Private-Claude"
branch = "claude/setup-e2b-webhooks-CPFBo"
autoSync = true
autoCommit = true
commitMessage = "Agent 5.0: {iteration} execution - {timestamp}"
```

## Monitoring & Logs

### View Real-Time Logs

```bash
# In Replit terminal
tail -f logs/agent_5_orchestrator.log
```

### View Execution Reports

```bash
# List all reports
ls -lrt logs/agent_5_report_*.json

# View latest report (formatted)
python3 -m json.tool logs/agent_5_report_*.json | tail -50
```

### Monitor Integrations

```bash
# Check E2B executions
grep "E2B" logs/agent_5_orchestrator.log

# Check GitHub syncs
grep "GitHub" logs/agent_5_orchestrator.log

# Check Zapier triggers
grep "Zapier" logs/agent_5_orchestrator.log

# Check Slack notifications
grep "Slack" logs/agent_5_orchestrator.log
```

## Scheduling Execution

### Using Replit UPS (Always-On)

Replit UPS (Unlimited Personal Storage) allows 24/7 execution:

1. Click **Tools** → **Upgrade**
2. Enable **Replit UPS**
3. Script will run continuously

### Using Cron Schedule (Advanced)

Create `cron_scheduler.py`:

```python
import schedule
import time
import subprocess
from datetime import datetime

def run_agent():
    print(f"Starting Agent 5.0 execution - {datetime.now()}")
    result = subprocess.run(['python3', 'scripts/agent_5_orchestrator.py'], capture_output=True)
    print(f"Execution completed - {datetime.now()}")

# Schedule execution every 6 hours
schedule.every(6).hours.do(run_agent)

while True:
    schedule.run_pending()
    time.sleep(60)
```

Run scheduler:

```bash
pip install schedule
python3 cron_scheduler.py
```

## Troubleshooting in Replit

### Issue: Module Not Found

```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### Issue: Secret Not Accessible

```bash
# Verify secrets are set
python3 << 'EOF'
import os
secrets = ['E2B_API_KEY', 'GITHUB_TOKEN', 'ZAPIER_MCP_BEARER_TOKEN']
for secret in secrets:
    status = "SET" if os.getenv(secret) else "NOT SET"
    print(f"{secret}: {status}")
EOF
```

### Issue: Git Push Failed

```bash
# Check git configuration
git config --list

# Configure git user (if needed)
git config user.email "appsefilepro@gmail.com"
git config user.name "Agent 5.0"

# Retry push
git push origin claude/setup-e2b-webhooks-CPFBo
```

### Issue: Memory/CPU Limits

Monitor resource usage:

```bash
# Check resource limits
cat /proc/meminfo
cat /proc/cpuinfo

# Reduce concurrent tasks if needed
export MAX_CONCURRENT_TASKS=5
```

## Performance Optimization in Replit

### Memory Management

```python
# In agent_5_orchestrator.py
import gc

async def optimize_memory():
    """Force garbage collection between iterations"""
    gc.collect()
    gc.enable()
```

### Connection Pooling

Agent 5.0 uses connection pooling by default:

```json
{
  "performance_optimization": {
    "connection_pooling": true,
    "pool_size": 20
  }
}
```

### Batch Processing

Configure batch size in `config/agent_5_config.json`:

```json
{
  "performance_optimization": {
    "batch_processing": true,
    "batch_size": 100
  }
}
```

## Security in Replit

### Secure Secrets Storage

1. All secrets stored in Replit Secrets (encrypted)
2. Never print secrets to console
3. Never commit .env file

### Network Security

1. All external APIs use HTTPS
2. Webhook signatures verified
3. Rate limiting enabled

### Code Security

```bash
# Scan for vulnerabilities
pip install bandit
bandit -r scripts/

# Check dependencies
pip audit
```

## Integration Health Checks

Create `health_check.py`:

```python
#!/usr/bin/env python3
import json
import os
import asyncio
from datetime import datetime

async def check_integrations():
    """Health check for all integrations"""
    print(f"Integration Health Check - {datetime.now()}")
    print("-" * 50)

    checks = {
        "E2B API": os.getenv('E2B_API_KEY') is not None,
        "GitHub Token": os.getenv('GITHUB_TOKEN') is not None,
        "Zapier Bearer": os.getenv('ZAPIER_MCP_BEARER_TOKEN') is not None,
        "Slack Token": os.getenv('SLACK_BOT_TOKEN') is not None,
        "Microsoft Config": all([
            os.getenv('MICROSOFT_CLIENT_ID'),
            os.getenv('MICROSOFT_CLIENT_SECRET'),
            os.getenv('MICROSOFT_TENANT_ID')
        ]),
        "Kraken API": os.getenv('KRAKEN_API_KEY') is not None,
        "SAM.gov API": os.getenv('SAM_GOV_API_KEY') is not None,
    }

    for service, status in checks.items():
        status_str = "✓ OK" if status else "✗ MISSING"
        print(f"{service:<25} {status_str}")

    print("-" * 50)
    all_ok = all(checks.values())
    print(f"Overall Status: {'HEALTHY' if all_ok else 'DEGRADED'}")

if __name__ == "__main__":
    asyncio.run(check_integrations())
```

Run health checks:

```bash
python3 health_check.py
```

## Support & Documentation

### Files in Replit

- **Configuration:** `config/agent_5_config.json`
- **Orchestrator:** `scripts/agent_5_orchestrator.py`
- **Logs:** `logs/agent_5_orchestrator.log`
- **Reports:** `logs/agent_5_report_*.json`
- **Deployment Guide:** `docs/AGENT_5_DEPLOYMENT_GUIDE.md`

### Getting Help

1. **Check logs:** `tail -f logs/agent_5_orchestrator.log`
2. **View reports:** `cat logs/agent_5_report_*.json | python3 -m json.tool`
3. **Test integrations:** Run health check script
4. **Review configuration:** `cat config/agent_5_config.json | python3 -m json.tool`

---

**Agent 5.0 on Agent Forge Replit**
*Cloud-Hosted Enterprise Automation*
*Updated: December 21, 2025*
