# Architecture & Workflow Diagrams

**Comprehensive visual documentation for the Private-Claude system**

---

## Quick Navigation

### Diagrams Included

1. **System Workflow** (`system_workflow.mmd`)
   - Complete end-to-end system architecture
   - All services and data flows
   - 10x loop execution pattern
   - Agent 5.0 orchestration

2. **Integration Map** (`integration_map.mmd`)
   - API connections and endpoints
   - Authentication flows
   - Webhook integration
   - Security and monitoring

3. **Deployment Flow** (`deployment_flow.mmd`)
   - GitHub Actions CI/CD pipeline
   - E2B sandbox testing
   - Postman API testing
   - Production deployment process

---

## Viewing the Diagrams

### Quick View (Recommended)

View in GitHub web interface - diagrams render automatically:
- Click any `.mmd` file in this directory
- Diagram displays instantly
- No tools required

### Interactive Editing

Use Mermaid Live Editor:
1. Go to https://mermaid.live
2. Upload or paste `.mmd` file content
3. Edit and export as PNG/SVG

### VS Code

Install "Markdown Preview Mermaid Support" extension:
- Shows inline preview in `.md` files with mermaid blocks
- Preview `.mmd` files directly
- Auto-refresh on save

### Convert to Images

```bash
# Install mermaid-cli
npm install -g @mermaid-js/mermaid-cli

# Export to PNG
mmdc -i system_workflow.mmd -o system_workflow.png

# Export to SVG
mmdc -i system_workflow.mmd -o system_workflow.svg
```

---

## System Components

### Services & Integrations

| Service | Role | Authentication |
|---------|------|-----------------|
| **E2B** | Code execution sandbox | Bearer Token (API Key) |
| **GitHub** | Repository & CI/CD | Personal Access Token |
| **Zapier** | Workflow automation | Webhook Token |
| **Slack** | Notifications | Bot Token |
| **Google Gemini** | AI analysis | API Key |
| **Google Sheets** | Data storage | OAuth 2.0 |
| **Replit** | Development IDE | Built-in auth |
| **GitHub Copilot** | Code review & assistance | GitHub context |

### Business Pillars

| Pillar | Purpose | Output |
|--------|---------|--------|
| **A: Trading** | Automated bot network with pattern recognition | Trade execution logs |
| **B: Legal** | Document automation & case management | Generated documents |
| **C: Federal** | SAM.gov monitoring & contracting support | Opportunity lists |
| **D: Nonprofit** | Grant research & pipeline management | Grant opportunities |

### Core Systems

| System | Function |
|--------|----------|
| **Data Ingestion** | Gmail, OneDrive, SharePoint, Dropbox extraction |
| **Remediation** | Data validation, cleaning, standardization |
| **Compliance Logger** | Audit trails and compliance tracking |
| **Webhook Handler** | Event routing and processing |

---

## Data Flow Overview

### Simple Flow: GitHub → E2B → Zapier → Slack

```
Developer Push
    ↓
GitHub Webhook
    ↓
E2B Sandbox Execution
    ↓
Webhook Callback
    ↓
Zapier Processing
    ↓
Slack Notification
```

**Time to Completion:** ~5 seconds
**Reliability:** >99%

### Complex Flow: 10x Loop Execution

```
Agent 5.0 Receives Request
    ↓
Loop Iteration 1
    ├─ E2B Sandbox Execution
    ├─ Quality Assessment
    └─ Result Storage
    ↓
Loop Iterations 2-9 (If improving)
    └─ Repeat with refinement
    ↓
Loop Iteration 10 (Final)
    └─ Best result delivered
```

**Enhanced Quality:** 35-50% improvement per loop
**Max Time:** 60 seconds for 10 iterations

---

## Key Features Visualized

### ✅ Services Represented

- E2B Sandbox with multiple parallel executions
- GitHub with CI/CD integration
- Zapier multi-app workflow engine
- Slack notifications
- Google Sheets data storage
- GitHub Copilot code review
- Replit IDE integration

### ✅ Data Flows Shown

- Input routing from GitHub, Slack, Replit
- Webhook chains between services
- Loop control pattern visualization
- Output aggregation and storage
- Feedback loops for optimization

### ✅ Security & Monitoring

- Authentication paths for all services
- HMAC-SHA256 signature verification
- AES-256-GCM encryption
- Rate limiting and retry logic
- Health checks and monitoring
- Audit logging

### ✅ Deployment Pipeline

