# Integration Quick Reference

## Webhook Setup Checklist

### Zapier Setup
- [ ] Create Zapier account
- [ ] Create 5 Zaps using the templates in `zapier_workflows.json`
- [ ] Copy webhook URLs to `.env` as `ZAPIER_WEBHOOK_URL`
- [ ] Test each Zap with sample data
- [ ] Enable all Zaps

### Slack Setup
- [ ] Create Slack workspace (or use existing)
- [ ] Create 7 incoming webhooks (one per channel)
- [ ] Copy all webhook URLs to `.env`:
  ```
  SLACK_WEBHOOK_GENERAL=https://hooks.slack.com/services/...
  SLACK_WEBHOOK_E2B=https://hooks.slack.com/services/...
  SLACK_WEBHOOK_TRADING=https://hooks.slack.com/services/...
  SLACK_WEBHOOK_ERRORS=https://hooks.slack.com/services/...
  SLACK_WEBHOOK_GITHUB=https://hooks.slack.com/services/...
  SLACK_WEBHOOK_HEALTH=https://hooks.slack.com/services/...
  SLACK_WEBHOOK_ZAPIER=https://hooks.slack.com/services/...
  ```

### GitHub Enterprise Setup
- [ ] Enable GitHub Enterprise 30-day trial
- [ ] Enable Secret Scanning
- [ ] Enable Code Scanning (CodeQL)
- [ ] Enable Dependabot
- [ ] Create GitHub Personal Access Token
- [ ] Add to `.env` as `GITHUB_TOKEN`
- [ ] Configure branch protection for main branch
- [ ] Set up 5 Copilot Business seats

### E2B Integration
- [ ] Get E2B API key
- [ ] Create E2B webhook
- [ ] Add to `.env`:
  ```
  E2B_API_KEY=your_key
  E2B_WEBHOOK_SECRET=your_secret
  E2B_WEBHOOK_URL=your_endpoint
  ```

## Environment Variables Template

```bash
# E2B Configuration
E2B_API_KEY="sk_prod_..."
E2B_WEBHOOK_SECRET="whsec_..."
E2B_WEBHOOK_URL="https://your-domain.com/webhooks/e2b"

# Zapier Configuration
ZAPIER_WEBHOOK_URL="https://hooks.zapier.com/hooks/catch/.../..."

# Slack Webhooks
SLACK_WEBHOOK_GENERAL="https://hooks.slack.com/services/T.../B.../..."
SLACK_WEBHOOK_E2B="https://hooks.slack.com/services/T.../B.../..."
SLACK_WEBHOOK_TRADING="https://hooks.slack.com/services/T.../B.../..."
SLACK_WEBHOOK_ERRORS="https://hooks.slack.com/services/T.../B.../..."
SLACK_WEBHOOK_GITHUB="https://hooks.slack.com/services/T.../B.../..."
SLACK_WEBHOOK_HEALTH="https://hooks.slack.com/services/T.../B.../..."
SLACK_WEBHOOK_ZAPIER="https://hooks.slack.com/services/T.../B.../..."

# GitHub Configuration
GITHUB_TOKEN="ghp_..."
GH_ENTERPRISE_BILLING_EMAIL="billing@example.com"
GH_ADMIN_USER="github_username"

# Google/Gemini
GEMINI_API_KEY="AIzaSy..."
GEMINI_PROJECT_NUMBER="123456789"

# SharePoint (optional, for Form 1023 generation)
SHAREPOINT_SITE="https://company.sharepoint.com/sites/Private-Claude"

# Alert Email List (comma-separated)
ALERT_EMAIL_LIST="team@example.com,devops@example.com"

# Trading API (if using trading signals)
TRADING_API_KEY="your_trading_api_key"
TRADING_WEBHOOK_URL="https://your-trading-api.com/webhooks"

# Forms
FORM_1023_ID="your_google_form_id"
```

## Zap Templates Quick Deploy

### Zap 1: E2B Execution to Google Sheets
```
Trigger: E2B Webhook (execution.completed)
Action 1: Add row to Google Sheets
  - Spreadsheet: "E2B Execution Logs"
  - Columns: Execution ID, Status, Output, Timestamp, Sandbox ID
Action 2 (Optional): Send Slack if failed
  - Condition: Status = "failed"
  - Channel: #e2b-alerts
```

### Zap 2: GitHub Push to E2B Test
```
Trigger: GitHub (new commit on main/develop)
Action 1: Execute code in E2B
  - Code: pytest --tb=short -v
  - Language: Python
  - Timeout: 60s
Action 2 (Optional): Create GitHub issue if failed
  - Condition: Exit code != 0
```

### Zap 3: Trading Signals to Slack
```
Trigger: Trading API (signal generated)
Action 1: Send Slack message
  - Channel: #trading-signals
  - Format: "BUY/SELL {{asset}} at {{price}}"
Action 2: Add row to Google Sheets
  - Spreadsheet: "Trading Signals"
  - Log: Timestamp, Signal, Asset, Confidence
```

### Zap 4: Form 1023 to SharePoint
```
Trigger: Google Forms (form submission)
Action 1: Execute code in E2B
  - Generate PDF from form data
Action 2: Upload to SharePoint
  - Site: Private-Claude
  - Library: Form Archive
  - Folder: Monthly
Action 3: Send confirmation email
```

### Zap 5: Error Alerts to Email/Slack
```
Trigger: Error API (threshold exceeded)
Action 1: Send Slack message (if critical)
  - Channel: #error-alerts
  - Mention: @devops
Action 2: Send email
  - To: Alert list
  - Subject: [CRITICAL] Error type in service
Action 3: Log to Google Sheets
  - Spreadsheet: "Error Logs"
```

## Testing Commands

