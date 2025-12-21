# E2B Webhook Integration - Complete Setup Guide

## 🎯 Overview

This guide covers the complete setup of E2B webhooks with GitHub, Zapier, Google Gemini AI, and other integrations for the Private-Claude repository.

**Webhook ID:** `YIyOpaJ0UMJ3Pl9Md5kVExEDdkqyDGRp`

## 📋 Prerequisites

- Python 3.8+
- Git
- Node.js (optional, for advanced features)
- Postman (for API testing)
- Administrator access (Windows) or sudo (Linux/Mac)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
cd Private-Claude
git checkout claude/setup-e2b-webhooks-CPFBo
```

### 2. Configure Environment

```bash
# Copy environment template
cp config/.env.template config/.env

# Edit with your API keys
nano config/.env  # or use your preferred editor
```

### 3. Run Setup Script

**Linux/Mac:**
```bash
python3 scripts/complete_integration_setup.py
```

**Windows (PowerShell as Administrator):**
```powershell
.\scripts\Setup-E2BIntegration.ps1
```

## 🔑 API Keys Configuration

### E2B API
```bash
E2B_API_KEY=e2b_fcc08e8c733b3eab00bdb3ad5857f5966afc2773
E2B_WEBHOOK_SECRET=YIyOpaJ0UMJ3Pl9Md5kVExEDdkqyDGRp
E2B_WEBHOOK_URL=https://your-domain.com/webhooks/e2b
```

### Google Gemini AI
```bash
GEMINI_API_KEY=AIzaSyBqAbzJdyg7sP5tIhCddWk4Q1EEmSZSCT4
GEMINI_PROJECT_NAME=projects/190831837188
GEMINI_PROJECT_NUMBER=190831837188
```

### Zapier
```bash
ZAPIER_WEBHOOK_URL=https://hooks.zapier.com/hooks/catch/YOUR_ID/
ZAPIER_MCP_BEARER_TOKEN=your_token_here
```

### GitHub
```bash
GITHUB_TOKEN=your_github_personal_access_token
```

## 📁 Project Structure

```
Private-Claude/
├── config/
│   ├── .env.template              # Environment variables template
│   ├── .env                       # Your actual keys (git-ignored)
│   ├── API_KEYS_REFERENCE.md      # API keys documentation
│   ├── e2b_webhook_config.json    # E2B webhook configuration
│   ├── zapier_connector.json      # Zapier integration settings
│   ├── github_webhook_integration.json  # GitHub automation
│   ├── mcp_server_config.json     # MCP server settings
│   └── postman_collection.json    # Postman API collection
├── scripts/
│   ├── e2b_webhook_handler.py     # Main webhook handler
│   ├── complete_integration_setup.py  # Automated setup
│   ├── Setup-E2BIntegration.ps1   # Windows PowerShell setup
│   └── api_manager.py             # CLI for API management
└── E2B_WEBHOOK_SETUP_GUIDE.md     # This file
```

## 🔧 Using the API Manager CLI

The `api_manager.py` script provides a command-line interface for all APIs.

### E2B Commands

```bash
# Create new sandbox
python3 scripts/api_manager.py e2b create --template python3

# List all sandboxes
python3 scripts/api_manager.py e2b list

# Execute code in sandbox
python3 scripts/api_manager.py e2b exec <sandbox_id> "print('Hello')"
```

### Zapier Commands

```bash
# Trigger Zapier webhook
python3 scripts/api_manager.py zapier execution.completed --data '{"status":"success"}'
```

### GitHub Commands

```bash
# Create issue
python3 scripts/api_manager.py github issue "Bug Report" "Description here"