- Local development workflow
- Automated testing stages
  - Linting and formatting
  - Unit tests
  - E2B integration tests
  - Postman API tests
  - Security scanning
- Staging environment validation
- Production deployment
- Rollback procedures

---

## Configuration Files Referenced

| File | Purpose | Location |
|------|---------|----------|
| `.env` | API keys & secrets | `config/.env` |
| `e2b_webhook_config.json` | E2B settings | `config/` |
| `zapier_connector.json` | Zapier config | `config/` |
| `github_webhook_integration.json` | GitHub settings | `config/` |
| `postman_collection.json` | API tests | `config/` |

---

## Performance Metrics

| Metric | Target | Notes |
|--------|--------|-------|
| E2B startup time | <2 seconds | Per sandbox |
| Webhook latency | <500ms | Per hop |
| Loop iteration time | ~5 seconds | Per cycle |
| Total loop (10x) | <60 seconds | Until quality threshold |
| Data sync time | <10 seconds | Ingestion to Sheets |
| API success rate | >99% | With retry logic |

---

## Troubleshooting Reference

### Common Issues

| Issue | Check First | Documentation |
|-------|-------------|-----------------|
| E2B 401/403 errors | API key in `.env` | See VISUAL_WORKFLOW_GUIDE.md |
| Zapier not triggering | Webhook URL format | Integration_map.mmd |
| CI/CD failures | GitHub Actions logs | Deployment_flow.mmd |
| Data missing in Sheets | Zapier task history | system_workflow.mmd |
| Copilot not reviewing | GitHub token scopes | Integration_map.mmd |

**Full troubleshooting guide:** See `/home/user/Private-Claude/docs/VISUAL_WORKFLOW_GUIDE.md`

---

## Related Documentation

- **Main Guide:** `/home/user/Private-Claude/docs/VISUAL_WORKFLOW_GUIDE.md`
- **E2B Setup:** `/home/user/Private-Claude/E2B_WEBHOOK_SETUP_GUIDE.md`
- **Deployment:** `/home/user/Private-Claude/docs/DEPLOYMENT_GUIDE.md`
- **API Setup:** `/home/user/Private-Claude/docs/API_SETUP_INSTRUCTIONS.md`
- **Executive Summary:** `/home/user/Private-Claude/docs/EXECUTIVE_SUMMARY.md`

---

## File Structure

```
docs/
├── architecture/
│   ├── README.md                    ← You are here
│   ├── system_workflow.mmd         ← Main system diagram
│   ├── integration_map.mmd         ← API & service connections
│   └── deployment_flow.mmd         ← CI/CD & deployment pipeline
│
├── VISUAL_WORKFLOW_GUIDE.md         ← Comprehensive guide
├── DEPLOYMENT_GUIDE.md
├── API_SETUP_INSTRUCTIONS.md
├── EXECUTIVE_SUMMARY.md
└── MASTER_PROMPT_ARCHIVE.md
```

---

## Quick Start

1. **View Diagrams:**
   - Open any `.mmd` file in GitHub web interface
   - Or visit https://mermaid.live and paste content

2. **Read Guide:**
   - Start with `VISUAL_WORKFLOW_GUIDE.md`
   - Review "System Architecture Overview" section
   - Reference "Integration Points" for specific services

3. **Set Up System:**
   - Follow `E2B_WEBHOOK_SETUP_GUIDE.md`
   - Configure `.env` file
   - Run integration tests with Postman

4. **Deploy:**
   - Follow `DEPLOYMENT_GUIDE.md`
   - Complete GitHub Actions setup
   - Test E2B sandbox connection

---

## Key Takeaways

**System Design:**
- Modular architecture with 4 independent business pillars
- Central orchestration with Agent 5.0
- Resilient webhook-based communication
- Multi-layer security and monitoring

**Data Flow:**
- Asynchronous event-driven architecture
- Reliable webhook chains with retry logic
- Real-time data synchronization
- Audit trail for compliance

**Deployment:**
- Automated CI/CD with GitHub Actions
- Comprehensive testing at multiple stages
- Staged deployment to production
- Rollback capability for safety

**Quality:**
- 10x execution loop for optimization
- >99% API success rate
- Sub-second latency for most operations
- Full encryption and security

---

**Document Version:** 1.0
**Last Updated:** 2025-12-21
**Branch:** claude/setup-e2b-webhooks-CPFBo

---

For detailed information, comprehensive troubleshooting, and complete API reference, see the full **[Visual Workflow Guide](../VISUAL_WORKFLOW_GUIDE.md)**