### Test Webhook Delivery
```bash
# Test Slack webhook
curl -X POST $SLACK_WEBHOOK_GENERAL \
  -H 'Content-Type: application/json' \
  -d '{"text": "Test message from integration", "blocks": [{"type": "section", "text": {"type": "mrkdwn", "text": "*Test*"}}]}'

# Test Zapier webhook
curl -X POST $ZAPIER_WEBHOOK_URL \
  -H 'Content-Type: application/json' \
  -d '{"event_type": "test", "status": "success"}'

# Test E2B webhook
curl -X POST $E2B_WEBHOOK_URL \
  -H 'Content-Type: application/json' \
  -H "X-E2B-Signature: $(echo -n '{}' | openssl dgst -sha256 -hmac $E2B_WEBHOOK_SECRET | cut -d' ' -f2)" \
  -d '{"event": "execution.completed", "status": "success"}'
```

### Test Python Script
```bash
# Run integration sync test
python3 scripts/integration_sync.py

# Test with verbose logging
python3 -u scripts/integration_sync.py 2>&1 | tee /tmp/sync.log

# Check configuration validity
for file in config/integrations/*.json; do
  python3 -m json.tool "$file" > /dev/null && echo "✓ $(basename $file)"
done
```

## Monitoring Commands

### View Integration Logs
```bash
# Real-time logs
tail -f /var/log/integration-sync.log

# Filter by level
grep "ERROR" /var/log/integration-sync.log
grep "WARNING" /var/log/integration-sync.log

# Count events by type
grep "event_type" /var/log/integration-sync.log | cut -d'"' -f4 | sort | uniq -c
```

### Check Webhook Status
```bash
# Verify webhook URLs are accessible
for url in $SLACK_WEBHOOK_GENERAL $ZAPIER_WEBHOOK_URL $E2B_WEBHOOK_URL; do
  echo "Testing: $url"
  curl -I "$url" 2>/dev/null | head -1
done
```

### Monitor Data Usage
```bash
# Check file sizes
du -sh config/integrations/*

# Monitor sync script memory
ps aux | grep integration_sync

# Check network traffic
iftop -i eth0 -n
```

## Configuration Validation

### Validate JSON Files
```bash
python3 -m json.tool config/integrations/zapier_workflows.json > /dev/null && echo "✓ Valid"
python3 -m json.tool config/integrations/slack_config.json > /dev/null && echo "✓ Valid"
python3 -m json.tool config/integrations/github_enterprise.json > /dev/null && echo "✓ Valid"
```

### Check Python Syntax
```bash
python3 -m py_compile scripts/integration_sync.py && echo "✓ Valid"
```

### Verify Environment
```bash
# Check all required variables are set
required_vars=(
  "E2B_API_KEY"
  "ZAPIER_WEBHOOK_URL"
  "SLACK_WEBHOOK_GENERAL"
  "GITHUB_TOKEN"
)

for var in "${required_vars[@]}"; do
  if [ -z "${!var}" ]; then
    echo "✗ Missing: $var"
  else
    echo "✓ Set: $var"
  fi
done
```

## Performance Tuning

### Optimize Data Usage
```python
# In integration_sync.py
DATA_OPTIMIZATION_ENABLED = True  # Enable compression
BATCH_SIZE_LIMIT = 10  # Max events per batch
BATCH_TIMEOUT_SECONDS = 60  # Wait time before flushing
MAX_RETRIES = 3  # Retry failed events
```

### Adjust Rate Limiting
```json
{
  "rate_limiting": {
    "messages_per_minute": 60,  # Slack limit
    "messages_per_hour": 1000,   # Slack limit
    "burst_limit": 10             # Max burst
  }
}
```

### Configure Webhooks
```json
{
  "webhook_configuration": {
    "timeout_seconds": 30,
    "retry_policy": {
      "max_retries": 3,
      "backoff_multiplier": 2
    }
  }
}
```

## Troubleshooting Guide

| Issue | Cause | Solution |
|-------|-------|----------|
| Webhook not delivering | Invalid URL | Verify webhook URL is correct |
| Rate limit exceeded | Too many events | Increase batch size or timeout |
| Retries failing | Service down | Check service status, wait for retry |
| High latency | Network issue | Check network connectivity |
| Memory leak | Event queue growing | Monitor queue size, flush batches |
| Data truncation | Fields too long | Enable field truncation in config |

## Daily Operations

### Morning Check
```bash
# 1. Verify all services are up
curl -s $E2B_WEBHOOK_URL -I | grep -q "200\|405" && echo "✓ E2B"
curl -s $ZAPIER_WEBHOOK_URL -I | grep -q "200\|405" && echo "✓ Zapier"

# 2. Check error logs
grep ERROR /var/log/integration-sync.log | tail -10

# 3. Verify metrics
python3 -c "from scripts.integration_sync import sync_manager; import json; print(json.dumps(sync_manager.get_metrics(), indent=2))"
```

### Weekly Maintenance
```bash
# 1. Rotate logs
logrotate /etc/logrotate.d/integration-sync

# 2. Archive old webhook data
find /var/log -name "*.log" -mtime +7 -exec gzip {} \;

# 3. Review failed events
grep "retry_count.*3" /var/log/integration-sync.log > /tmp/failed-events.txt
```

### Monthly Review
```bash
# 1. Check data usage
du -sh config/integrations/
du -sh /var/log/integration-sync*

# 2. Review GitHub Enterprise trial status
# 3. Validate all webhook URLs are still active
# 4. Check Zapier task usage
# 5. Review Slack message statistics
```

---

**Quick Start**: Copy `.env` template, fill in webhook URLs, run `python3 scripts/integration_sync.py`

**Version**: 2.0.0
