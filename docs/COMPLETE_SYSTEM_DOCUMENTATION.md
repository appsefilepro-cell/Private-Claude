# Agent X5.0 - Complete System Documentation

## System Overview

Agent X5.0 is a 250-agent multi-division AI orchestration system for automated trading, legal research, financial analysis, and business operations.

## Architecture

### Agent Distribution (250 Total)

| Division | Agents | Function |
|----------|--------|----------|
| Master CFO | 13 | Orchestration & Decisions |
| AI/ML | 33 | Research & Analysis |
| Legal | 35 | Legal Documentation |
| Trading | 30 | Market Analysis |
| Integration | 30 | API Management |
| Communication | 26 | Client Relations |
| DevOps/Security | 12 | Infrastructure |
| Financial | 20 | Tax & Accounting |
| Committee 100 | 20 | Specialized Tasks |
| Extended Roles | 31 | Cross-functional |

### Role Types

- **100 Executive Roles** - Strategic decision-making
- **50 Multi-Unit Agents** - Cross-functional operations
- **50 Co-Support Agents** - Division support
- **50 Coding/Developer Agents** - GitHub/GitLab/Zapier integration

## Automation

### Scheduled Workflows

| Workflow | Schedule | Trigger |
|----------|----------|---------|
| Bonds Trading | Hourly | `0 * * * *` |
| Trading Dashboard | Every 6 hours | `0 */6 * * *` |
| API Health Check | Daily 6 AM | `0 6 * * *` |
| Issue Monitoring | Every 15 min | `*/15 * * * *` |
| Security Scan | Every 4 hours | `0 */4 * * *` |

### External Triggers

Webhook endpoint: `https://api.github.com/repos/appsefilepro-cell/Private-Claude/dispatches`

Event types:
- `trading-signal`
- `bonds-alert`
- `api-health`
- `issue-created`
- `zapier-trigger`

## Trading Configuration

### Mode: PAPER (Safe Testing)

| Market | Status |
|--------|--------|
| BTC-USDT-SWAP | Active |
| ETH-USDT-SWAP | Active |
| SOL-USDT-SWAP | Active |
| XRP-USDT-SWAP | Active |

### Risk Management

- Max position: 2% of capital
- Max daily loss: 5%
- Max trades/day: 10
- Stop loss: Enabled
- Cooldown after loss: 30 min

## API Integrations

### Connected Services

| Service | Status | Used For |
|---------|--------|----------|
| Gemini AI | Active | Trading analysis |
| OKX | Paper Mode | Crypto trading |
| US Treasury | Active | Bond rates |
| GitHub | Active | Automation |
| GitLab Duo | Active | Code review |
| E2B | Configured | Sandbox |
| Zapier | Active | Workflows |

## Deployment

### Docker

```bash
docker-compose up -d
```

### E2B Sandbox

```bash
export E2B_API_KEY=your-key
python scripts/e2b_sandbox_launcher.py
```

### GitHub Actions

Workflows run automatically on:
- Push to main/claude/copilot branches
- Scheduled cron jobs
- External webhook triggers

## Security

- Vulnerability scanning every 4 hours
- Secret detection enabled
- Best practices checks
- CodeRabbit disabled (using Copilot/Duo)

## Monitoring

- API health checks daily
- Trading dashboard every 6 hours
- Issue monitoring every 15 minutes
- Automated alerts for failures

## Support

- Issues: GitHub Issues
- Documentation: /docs folder
- Status: AGENT_X5_STATUS_REPORT.json
