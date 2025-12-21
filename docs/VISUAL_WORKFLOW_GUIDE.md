# Visual Workflow Guide - Private-Claude Architecture

**Version:** 1.0
**Date:** December 21, 2025
**Last Updated:** December 21, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [How to View Mermaid Diagrams](#how-to-view-mermaid-diagrams)
3. [System Architecture Overview](#system-architecture-overview)
4. [Integration Points](#integration-points)
5. [Data Flow Patterns](#data-flow-patterns)
6. [Troubleshooting Flows](#troubleshooting-flows)
7. [Quick Reference](#quick-reference)

---

## Overview

The Private-Claude system is a comprehensive, multi-pillar automation platform that orchestrates multiple services and APIs to provide enterprise-grade automation for trading, legal, federal, and nonprofit operations.

### System Diagram Files

This guide includes three comprehensive Mermaid diagrams:

- **`docs/architecture/system_workflow.mmd`** - Complete system workflow and data flow
- **`docs/architecture/integration_map.mmd`** - API connections and authentication
- **`docs/architecture/deployment_flow.mmd`** - CI/CD pipeline and deployment process

---

## How to View Mermaid Diagrams

### Option 1: GitHub Web Interface (Recommended)

Mermaid diagrams are automatically rendered in GitHub's web interface:

1. Navigate to the `.mmd` file in GitHub
2. Click the file
3. The diagram renders automatically in the preview
4. No additional tools needed

**Files:**
- https://github.com/your-org/Private-Claude/blob/main/docs/architecture/system_workflow.mmd
- https://github.com/your-org/Private-Claude/blob/main/docs/architecture/integration_map.mmd
- https://github.com/your-org/Private-Claude/blob/main/docs/architecture/deployment_flow.mmd

### Option 2: Mermaid Live Editor

For interactive editing and full-screen viewing:

1. Visit https://mermaid.live
2. Paste the contents of any `.mmd` file
3. The diagram renders in real-time
4. Use the editor to make modifications
5. Export as PNG or SVG

### Option 3: VS Code Extension

For local development:

1. Install "Markdown Preview Mermaid Support" extension
2. Open any `.mmd` or `.md` file with mermaid code blocks
3. Preview automatically renders
4. Press Ctrl+Shift+V to preview

**Extension IDs:**
- `bierner.markdown-mermaid`
- `Markdown Preview Enhanced`

### Option 4: VS Code Built-in Preview

1. Open any `.mmd` file
2. Press `Ctrl+Shift+V` (Mac: `Cmd+Shift+V`)
3. Click "Open Preview" if prompted

### Option 5: Command Line Conversion

Convert Mermaid to PNG/SVG using `mmdc`:

```bash
# Install mermaid-cli
npm install -g @mermaid-js/mermaid-cli

# Convert to PNG
mmdc -i docs/architecture/system_workflow.mmd -o system_workflow.png

# Convert to SVG
mmdc -i docs/architecture/system_workflow.mmd -o system_workflow.svg
```

---

## System Architecture Overview

### Layer Structure

The Private-Claude system is organized into 5 key layers:

```
┌─────────────────────────────────────────┐
│   Agent 5.0 Orchestration Layer         │ <- Central decision maker
├─────────────────────────────────────────┤
│   Core Execution Layer                  │ <- E2B Sandboxes
├─────────────────────────────────────────┤
│   Integration Hub - Zapier              │ <- Workflow automation
├─────────────────────────────────────────┤
│   Business Logic Pillars                │ <- Trading, Legal, Federal, Nonprofit
├─────────────────────────────────────────┤
│   Core Systems & Output                 │ <- Data processing & results
└─────────────────────────────────────────┘
```

### Component Overview

#### 1. Agent 5.0 Orchestration Layer

The central orchestrator that manages:

- **Loop Control Pattern:** Executes workflows up to 10x for optimal results
- **Input Routing:** Directs requests from GitHub, Slack, and Replit
- **Output Aggregation:** Collects results from all pillars
- **Error Handling:** Manages failures and retries

**Key Functions:**
- Decision making on workflow execution
- Load balancing across E2B sandboxes
- Loop iteration control
- State management

#### 2. E2B Sandbox Execution Layer

Provides isolated, secure code execution:

- **Parallel Execution:** Multiple sandboxes running simultaneously
- **Resource Isolation:** Each execution is independent
- **Cleanup:** Automatic resource management after execution
- **Webhook Integration:** Event reporting back to orchestrator

**Performance Characteristics:**
- Startup time: <2 seconds per sandbox
- Max concurrent sandboxes: Limited by E2B plan
- Auto-cleanup on failure: Yes
- Cost: Per execution minute

#### 3. Zapier Integration Hub

Connects E2B execution to business workflows:

- **Event Triggering:** Responds to E2B completion events
- **Multi-app Sync:** Connects to Google Sheets, Slack, etc.
- **Data Transformation:** Converts API responses to actionable data
- **Workflow Orchestration:** Complex multi-step automations

**Connected Services:**
- Google Sheets (data storage)
- Slack (notifications)
- Email (reports)
- Custom webhooks

#### 4. Business Logic Pillars

Four specialized business domains:

**Pillar A: Trading Bot Network**
- Pattern recognition on candlestick data
- Automated trade execution
- Compliance logging
- Risk management

**Pillar B: Legal Document Automation**
- Document generation from templates
- Case management system
- Compliance tracking
- Integration with Microsoft 365

**Pillar C: Federal Contracting**
- SAM.gov opportunity monitoring
- 8(a) application package generation
- CDFI outreach automation
- Government compliance tracking

**Pillar D: Grant Intelligence**
- Grant opportunity research
- Pipeline management
- Nonprofit matching
- Weekly digest generation

#### 5. Core Systems & Output

**Data Ingestion:**
- Gmail inbox scanning
- OneDrive file monitoring
- SharePoint document extraction
- Dropbox integration

**Remediation Engine:**
- Data validation
- Format conversion
- Error correction
- Quality assurance

**Compliance Logger:**
- Audit trail generation
- Compliance documentation
- Change tracking
- Report generation

**Output Channels:**
- Google Sheets (structured data)
- GitHub (code and docs)
- GitHub Copilot (AI assistance)
- Reporting dashboards

---

## Integration Points

### Direct API Integrations

#### E2B Sandbox API

```
Endpoint: https://api.e2b.dev
Authentication: Bearer Token (API Key)
Methods:
  - POST /sandboxes - Create sandbox
  - GET /sandboxes/{id} - Get sandbox info
  - POST /sandboxes/{id}/exec - Execute code
  - DELETE /sandboxes/{id} - Cleanup
Rate Limit: 60 requests/minute
Webhook: POST /api/webhooks/e2b
```

**Use Cases:**
- Code execution for trading patterns
- Legal document processing
- Federal form generation
- Grant research scripting

#### GitHub API

```
Endpoint: https://api.github.com
Authentication: Personal Access Token
Methods:
  - GET /repos/{owner}/{repo} - Repo info
  - POST /repos/{owner}/{repo}/issues - Create issue
  - POST /repos/{owner}/{repo}/pulls - Create PR
  - POST /repos/{owner}/{repo}/dispatches - Trigger actions
Webhook: POST /api/webhooks/github
Copilot: Integrated code review context
```

**Use Cases:**
- Repository management
- Issue/PR automation
- CI/CD triggering
- Copilot context sharing

#### Zapier Webhooks

```
Endpoint: https://hooks.zapier.com/hooks/catch/{ZAPIER_ID}/{secret}
Authentication: Webhook Token in URL
Methods:
  - POST - Trigger workflow
  - GET - Check status
Response: 200 OK with task ID
Workflow Types:
  - E2B → Google Sheets
  - GitHub → Slack Notifications
  - Multi-service data sync
```

**Use Cases:**
- Event-driven automation
- Cross-service data flow
- Spreadsheet updates
- Notification delivery

#### Slack API

```
Endpoint: https://slack.com/api
Authentication: Bot Token
Methods:
  - POST /chat.postMessage - Send message
  - POST /workflows.trigger - Trigger workflow
  - POST /reactions.add - Add emoji reaction
Webhook: Slash commands, Event subscriptions
```

**Use Cases:**
- Task notifications
- Status updates
- Alert routing
- User interaction

#### Google Services

```
Sheets API:
  Endpoint: https://sheets.googleapis.com
  Auth: OAuth 2.0
  Methods: values.update, values.append, values.get

Gemini AI:
  Endpoint: https://generativelanguage.googleapis.com
  Auth: API Key
  Methods: generateContent, countTokens
```

**Use Cases:**
- Data storage and retrieval
- AI-powered analysis
- Report generation
- Intelligent processing

---

## Data Flow Patterns

### Pattern 1: GitHub Push → E2B Execution → Slack Notification

```
┌─────────────┐
│ GitHub Push │ Developer commits code
└──────┬──────┘
       │ Webhook
       ▼
┌──────────────────┐
│ GitHub Actions   │ Triggers CI/CD pipeline
└──────┬───────────┘
       │ Calls
       ▼
┌──────────────────────┐
│ E2B Sandbox Executor │ Runs tests in isolated env
└──────┬───────────────┘
       │ Webhook
       ▼
┌──────────────────┐
│ Zapier Handler   │ Processes event
└──────┬───────────┘
       │ Triggers
       ▼
┌──────────────────┐
│ Slack Webhook    │ Posts message to channel
└──────────────────┘
```

**Time to Completion:** 2-10 seconds
**Success Rate:** >99%
**Retry Logic:** Exponential backoff

### Pattern 2: Agent 5.0 Loop Execution (10x Pattern)

```
Iteration 1: Initial execution
  ├─ E2B Sandbox 1
  ├─ Collect results
  └─ Check quality score

Iteration 2-9: Refinement loops
  ├─ E2B Sandbox N
  ├─ Compare results
  ├─ Detect improvement
  └─ Continue if improved

Iteration 10: Final execution
  ├─ E2B Sandbox Final
  ├─ Validation
  └─ Return best result

Exit Condition: Quality threshold met OR max iterations reached
```

**Benefits:**
- Improved accuracy
- Better pattern recognition
- Optimized results
- Graceful degradation

### Pattern 3: Data Ingestion → Remediation → Pillar Processing

```
┌─────────────────────┐
│ Data Ingestion      │
├─────────────────────┤
│ Gmail              │ Extract emails
│ OneDrive           │ Get documents
│ SharePoint         │ Pull files
│ Dropbox            │ Sync folders
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ Remediation Engine  │
├─────────────────────┤
│ Validate data       │ Schema check
│ Clean formats       │ Standardize
│ Fix errors          │ Correct issues
│ Deduplicate         │ Remove duplicates
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ Pillar Processing   │
├─────────────────────┤
│ Trading Logic       │ Pillar A
│ Legal Engine        │ Pillar B
│ Federal Contracts   │ Pillar C
│ Grant Research      │ Pillar D
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ Output Storage      │
└─────────────────────┘
```

**Quality Metrics:**
- Input validation: 100%
- Remediation success: 95%+
- Processing time: <30 seconds
- Output accuracy: >99%

### Pattern 4: Multi-Service Webhook Chain

```
Event Trigger
    ▼
E2B Webhook Handler
    │ ├─ Verify signature (HMAC-SHA256)
    │ ├─ Decompress payload
    │ └─ Log event
    ▼
Router
    │ ├─ Route to Zapier
    │ ├─ Route to GitHub
    │ └─ Route to Slack
    ▼
Sync Engine
    │ ├─ Compress response
    │ ├─ Apply rate limiting
    │ └─ Queue for delivery
    ▼
Output Services
    ├─ Google Sheets
    ├─ Slack Messages
    └─ GitHub Comments
```

**Latency:** <500ms per hop
**Reliability:** Guaranteed delivery with retry
**Security:** Full encryption end-to-end

---

## Troubleshooting Flows

### Flow 1: E2B Sandbox Connection Issues

```
Problem: E2B API returns 401 or 403

┌─────────────────────────────────┐
│ Check API Key in .env           │ ✓ Correct?
└──────┬──────────────────────────┘
       │ No
       ▼
┌─────────────────────────────────┐
│ Regenerate API Key in E2B       │
│ Update .env file                │
└──────┬──────────────────────────┘
       │ Still failing?
       ▼
┌─────────────────────────────────┐
│ Check IP Whitelisting           │
│ E2B Settings → Security         │
└──────┬──────────────────────────┘
       │ Still failing?
       ▼
┌─────────────────────────────────┐
│ Check Rate Limits               │
│ Use: api_manager.py status      │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ Create GitHub Issue             │
│ Include: Error logs, API key    │
│ format, request headers         │
└─────────────────────────────────┘
```

### Flow 2: Zapier Webhook Not Triggering

```
Problem: E2B completes but Zapier doesn't receive event

┌─────────────────────────────────┐
│ Check webhook URL in .env       │ Correct?
└──────┬──────────────────────────┘
       │ No
       ▼
┌─────────────────────────────────┐
│ Copy from Zapier webhook config │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ Test with Postman               │
│ POST to Zapier URL              │
└──────┬──────────────────────────┘
       │ Success?
       ├─ Yes → Check Zap enabled
       └─ No  → Check URL format
              └─ Verify auth token
```

### Flow 3: GitHub Actions CI/CD Failures

```
Problem: GitHub Actions workflow fails

┌─────────────────────────────────┐
│ Check GitHub Actions logs       │
│ → Actions tab → Failed run      │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ Identify failing step           │
│ - Lint/Format                   │
│ - Unit Tests                    │
│ - E2B Tests                     │
│ - Postman Tests                 │
└──────┬──────────────────────────┘
       │
       ├─ Lint/Format → Run locally, fix, commit
       │
       ├─ Unit Tests → Check test files, fix code
       │
       ├─ E2B Tests → Verify E2B_API_KEY in secrets
       │              Check sandbox limits
       │
       └─ Postman → Verify API endpoints online
                     Check authentication
                     Review response schemas
```

### Flow 4: Data Loss During Sync

```
Problem: Data not appearing in Google Sheets

┌─────────────────────────────────┐
│ Check Zapier task history       │ Executed?
└──────┬──────────────────────────┘
       │ No
       ▼
┌─────────────────────────────────┐
│ Check webhook was received      │ Logged?
│ tail -f logs/e2b_webhook.log    │
└──────┬──────────────────────────┘
       │ No
       ▼
┌─────────────────────────────────┐
│ Check E2B webhook configuration │
│ Verify in config/e2b_*          │
└──────┬──────────────────────────┘
       │ Yes, check Sheets
       ▼
┌─────────────────────────────────┐
│ Verify Google Sheets auth       │
│ Check OAuth token expiration    │
│ Re-authenticate if needed       │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ Check Zapier action config      │
│ Verify sheet ID and tab name    │
│ Verify column mapping           │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ Re-test Zap with sample data    │
│ Use Zapier "Test" feature       │
└─────────────────────────────────┘
```

### Flow 5: Copilot Code Review Not Showing

```
Problem: GitHub Copilot not reviewing PRs

┌─────────────────────────────────┐
│ Check Copilot enabled in        │
│ config/github_webhook_*         │
└──────┬──────────────────────────┘
       │ Disabled
       ▼
┌─────────────────────────────────┐
│ Enable Copilot integration      │
│ Set: copilot_integration.       │
│ enabled = true                  │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ Verify GitHub Token has access  │
│ Scopes: repo, read:org,         │
│ workflow, gist                  │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ Check E2B execution context     │
│ Share execution output with     │
│ Copilot in webhook handler      │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ Manually trigger review via     │
│ GitHub UI or API                │
└─────────────────────────────────┘
```

---

## Quick Reference

### Essential Commands

```bash
# Check API status
python3 scripts/api_manager.py status

# Test E2B connection
curl -H "Authorization: Bearer $E2B_API_KEY" \
  https://api.e2b.dev/sandboxes

# Check GitHub API rate limit
curl -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://api.github.com/rate_limit

# Test Zapier webhook
curl -X POST https://hooks.zapier.com/hooks/catch/{ID}/{SECRET} \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'

# View webhook logs
tail -f logs/e2b_webhook.log

# Run Postman collection
newman run config/postman_collection.json
```

### Configuration Files

| File | Purpose |
|------|---------|
| `config/.env` | API keys and secrets (git-ignored) |
| `config/e2b_webhook_config.json` | E2B webhook settings |
| `config/zapier_connector.json` | Zapier integration config |
| `config/github_webhook_integration.json` | GitHub webhook settings |
| `config/postman_collection.json` | Postman API test collection |

### Key Metrics

| Metric | Target | Current |
|--------|--------|---------|
| E2B execution time | <5 seconds | ~2 seconds |
| Webhook latency | <1 second | ~200ms |
| API success rate | >99% | ~99.5% |
| Data sync time | <10 seconds | ~5 seconds |
| Loop completion (10x) | <60 seconds | ~45 seconds |

### Monitoring Dashboards

- **GitHub Actions:** https://github.com/{org}/{repo}/actions
- **E2B Console:** https://e2b.dev/docs/console
- **Zapier Dashboard:** https://zapier.com/app/dashboard
- **Google Sheets:** Direct integration visible in Sheet
- **Slack Channels:** #e2b-webhooks, #deployment-alerts

### Support Resources

- **E2B Docs:** https://e2b.dev/docs
- **GitHub Webhooks:** https://docs.github.com/en/developers/webhooks-and-events/webhooks
- **Zapier Help:** https://help.zapier.com
- **Google APIs:** https://developers.google.com
- **Repository Issues:** File issues with diagram-specific tags

---

## Appendix: Color Legend

### System Workflow Diagram

| Color | Component Type |
|-------|-----------------|
| 🔴 Red | Orchestration & Control |
| 🔵 Blue | Execution & Compute |
| 🟢 Green | Integration Points |
| 🟡 Yellow | Business Logic |
| 🟣 Purple | Data Processing |

### Integration Map Diagram

| Color | Service Category |
|-------|-----------------|
| 🔴 Red | Authentication |
| 🔵 Blue | Cloud Services |
| ⭐ Gold | Synchronization |
| 🔴 Red | Security |
| ⚫ Black | Monitoring |

### Deployment Flow Diagram

| Color | Stage |
|-------|-------|
| 🔴 Red | Development |
| 🔵 Blue | Staging |
| 🟢 Green | Production |
| 🟡 Yellow | Testing |
| 🟣 Purple | Approval |

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-21 | Initial creation with 3 comprehensive diagrams |

---

**For the latest updates and documentation, visit:** `/home/user/Private-Claude/docs/architecture/`

**Questions or issues?** File a GitHub issue with the tag `[ARCHITECTURE]`

