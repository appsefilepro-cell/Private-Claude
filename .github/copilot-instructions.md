# GitHub Copilot Instructions for Agent X5 Repository

## System Identity
You are assisting with the **Agent X5.0 - Enterprise Multi-Agent Orchestration System**, a production-ready system with 219 agents across 8 divisions.

## Core Architecture
- **Master CFO (Agents 1-13)**: Orchestration & Delegation
- **AI/ML (Agents 14-46)**: Research & Analysis  
- **Legal (Agents 47-81)**: Legal Research & Documentation
- **Trading (Agents 82-111)**: 24/7 Market Analysis
- **Integration (Agents 112-141)**: Zapier & API Management
- **Communication (Agents 142-167)**: Client Communications
- **DevOps/Security (Agents 168-179)**: System Maintenance
- **Financial (Agents 180-199)**: Tax & CFO Suite
- **Committee 100 (Agents 200-219)**: Specialized Tasks

## Code Standards
- **Python**: Follow PEP 8, use type hints, async/await for concurrency
- **Security**: Never commit secrets, use environment variables, validate all inputs
- **Documentation**: Clear docstrings, inline comments for complex logic
- **Testing**: Write tests for new functionality, maintain >80% coverage
- **Error Handling**: Comprehensive try-except blocks with logging

## Trading Safety
- **Default Mode**: PAPER (simulated trading, no real money)
- **LIVE Trading**: Requires explicit `LIVE_TRADING=true` environment variable
- **Risk Management**: Always implement stop-loss, position sizing, max daily trades

## Integration Patterns
- **Zapier**: Use webhooks for real-time events, schedules for periodic tasks
- **APIs**: Implement rate limiting, retry logic, health checks
- **E2B Sandbox**: Use for code execution isolation
- **GitHub Actions**: Automate deployments, testing, issue management

## File Organization
- `/scripts`: Main orchestration and automation scripts
- `/config`: Configuration files (JSON), API keys templates
- `/pillar-*`: Specialized domain implementations (trading, legal, federal, nonprofit)
- `/agent-4.0`: Previous generation agent system
- `/core-systems`: Claude API integration, webhooks, data ingestion
- `/tests`: Unit and integration tests

## Agent X5 Orchestration
When working on agent coordination:
1. Review `config/AGENT_5_MERGE_AND_UNFINISHED_TASKS.json` for current task status
2. Follow delegation patterns in `config/COMMITTEE_100_MASTER_PROMPTS_ASSIGNMENTS.json`
3. Update `AGENT_X5_STATUS_REPORT.json` after completing tasks
4. Use parallel execution where possible for efficiency

## Automation Priorities
1. **FREE Tier First**: Optimize for free tiers (Zapier 100 tasks/month, GitHub Actions, etc.)
2. **24/7 Operations**: Design for continuous running without human intervention
3. **Self-Healing**: Implement error detection and automatic recovery
4. **Monitoring**: Log all operations, create dashboards, send alerts

## Common Tasks
- **New Agent**: Add to appropriate division in `agent_x5_master_orchestrator.py`
- **Zapier Workflow**: Document in `ZAPIER_COPILOT_ACTION_PLAN.md`
- **API Integration**: Add to `config/*.json` with health checks
- **Trading Strategy**: Implement in `pillar-a-trading/` with backtesting

## Quality Checks
Before committing:
- [ ] No secrets or API keys in code
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Error handling implemented
- [ ] Logging added for debugging
- [ ] PAPER mode is default for trading code

## Resources
- Main README: System overview and quick start
- DEPLOYMENT_README.md: Deployment instructions
- AGENT_EVOLUTION.md: Version history
- AGENT_4.0_ARCHITECTURE.md: Previous architecture reference

## Support
For complex tasks, leverage:
- GitHub Copilot Chat for code generation
- GitLab Duo for code review
- Claude AI for documentation
- Zapier Copilot for automation workflows
