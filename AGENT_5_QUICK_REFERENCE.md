# Agent 5.0 - Quick Reference Guide

## Quick Start (5 Minutes)

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Configure secrets
cp config/.env.template config/.env
# Edit config/.env with your API keys

# 3. Run orchestrator
python3 scripts/agent_5_orchestrator.py

# 4. View results
cat logs/agent_5_report_*.json | python3 -m json.tool
```

## Key Files

| File | Purpose |
|------|---------|
| `config/agent_5_config.json` | Master configuration (all pillars, integrations) |
| `scripts/agent_5_orchestrator.py` | Main orchestrator (10x loop execution) |
| `docs/AGENT_5_DEPLOYMENT_GUIDE.md` | Complete setup & deployment instructions |
| `docs/AGENT_FORGE_REPLIT_INTEGRATION.md` | Cloud deployment guide |
| `logs/agent_5_orchestrator.log` | Real-time execution logs |
| `logs/agent_5_report_*.json` | Execution reports (JSON format) |

## Command Reference

### Execute Agent 5.0

```bash
# Standard execution (10x loop)
python3 scripts/agent_5_orchestrator.py

# With debug logging
PYTHONUNBUFFERED=1 python3 scripts/agent_5_orchestrator.py 2>&1 | tee logs/debug.log

# Dry-run mode (simulations only)
DRY_RUN=1 python3 scripts/agent_5_orchestrator.py

# Custom iterations
# (Edit config/agent_5_config.json: "max_iterations": 20)
```

### Monitor Execution

```bash
# Real-time logs
tail -f logs/agent_5_orchestrator.log

# Watch for errors
tail -f logs/agent_5_orchestrator.log | grep -i "error\|fail"

# Latest report (formatted)
python3 -c "import json; print(json.dumps(json.load(open(sorted(list(__import__('glob').glob('logs/agent_5_report_*.json')))[-1], 'r')), indent=2))" | tail -100
```

### Verify Configuration

```bash
# Check JSON validity
python3 -m json.tool config/agent_5_config.json > /dev/null && echo "✓ Valid JSON"

# Check Agent 5.0 version
python3 -c "import json; print(json.load(open('config/agent_5_config.json'))['system_metadata']['version'])"

# Check enabled pillars
python3 << 'EOF'
import json
c = json.load(open('config/agent_5_config.json'))
for k, v in c.items():
    if k.startswith('pillar_'):
        print(f"{k}: {'ENABLED' if v.get('enabled') else 'DISABLED'}")
EOF

# Verify all integrations
python3 << 'EOF'
import json
c = json.load(open('config/agent_5_config.json'))
for integration in ['e2b_integration', 'github_integration', 'zapier_integration', 'slack_integration']:
    status = "ON" if c[integration]['enabled'] else "OFF"
    print(f"{integration}: {status}")
EOF
```

## Environment Variables Required

```bash
# E2B
E2B_API_KEY=

# GitHub
GITHUB_TOKEN=

# Zapier
ZAPIER_MCP_BEARER_TOKEN=
ZAPIER_MCP_ENDPOINT=

# Slack
SLACK_BOT_TOKEN=
SLACK_WEBHOOK_URL=

# Microsoft 365
MICROSOFT_CLIENT_ID=
MICROSOFT_CLIENT_SECRET=
MICROSOFT_TENANT_ID=

# Trading
KRAKEN_API_KEY=
KRAKEN_SECRET_KEY=

# Federal
SAM_GOV_API_KEY=
```

## Configuration Sections

### Loop Control (10x Execution)
```json
{
  "loop_control": {
    "max_iterations": 10,
    "checkpoint_interval": 2,
    "iteration_delay_seconds": 2
  }
}
```

### Trading (Pillar A)
```json
{
  "pillar_a_trading": {
    "exchanges": {
      "kraken": {"enabled": true},
      "metatrader5": {"enabled": true}
    }
  }
}
```

### Legal (Pillar B)
```json
{
  "pillar_b_legal": {
    "document_types": ["contracts", "litigation"],
    "forensic_analysis": {"enabled": true}
  }
}
```

### Federal (Pillar C)
```json
{
  "pillar_c_federal": {
    "sam_gov": {"enabled": true},
    "opportunity_monitoring": {"enabled": true}
  }
}
```

### Nonprofit (Pillar D)
```json
{
  "pillar_d_nonprofit": {
    "form_processing": {
      "form_1023": {"enabled": true},
      "form_1023_ez": {"enabled": true}
    },
    "grant_intelligence": {"enabled": true}
  }
}
```

## Replit Deployment (Quick)

```bash
# 1. Go to https://72f0ad6a-efdf-4560-b50f-596680549d29-00-auxmaxx8t7os.kirk.replit.dev/
# 2. Sign in: appsefilepro@gmail.com
# 3. In terminal:

cd Private-Claude
git checkout claude/setup-e2b-webhooks-CPFBo

# 4. Set Secrets (Shield icon in left sidebar)
# 5. Run: python3 scripts/agent_5_orchestrator.py
```

## Troubleshooting

### E2B Issues
```bash
# Check E2B configuration
grep -A 10 "e2b_integration" config/agent_5_config.json

# Verify API key
echo $E2B_API_KEY
```

### GitHub Sync Issues
```bash
# Check GitHub remote
git remote -v

# Verify token
echo $GITHUB_TOKEN

# Check current branch
git branch -a
```

### Zapier Integration Issues
```bash
# Check Zapier config
grep -A 5 "zapier_integration" config/agent_5_config.json

# Verify endpoint
echo $ZAPIER_MCP_ENDPOINT
```

### Slack Notification Issues
```bash
# Check Slack config
grep -A 10 "slack_integration" config/agent_5_config.json

# Test webhook
curl -X POST $SLACK_WEBHOOK_URL \
  -H 'Content-type: application/json' \
  --data '{"text":"Test message"}'
```

## Logs & Reports

### Log Locations
```
logs/agent_5_orchestrator.log    - Main execution log
logs/agent_5_report_*.json       - JSON execution reports
logs/activation_*.json            - System activation logs
logs/data_ingestion_*.log         - Data processing logs
logs/legal_operations_*.log       - Legal operations log
logs/federal_operations_*.log     - Federal operations log
logs/nonprofit_operations_*.log   - Nonprofit operations log
logs/monitoring_*.log             - System monitoring log
```

### Parse Latest Report
```bash
# Pretty-print latest report
python3 -m json.tool logs/agent_5_report_*.json | head -50

# Count iterations
python3 -c "import json; r = json.load(open(sorted(list(__import__('glob').glob('logs/agent_5_report_*.json')))[-1])); print(f'Iterations: {r[\"execution_summary\"][\"successful_iterations\"]}')"

# Check errors
python3 -c "import json; r = json.load(open(sorted(list(__import__('glob').glob('logs/agent_5_report_*.json')))[-1])); print(f'Errors: {len(r[\"metrics\"][\"errors\"])}')"
```

## Performance Metrics

After execution, view:
- **Total Duration:** `metrics.duration_seconds`
- **Iterations Completed:** `metrics.iterations_completed`
- **Data Processed:** Sum of `pillar_results.*.data_processed`
- **Checkpoints:** `metrics.checkpoints_passed`
- **Integrations:** E2B, GitHub, Zapier, Slack calls

## Data Efficiency Features

1. **Compression:** Gzip for payloads > 1KB
2. **Batching:** Process 100 items per batch
3. **Caching:** 3600s TTL on results
4. **Connection Pooling:** 20 connection pool
5. **Async Execution:** 10 concurrent tasks

## API Endpoints

```
Kraken:         https://api.kraken.com
E2B:            https://api.e2b.dev/v1
GitHub:         https://api.github.com
Zapier:         https://hooks.zapier.com
SharePoint:     https://graph.microsoft.com/v1.0/sites
SAM.gov:        https://api.sam.gov/prod/opportunities/v2/search
Slack:          https://slack.com/api
```

## Slack Channels

- `#trading-alerts` - Trading signals
- `#legal-operations` - Legal documents
- `#federal-contracting` - SAM.gov opportunities
- `#nonprofit-automation` - Grant discoveries
- `#agent-5-execution` - Execution status
- `#errors-and-alerts` - Critical errors

## Support

| Issue | Solution |
|-------|----------|
| Module not found | `pip install -r requirements.txt` |
| Config invalid | `python3 -m json.tool config/agent_5_config.json` |
| Secrets missing | Update `config/.env` with API keys |
| Git sync failed | Run `git status` and `git config --list` |
| E2B execution error | Check `E2B_API_KEY` environment variable |
| Slack notifications fail | Verify `SLACK_BOT_TOKEN` and `SLACK_WEBHOOK_URL` |

## Next Steps

1. **Configure:** Update `config/.env` with your credentials
2. **Execute:** Run `python3 scripts/agent_5_orchestrator.py`
3. **Monitor:** Watch `logs/agent_5_orchestrator.log`
4. **Review:** Check `logs/agent_5_report_*.json` for results
5. **Deploy:** Use Replit guide for cloud deployment

---

**Agent 5.0** - Enterprise Automation at Scale
*v5.0.0 | December 21, 2025*
