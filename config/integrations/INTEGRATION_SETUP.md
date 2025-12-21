# Integration Configuration Setup Guide

## Overview

This directory contains comprehensive integration configurations for connecting Zapier, Slack, GitHub Enterprise, and other automation services to the Private-Claude platform.

**Key Features:**
- ✅ Minimal data usage optimized for free tier
- ✅ Advanced security and encryption
- ✅ Webhook routing and intelligent batching
- ✅ Automatic retry logic with exponential backoff
- ✅ Complete GitHub Enterprise 30-day trial setup
- ✅ Copilot Business integration with seat management

## Files Overview

### 1. `zapier_workflows.json`
**Purpose:** Define Zap workflows for automation between services

**Key Workflows:**
- **E2B Execution → Google Sheets**: Log all E2B code executions and outputs
- **GitHub Push → E2B Test**: Trigger tests on every push to main/develop
- **Trading Signals → Slack**: Real-time notifications for buy/sell signals
- **Form 1023 → SharePoint**: Auto-generate and upload legal documents
- **Error Alerts → Email/Slack**: Route critical errors to team

**Configuration Details:**
```json
{
  "triggers": ["execution.completed", "new_commit"],
  "actions": ["Add row to Google Sheets", "Send Slack message"],
  "retry_policy": {
    "max_retries": 3,
    "backoff_multiplier": 2
  }
}
```

**Free Tier Optimizations:**
- Maximum 5 Zaps allowed
- 100 tasks per month
- Batching enabled for high-volume events
- Field truncation (512 chars max)
- Automatic deduplication

### 2. `slack_config.json`
**Purpose:** Configure Slack webhooks, notification templates, and routing rules

**Webhook Channels:**
- `#general`: General announcements
- `#e2b-alerts`: E2B execution status (HIGH priority)
- `#trading-signals`: Real-time trading alerts (HIGH priority)
- `#error-alerts`: Critical system errors (CRITICAL priority)
- `#github-updates`: GitHub events (MEDIUM priority)
- `#zapier-logs`: Zapier workflow status (LOW priority)
- `#system-health`: System metrics and uptime

**Alert Routing Rules:**
| Condition | Target Channel | Mention | Enabled |
|-----------|---|---|---|
| E2B Error | #e2b-alerts | N/A | Yes |
| Critical Error | #error-alerts | @devops | Yes |
| Trading Signal | #trading-signals | N/A | Yes |
| GitHub Push/PR | #github-updates | N/A | Yes |

**Message Templates:**
- E2B Execution Success/Failure
- Trading Signals (Buy/Sell)
- System Health Status
- GitHub Events
- Error Alerts

### 3. `github_enterprise.json`
**Purpose:** Configure GitHub Enterprise 30-day trial with advanced security

**Trial Configuration:**
- **Duration**: 30 days from activation
- **Auto-downgrade**: Drops to Pro plan after trial ends
- **Monthly cost**: $231 (5 Copilot seats @ $39 each)

**Advanced Security Features:**
```
✓ Secret Scanning with custom patterns
  - API keys, AWS credentials, private keys, database passwords
✓ Code Scanning (CodeQL)
  - Python security and quality analysis
✓ Branch Protection
  - Require code reviews, status checks
  - Dismiss stale reviews on push
✓ Dependabot
  - Automated vulnerability alerts
  - Auto-update pull requests
✓ Audit Logging (90-day retention)
✓ SAML SSO Configuration
```

**Copilot Business:**
- 5 total seats
- 1 currently assigned
- 4 seats available
- Features: Code completion, chat, code review, documentation
- Excludes from AI training

**GitHub Actions:**
- 3,000 minutes/month included
- Rate limiting: 100/min, 1000/hour
- Cost optimization: scheduled maintenance, dependency caching

### 4. `integration_sync.py`
**Purpose:** Python script for syncing data between all services

**Main Components:**

#### DataCompressor
- Gzip compression for payloads
- Automatic field truncation
- Compression ratio calculation
- Free tier data optimization

#### WebhookRouter
- Event-based routing to appropriate channels
- Conditional routing (severity, source, type)
- Fallback to default channel

