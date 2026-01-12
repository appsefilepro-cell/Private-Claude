# Postman API MCP Integration Guide

## Overview

This guide explains how to integrate Agent X5.0 with Postman API for automated API testing, monitoring, and collection management.

---

## Quick Start (5 Minutes)

### Step 1: Get Postman API Key

1. Go to [Postman Account Settings](https://go.postman.co/settings/me/api-keys)
2. Click **Generate API Key**
3. Name it: `Agent-X5-Integration`
4. Copy the API key (shown once only)

### Step 2: VS Code Extension Authentication

The VS Code extension URL provided contains an authorization code:
```
vscode://Postman.postman-for-vscode?code=482ee78e89079905b270c99d578eb06ae729773eb796e9544ba5e96ea37923fe
```

This code is used to authenticate the Postman VS Code extension with your Postman account.

### Step 3: Configure Environment Variables

Add to your `config/.env` file:

```bash
POSTMAN_API_KEY=your_api_key_here
POSTMAN_WORKSPACE_ID=your_workspace_id
POSTMAN_VSCODE_AUTH_CODE=482ee78e89079905b270c99d578eb06ae729773eb796e9544ba5e96ea37923fe
POSTMAN_COLLECTION_ID=your_collection_id
```

### Step 4: Test Connection

```bash
cd /home/runner/work/Private-Claude/Private-Claude
python pillar-a-trading/zapier-integration/postman_mcp_connector.py
```

---

## Features

### 1. API Testing Automation
- Automated endpoint testing
- Response validation
- Performance monitoring
- Integration testing

### 2. Collection Management
- Create and manage collections
- Import/export collections
- Version control for API tests
- Share collections with team

### 3. Monitoring & Alerts
- Scheduled API health checks
- Real-time monitoring
- Custom alert rules
- Integration with Slack/Teams

### 4. VS Code Integration
- Send requests from VS Code
- Manage collections in editor
- Debug API responses
- Sync with Postman Cloud

---

## Usage Examples

### Example 1: Test Trading API Health

```python
from pillar_a_trading.zapier_integration.postman_mcp_connector import PostmanMCPConnector

connector = PostmanMCPConnector()

# Check connection
status = connector.check_connection()
print(f"Connected: {status['connected']}")

# List available collections
collections = connector.list_collections()
for collection in collections:
    print(f"Collection: {collection['name']}")
```

### Example 2: Create API Test Collection

```python
# Create a new collection for trading API tests
result = connector.create_collection(
    name="Agent X5.0 Trading API Tests",
    description="Automated tests for trading bot endpoints"
)

if result['success']:
    collection_id = result['collection']['id']
    print(f"Collection created: {collection_id}")
```

### Example 3: Set Up Monitoring

```python
# Create a monitor to check API health every 6 hours
schedule = {
    "cron": "0 */6 * * *",
    "timezone": "America/Los_Angeles"
}

monitor = connector.create_monitor(
    collection_id="your_collection_id",
    name="Trading API Health Monitor",
    schedule=schedule
)

print(f"Monitor created: {monitor['monitor']['name']}")
```

### Example 4: Generate Trading API Test Config

```python
# Create test configuration for trading endpoint
test_config = connector.integrate_with_trading_bot(
    api_endpoint="https://api.agentx5.com/trade/signal",
    method="POST"
)

print(f"Test config: {test_config['name']}")
```

---

## Integration with Agent X5.0 Systems

### Trading Bot Integration

```python
# Test trading bot API endpoints
trading_tests = connector.integrate_with_trading_bot(
    api_endpoint="http://localhost:8000/api/market/BTC-USD",
    method="GET"
)

# Run tests before executing trades
result = connector.run_collection(collection_id="trading_api_tests")
```

### Zapier Integration

Combine Postman and Zapier for powerful automation:

1. **Postman** runs API tests
2. **Zapier** processes results
3. **Actions** based on test outcomes:
   - Send alerts if tests fail
   - Log results to Google Sheets
   - Create GitHub issues for failures
   - Notify team via Slack

### CI/CD Integration

Add to your GitHub Actions workflow:

```yaml
- name: Run Postman Tests
  run: |
    newman run collection.json \
      -e environment.json \
      --reporters cli,json \
      --reporter-json-export results.json
```

---

## VS Code Extension Setup

### Installation

1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "Postman"
4. Install "Postman" by Postman

### Authentication

Use the provided authorization code:

1. Click the Postman icon in VS Code sidebar
2. Click "Sign In"
3. Or use the URL directly:
   ```
   vscode://Postman.postman-for-vscode?code=482ee78e89079905b270c99d578eb06ae729773eb796e9544ba5e96ea37923fe
   ```
4. Your extension is now connected to Postman Cloud

### Features in VS Code

- **Send Requests**: Test APIs directly from editor
- **Collections**: Access all your Postman collections
- **Environments**: Switch between dev/staging/prod
- **History**: View previous API requests
- **Sync**: Auto-sync with Postman Cloud

---

## API Endpoints Reference

### Base URL
```
https://api.getpostman.com
```

### Authentication
```
X-Api-Key: YOUR_API_KEY
```

### Common Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/me` | GET | Get current user info |
| `/workspaces` | GET | List workspaces |
| `/collections` | GET | List collections |
| `/collections/{id}` | GET | Get collection details |
| `/collections` | POST | Create collection |
| `/environments` | GET | List environments |
| `/monitors` | POST | Create monitor |

---

## Monitoring & Alerts

### Set Up Daily Health Checks

```python
# Monitor trading API every 6 hours
connector.create_monitor(
    collection_id="trading_api_collection",
    name="Daily Trading API Health",
    schedule={
        "cron": "0 */6 * * *",
        "timezone": "America/Los_Angeles"
    }
)
```

### Alert Notifications

Configure alerts in `config/postman_mcp_config.json`:

```json
{
  "monitors": {
    "trading_api_monitor": {
      "notifications": {
        "on_failure": true,
        "email": "your-email@example.com",
        "slack_webhook": "https://hooks.slack.com/..."
      }
    }
  }
}
```

---

## Newman CLI (Command Line Runner)

### Installation

```bash
npm install -g newman
```

### Run Collection

```bash
# Basic run
newman run collection.json

# With environment
newman run collection.json -e environment.json

# With reporters
newman run collection.json --reporters cli,html,json

# In CI/CD
newman run collection.json \
  --environment production.json \
  --reporters cli,json \
  --reporter-json-export results.json
```

---

## Best Practices

### 1. API Key Security
- Store API key in `.env` file
- Never commit `.env` to version control
- Rotate API keys every 90 days
- Use separate keys for dev/prod

### 2. Collection Organization
- One collection per service/API
- Use folders to group related requests
- Document each request with descriptions
- Use environment variables for dynamic values

### 3. Testing Strategy
- Test all critical endpoints
- Validate response status codes
- Check response times (< 2000ms)
- Verify data structure and types
- Test error handling

### 4. Monitoring
- Monitor production APIs 24/7
- Set up alerts for failures
- Track API performance trends
- Review monitor results weekly

---

## Troubleshooting

### Issue: API Key Invalid

**Solution:**
1. Verify API key in Postman account settings
2. Check key hasn't expired
3. Ensure key has proper permissions
4. Regenerate key if necessary

### Issue: Rate Limit Exceeded

**Solution:**
- Postman API allows 60 requests/minute
- Implement rate limiting in your code
- Use caching where possible
- Consider upgrading plan for higher limits

### Issue: VS Code Extension Not Connecting

**Solution:**
1. Verify authorization code is correct
2. Try signing out and back in
3. Reinstall extension if needed
4. Check internet connectivity

### Issue: Collection Run Fails

**Solution:**
1. Check API endpoint is accessible
2. Verify environment variables are set
3. Review test scripts for errors
4. Check authentication headers

---

## Integration Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Agent X5.0                           │
│                                                         │
│  ┌──────────────┐      ┌─────────────────────┐        │
│  │   Trading    │──────│  Postman MCP        │        │
│  │     Bot      │      │   Connector         │        │
│  └──────────────┘      └─────────────────────┘        │
│                                 │                       │
│                                 │                       │
└─────────────────────────────────┼───────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │    Postman API Cloud    │
                    │                         │
                    │  - Collections          │
                    │  - Monitors             │
                    │  - Environments         │
                    │  - Test Results         │
                    └─────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
          ┌──────────────────┐       ┌──────────────────┐
          │  VS Code         │       │  Newman CLI      │
          │  Extension       │       │  (CI/CD)         │
          └──────────────────┘       └──────────────────┘
```

---

## API Rate Limits

| Plan | Rate Limit | Daily Limit |
|------|-----------|-------------|
| Free | 60/min | 1,000/day |
| Basic | 60/min | 10,000/day |
| Professional | 120/min | Unlimited |
| Enterprise | Custom | Unlimited |

---

## Resources

- **Postman API Documentation**: https://www.postman.com/postman/workspace/postman-public-workspace/documentation/12959542-c8142d51-e97c-46b6-bd77-52bb66712c9a
- **VS Code Extension**: https://marketplace.visualstudio.com/items?itemName=Postman.postman-for-vscode
- **Newman CLI**: https://learning.postman.com/docs/running-collections/using-newman-cli/command-line-integration-with-newman/
- **Postman Learning Center**: https://learning.postman.com/

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Postman API documentation
3. Contact: appsefilepro@gmail.com
4. Create GitHub issue in Private-Claude repository

---

**Agent X5.0 - Postman MCP Integration**
*Version 1.0.0 | January 2026 | APPS Holdings WY Inc.*
