# Zapier Workflows - Quick Reference

**Account:** terobinsonwy@gmail.com | **Plan:** Free (100 tasks/month) | **Active Workflows:** 8

---

## Webhook URLs

### Email & Tasks
```
zap_001 - Gmail to Task Extraction
https://hooks.zapier.com/hooks/catch/zap_001/gmail-to-task-extraction/

zap_002 - Email to Document Generator
https://hooks.zapier.com/hooks/catch/zap_002/email-to-document-generator/

zap_006 - Task Reminder System
https://hooks.zapier.com/hooks/catch/zap_006/task-reminder-system/
```

### Document Processing
```
zap_003 - Form 1023 Auto-Generator
https://hooks.zapier.com/hooks/catch/zap_003/form-1023-auto-generator/

zap_004 - Legal Document Automation
https://hooks.zapier.com/hooks/catch/zap_004/legal-document-automation/
```

### Trading & Testing
```
zap_005 - Trading Alert to Action
https://hooks.zapier.com/hooks/catch/zap_005/trading-alert-to-action/

zap_007 - E2B Execution to Postman Test
https://hooks.zapier.com/hooks/catch/zap_007/e2b-execution-to-postman-test/
```

### Deployment
```
zap_008 - GitHub to Live Deployment
https://hooks.zapier.com/hooks/catch/zap_008/github-to-live-deployment/
```

---

## Quick Commands

### Activate All Workflows
```bash
cd /home/user/Private-Claude
python3 scripts/zapier_activator.py
```

### Test Workflows
```bash
python3 scripts/test_zapier_workflows.py
```

### Check Status
```bash
cat config/zapier_live_workflows.json
```

### View Activation Report
```bash
cat logs/zapier_activation_report.json | jq
```

### Check Usage
```bash
cat config/zapier_live_workflows.json | jq '.usage_tracking'
```

---

## Test Email Template

**To:** terobinsonwy@gmail.com
**Subject:** Test - Action Items for Agent 5.0

**Body:**
```
Hi,

Please complete the following tasks:
- Review Form 1023 for ABC Nonprofit
- Schedule meeting with legal team at 2pm tomorrow
- Prepare probate documents for Case #12345

Documents needed:
- Financial statements Q4 2024
- Board meeting minutes

Deadline: December 25, 2025

Thanks!
```

---

## Webhook Test with curl

### Test Email Extraction (zap_001)
```bash
curl -X POST https://hooks.zapier.com/hooks/catch/zap_001/gmail-to-task-extraction/ \
  -H "Content-Type: application/json" \
  -d '{
    "from": "test@example.com",
    "subject": "Test Email - Action Items",
    "body": "Review Form 1023 for ABC Nonprofit",
    "timestamp": "'$(date -Iseconds)'"
  }'
```

### Test Trading Signal (zap_005)
```bash
curl -X POST https://hooks.zapier.com/hooks/catch/zap_005/trading-alert-to-action/ \
  -H "Content-Type: application/json" \
  -d '{
    "signal_type": "BUY",
    "pair": "BTC/USD",
    "signal_strength": 0.85,
    "price": 95000,
    "pattern": "HAMMER",
    "timestamp": "'$(date -Iseconds)'"
  }'
```

### Test Legal Document (zap_004)
```bash
curl -X POST https://hooks.zapier.com/hooks/catch/zap_004/legal-document-automation/ \
  -H "Content-Type: application/json" \
  -d '{
    "document_type": "probate_petition",
    "case_number": 12345,
    "case_caption": "Estate of John Doe",
    "jurisdiction": "Wyoming",
    "timestamp": "'$(date -Iseconds)'"
  }'
```

---

## OAuth Setup URLs

| Service | URL |
|---------|-----|
| Gmail | https://zapier.com/apps/gmail/integrations |
| Google Tasks | https://zapier.com/apps/google-tasks/integrations |
| Google Calendar | https://zapier.com/apps/google-calendar/integrations |
| Google Sheets | https://zapier.com/apps/google-sheets/integrations |
| Google Drive | https://zapier.com/apps/google-drive/integrations |
| GitHub | https://zapier.com/apps/github/integrations |
| Slack | https://zapier.com/apps/slack/integrations |

---

## Workflow Status Check

### Via Zapier Dashboard
```
https://zapier.com/app/zaps
```

### Via Python
```python
import json

with open('config/zapier_live_workflows.json', 'r') as f:
    config = json.load(f)

for workflow in config['active_workflows']:
    print(f"{workflow['workflow_id']}: {workflow['workflow_name']} - {workflow['status']}")
```

---

## Common Issues & Solutions

### Issue: Workflow not triggering
**Solution:** Check OAuth authentication in Zapier dashboard

### Issue: Task limit reached
**Solution:** Wait for monthly reset or upgrade plan

### Issue: Webhook 404 error
**Solution:** Verify webhook URL is correct and endpoint is accessible

### Issue: No tasks created in Google Tasks
**Solution:** Verify "Agent 5.0 Tasks" list exists in Google Tasks

---

## Integration Endpoints

Add these to `/home/user/Private-Claude/config/.env`:

```bash
# Agent 5.0 Webhook
AGENT_5_WEBHOOK_URL=https://your-agent-5-webhook.com/api/process

# E2B Webhook
E2B_WEBHOOK_URL=https://your-e2b-webhook.com/api/execute

# Trading Bot API
TRADING_BOT_API=https://your-trading-bot.com/api
```

---

## Monitoring Commands

### Check Active Workflows
```bash
cat config/zapier_live_workflows.json | jq '.total_active'
```

### List All Webhook URLs
```bash
cat config/zapier_live_workflows.json | jq '.webhook_urls'
```

### View Last Test Results
```bash
cat logs/zapier_workflow_tests.json | jq '.summary'
```

### Check Task Usage
```bash
cat config/zapier_live_workflows.json | jq '.usage_tracking'
# Output: {"tasks_used": 0, "tasks_limit": 100, "workflows_active": 8}
```

---

## Support

**Documentation:** /home/user/Private-Claude/ZAPIER_ACTIVATION_SUMMARY.md
**Activation Script:** /home/user/Private-Claude/scripts/zapier_activator.py
**Test Script:** /home/user/Private-Claude/scripts/test_zapier_workflows.py

**For detailed information, see ZAPIER_ACTIVATION_SUMMARY.md**

---

Last Updated: 2025-12-22
