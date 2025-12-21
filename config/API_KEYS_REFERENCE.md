# API Keys Reference & Setup Guide

## E2B Webhook Configuration
**Webhook ID:** `YIyOpaJ0UMJ3Pl9Md5kVExEDdkqyDGRp`

### Current API Keys (from screenshots)

#### E2B API Key
```
e2b_fcc08e8c733b3eab00bdb3ad5857f5966afc2773
```

#### Google Gemini API Key
```
AIzaSyBqAbzJdyg7sP5tIhCddWk4Q1EEmSZSCT4
```
- **Name:** Default Gemini API Key
- **Project:** projects/190831837188
- **Project Number:** 190831837188

### Setup Instructions

#### 1. Configure Environment Variables

Create `.env` file from template:
```bash
cp config/.env.template .env
```

Add your keys to `.env`:
```bash
# E2B Configuration
E2B_API_KEY=e2b_fcc08e8c733b3eab00bdb3ad5857f5966afc2773
E2B_WEBHOOK_SECRET=YIyOpaJ0UMJ3Pl9Md5kVExEDdkqyDGRp
E2B_WEBHOOK_URL=https://your-domain.com/webhooks/e2b

# Google Gemini
GEMINI_API_KEY=AIzaSyBqAbzJdyg7sP5tIhCddWk4Q1EEmSZSCT4
GEMINI_PROJECT_NAME=projects/190831837188
GEMINI_PROJECT_NUMBER=190831837188
```

#### 2. Configure Webhooks

**E2B Webhook Endpoint:**
```
POST /api/webhooks/e2b
```

**Events Subscribed:**
- `sandbox.created`
- `sandbox.started`
- `execution.completed`
- `file.uploaded`

#### 3. Zapier Integration

**Setup Steps:**
1. Go to https://zapier.com/app/zaps
2. Create new Zap
3. Choose "Webhooks by Zapier" as trigger
4. Use webhook URL from Zapier
5. Add webhook URL to `.env`:
   ```
   ZAPIER_WEBHOOK_URL=https://hooks.zapier.com/hooks/catch/YOUR_ID/
   ```

**Recommended Zaps:**
- E2B Execution → Google Sheets (log results)
- E2B File Upload → Google Drive (backup files)
- E2B Event → Slack/Teams (notifications)

#### 4. GitHub Integration

**Repository:** Private-Claude
**Branch:** claude/setup-e2b-webhooks-CPFBo

**Webhook URL:**
```
https://api.github.com/repos/YOUR_USERNAME/Private-Claude/hooks
```

**Events:**
- Push events
- Pull request events
- Workflow run events

#### 5. Test Webhook Handler

Run the Python handler:
```bash
python3 scripts/e2b_webhook_handler.py
```

### Data Optimization Features

✅ **Compression enabled** - Reduces payload size by 60-80%
✅ **Minimal mode** - Sends only essential fields
✅ **Batch processing** - Groups multiple events
✅ **Size limits** - Max 100KB per payload

### Security Features

🔒 **Signature verification** - HMAC-SHA256
🔒 **Encryption** - AES-256-GCM
🔒 **Rate limiting** - 60 req/min
🔒 **IP filtering** - Optional whitelist

### Sync Targets

- **Zapier**: ✅ Enabled (automation workflows)
- **GitHub**: ✅ Enabled (code sync)
- **Google Cloud**: ✅ Enabled (storage & pubsub)
- **Copilot**: ✅ Enabled (context sharing)

### Copilot Integration

The webhook handler integrates with GitHub Copilot:
- Shares execution context
- Syncs code results
- Enables AI-assisted debugging

### Quick Commands

**Start webhook server:**
```bash
python3 scripts/e2b_webhook_handler.py
```

**Test webhook:**
```bash
curl -X POST http://localhost:5000/webhooks/e2b \
  -H "Content-Type: application/json" \
  -d '{"event":"execution.completed","status":"success"}'
```

**View logs:**
```bash
tail -f logs/e2b_webhook.log
```

### Configuration Files

- `config/e2b_webhook_config.json` - Main webhook configuration
- `config/zapier_connector.json` - Zapier integration settings
- `config/github_webhook_integration.json` - GitHub automation
- `scripts/e2b_webhook_handler.py` - Python webhook handler

### Support & Resources

- E2B Docs: https://e2b.dev/docs
- Zapier Help: https://help.zapier.com
- GitHub Webhooks: https://docs.github.com/webhooks

---

**Last Updated:** 2025-12-21
**Webhook ID:** YIyOpaJ0UMJ3Pl9Md5kVExEDdkqyDGRp