#### BatchManager
- Groups similar events
- Configurable batch size (10 events max)
- Timeout-based flushing (60 seconds)
- Thread-safe batch handling

#### RetryManager
- Exponential backoff (base delay: 1s, multiplier: 2x)
- Max retries: 3 attempts
- Maximum delay: 60 seconds
- Automatic queue processing

#### WebhookSender
- HTTP POST with timeout (10s)
- Automatic compression
- Error handling and logging
- Request retry capability

#### IntegrationSyncManager
- Event creation helpers
- Metric tracking
- Queue management
- Central orchestration

**Event Types:**
- `e2b.execution.success/failure`
- `github.push/pull_request`
- `trading.signal.buy/sell`
- `error.alert`
- `slack.message`
- `zapier.event`

## Setup Instructions

### Step 1: Environment Variables

Create or update `.env` with:

```bash
# E2B Configuration
E2B_API_KEY="your_e2b_api_key"
E2B_WEBHOOK_SECRET="your_e2b_webhook_secret"
E2B_WEBHOOK_URL="https://your-domain/webhooks/e2b"

# Zapier Configuration
ZAPIER_WEBHOOK_URL="https://hooks.zapier.com/hooks/catch/xxxxx/xxxxx"

# Slack Webhooks
SLACK_WEBHOOK_GENERAL="https://hooks.slack.com/services/T.../B.../..."
SLACK_WEBHOOK_E2B="https://hooks.slack.com/services/T.../B.../..."
SLACK_WEBHOOK_TRADING="https://hooks.slack.com/services/T.../B.../..."
SLACK_WEBHOOK_ERRORS="https://hooks.slack.com/services/T.../B.../..."

# GitHub Configuration
GITHUB_TOKEN="ghp_your_personal_access_token"
GH_ENTERPRISE_BILLING_EMAIL="billing@example.com"
GH_ADMIN_USER="your_github_username"

# Gemini/Google
GEMINI_API_KEY="your_gemini_api_key"
GEMINI_PROJECT_NUMBER="your_project_number"
```

### Step 2: Create Zapier Zaps

1. **Log into Zapier Dashboard**
2. **Create Each Zap:**
   - E2B → Google Sheets (Execute this first)
   - GitHub → E2B Tests
   - Trading Signals → Slack
   - Form 1023 → SharePoint
   - Error Alerts → Email/Slack

3. **Copy webhook URLs to .env:**
   ```bash
   ZAPIER_WEBHOOK_URL="https://hooks.zapier.com/hooks/catch/YOUR_KEY"
   ```

### Step 3: Set Up Slack Webhooks