# List branches
python3 scripts/api_manager.py github branches
```

### Gemini Commands

```bash
# Generate content
python3 scripts/api_manager.py gemini "Explain E2B webhooks"
```

### Status Check

```bash
# Check all API configurations
python3 scripts/api_manager.py status
```

## 🧪 Testing with Postman

### Import Collection

1. Open Postman
2. Click **Import**
3. Select `config/postman_collection.json`
4. Collection includes:
   - E2B webhook endpoints
   - Zapier integration tests
   - GitHub API calls
   - Gemini AI requests
   - Health checks

### Environment Variables in Postman

Set these variables in Postman:
- `base_url`: http://localhost:5000
- `e2b_api_key`: Your E2B API key
- `gemini_api_key`: Your Gemini API key
- `webhook_id`: YIyOpaJ0UMJ3Pl9Md5kVExEDdkqyDGRp

## 🌐 Webhook Server

### Start the Server

```bash
python3 scripts/e2b_webhook_handler.py
```

### Endpoints

- `POST /api/webhooks/e2b` - Receive E2B events
- `POST /api/webhooks/github` - GitHub webhook relay
- `POST /api/webhooks/zapier` - Zapier integration
- `GET /health` - Health check

### Example Webhook Payload

```json
{
  "event": "execution.completed",
  "execution_id": "exec_123",
  "sandbox_id": "sandbox_456",
  "status": "success",
  "output": "Hello from E2B!",
  "timestamp": "2025-12-21T00:00:00Z"
}
```

## 🔗 Integration Workflows

### 1. E2B → Zapier → Google Sheets

```
E2B Execution → Webhook Handler → Zapier → Google Sheets
```

**Setup:**
1. Create Zap with "Webhooks by Zapier" trigger
2. Copy webhook URL to `.env`
3. Add "Google Sheets" action
4. Map fields: execution_id, status, output

### 2. GitHub → E2B → Copilot

```
GitHub Push → E2B Sandbox → Execute Tests → Post to PR
```

**Setup:**
1. Configure GitHub webhook in repository settings
2. Point to `/api/webhooks/github`
3. Enable Copilot integration in `github_webhook_integration.json`

### 3. E2B → Gemini → Analysis

```
Code Execution → Gemini AI Review → GitHub Comment
```

**Setup:**
1. Enable in `e2b_webhook_config.json`
2. Configure Gemini API key
3. Set auto-review rules

## 🎯 Data Optimization Features

### Compression
- Payload compression: 60-80% reduction
- Minimal mode: Essential fields only
- Batch processing: Group multiple events

### Security
- HMAC-SHA256 signature verification
- AES-256-GCM encryption
- Rate limiting: 60 requests/minute
- IP whitelisting (optional)

### Configuration

Edit `config/e2b_webhook_config.json`:

```json
{
  "data_optimization": {
    "compress_payloads": true,
    "minimal_mode": true,
    "max_payload_size_kb": 100
  }
}
```

## 🐙 GitHub Copilot Integration

### Enable Copilot Sync

In `config/github_webhook_integration.json`:

```json
{
  "copilot_integration": {
    "enabled": true,
    "share_execution_context": true,
    "sync_with_copilot_workspace": true,
    "use_copilot_for_code_review": true
  }
}
```

### Features
- Share E2B execution context with Copilot
- Auto code review on PR
- Sync execution results to workspace
- AI-assisted debugging

## 🔐 Security Best Practices

1. **Never commit `.env` file**
2. **Rotate API keys every 90 days**
3. **Use environment-specific keys**
4. **Enable signature verification**
5. **Implement rate limiting**
6. **Monitor webhook logs**
7. **Use HTTPS in production**

## 🚨 Troubleshooting

### E2B Connection Issues

```bash
# Test E2B API
curl -H "Authorization: Bearer $E2B_API_KEY" \
  https://api.e2b.dev/sandboxes
```

### Zapier Not Receiving Events

1. Check webhook URL in `.env`
2. Verify Zap is enabled
3. Test with Postman
4. Check Zapier task history

### GitHub API Rate Limits

```bash
# Check rate limit
curl -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://api.github.com/rate_limit
```

### Webhook Handler Errors

```bash
# Check logs
tail -f logs/e2b_webhook.log

# Test handler
python3 scripts/e2b_webhook_handler.py
```

## 📊 Monitoring & Logs

### View Logs

```bash
# Real-time logs
tail -f logs/e2b_webhook.log

# Search logs
grep "error" logs/e2b_webhook.log
```

### Health Check

```bash
curl http://localhost:5000/health
```

## 🎓 Resources

- **E2B Documentation:** https://e2b.dev/docs
- **Zapier Help:** https://help.zapier.com
- **GitHub Webhooks:** https://docs.github.com/webhooks
- **Gemini API:** https://ai.google.dev/docs

## 📞 Support

For issues or questions:
1. Check troubleshooting section
2. Review configuration files
3. Check API status with `api_manager.py status`
4. Create GitHub issue in repository

## ✅ Checklist

- [ ] Environment variables configured
- [ ] All API keys added to `.env`
- [ ] Setup script executed successfully
- [ ] Postman collection imported
- [ ] Webhook server tested
- [ ] Zapier integration configured
- [ ] GitHub webhook set up
- [ ] Copilot integration enabled
- [ ] All APIs tested with `api_manager.py`

---

**Last Updated:** 2025-12-21
**Branch:** claude/setup-e2b-webhooks-CPFBo
**Webhook ID:** YIyOpaJ0UMJ3Pl9Md5kVExEDdkqyDGRp