1. **Create Incoming Webhooks:**
   - Go to Slack workspace admin
   - Apps → Custom Integrations → Incoming Webhooks
   - Create webhook for each channel (#general, #e2b-alerts, etc.)

2. **Copy URLs to .env:**
   ```bash
   SLACK_WEBHOOK_GENERAL="https://hooks.slack.com/services/..."
   SLACK_WEBHOOK_E2B="https://hooks.slack.com/services/..."
   ```

### Step 4: Configure GitHub Enterprise

1. **Enable 30-Day Trial:**
   - Go to GitHub Settings → Billing and plans
   - Select "Enterprise Cloud"
   - Start trial

2. **Enable Advanced Security:**
   - Go to Repository Settings → Code security
   - Enable "Secret scanning"
   - Enable "Code scanning"
   - Enable "Dependabot alerts"

3. **Set Up Copilot Business:**
   - Organization Settings → Copilot
   - Enable "Copilot Business"
   - Assign seats to team members

4. **Configure Branch Protection:**
   - Repository Settings → Branches
   - Add rule for "main" branch
   - Require reviews, status checks

### Step 5: Run Integration Sync

```bash
# Test the integration sync script
python3 /home/user/Private-Claude/scripts/integration_sync.py

# Set up as systemd service (optional)
# Create /etc/systemd/system/integration-sync.service
[Unit]
Description=Integration Sync Manager
After=network.target

[Service]
Type=simple
User=www-data
ExecStart=/usr/bin/python3 /home/user/Private-Claude/scripts/integration_sync.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## Usage Examples

### Create and Process E2B Event

```python
from scripts.integration_sync import sync_manager

event = sync_manager.create_e2b_event(
    status='success',
    execution_id='exec-abc123',
    output='Code executed successfully'
)
sync_manager.process_event(event)
```

### Send Trading Signal

```python
event = sync_manager.create_trading_event(
    signal_type='buy',
    asset='AAPL',
    confidence=85.5,
    entry_price=150.25,
    stop_loss=145.00,
    take_profit=160.00
)
sync_manager.process_event(event)
```

### Create Error Alert

```python
event = sync_manager.create_error_event(
    error_type='DatabaseError',
    service='user-service',
    severity='critical',
    error_count=3,
    stack_trace='Connection failed at line 42'
)
sync_manager.process_event(event)
```

## Data Optimization Strategies

### 1. Field Truncation
- Text fields: 512 characters max
- Output fields: 256 characters max
- Stack traces: 1,000 characters max

### 2. Compression
- Payload compression: Gzip (level 6)
- Compression savings: ~60-70% for typical events

### 3. Batching
- Batch size: 10 events max
- Batch timeout: 60 seconds
- Deduplication: 15-minute window

### 4. Free Tier Limits
- Zapier: 5 Zaps, 100 tasks/month
- Slack: Unlimited webhooks, rate limited to 1 msg/sec
- GitHub: 3,000 Actions minutes/month
- Data: Minimal payload optimization

## Monitoring and Metrics

### Available Metrics

```python
metrics = sync_manager.get_metrics()
# Returns:
{
    'events_processed': 42,
    'events_failed': 2,
    'batches_sent': 5,
    'total_data_compressed': 125000,
    'compression_ratio_avg': 65.5
}
```

### Log Monitoring

```bash
# Watch integration sync logs
tail -f /var/log/integration-sync.log

# Filter for errors
grep ERROR /var/log/integration-sync.log
```

## Troubleshooting

### Issue: Webhook not delivering
1. Check webhook URL in .env is correct
2. Verify endpoint is accessible
3. Check rate limiting (max 10 msg/sec for Slack)
4. Review logs for timeout errors

### Issue: Events not batching
1. Verify batch_size setting (should be 10)
2. Check event batch_key is set correctly
3. Monitor batch timeout (60 seconds)

### Issue: Retries failing
1. Check retry count (max 3 attempts)
2. Verify exponential backoff delay
3. Review network connectivity
4. Check endpoint availability

### Issue: High data usage
1. Verify compression is enabled
2. Check field truncation settings
3. Review batching configuration
4. Monitor payload sizes

## Free Tier Best Practices

1. **Zapier**:
   - Use 5 Zaps strategically
   - Batch similar operations
   - Avoid per-item operations

2. **Slack**:
   - Batch notifications
   - Limit thread replies
   - Use summarization

3. **GitHub Actions**:
   - Use matrix strategy efficiently
   - Cache dependencies
   - Schedule tests off-peak

4. **Data Compression**:
   - Always enable gzip
   - Truncate long fields
   - Remove unnecessary data

## Next Steps

1. Complete environment variable setup
2. Create Zapier Zaps (use JSON as template)
3. Configure Slack webhooks
4. Activate GitHub Enterprise trial
5. Run integration_sync.py test
6. Monitor logs for successful delivery
7. Set up systemd service for continuous operation

## Support

For issues or questions:
- Check logs: `tail -f /var/log/integration-sync.log`
- Verify configuration: `python3 -m json.tool config/integrations/*.json`
- Test connectivity: `curl -X POST <WEBHOOK_URL> -d '{"test": true}'`

## Security Considerations

- Keep all webhook URLs in .env (never commit)
- Use strong GitHub Personal Access Tokens
- Enable SAML SSO for GitHub Enterprise
- Rotate API keys quarterly
- Audit webhook deliveries monthly
- Review access logs for anomalies

---

**Version**: 2.0.0
**Last Updated**: 2025-12-21
**Maintained By**: Private-Claude Team
