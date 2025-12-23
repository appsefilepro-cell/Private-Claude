# GitHub Enterprise & GitLab Activation Guide

Complete guide for activating GitHub Enterprise features, GitHub Copilot, and GitLab integration with Agent 5.0.

## Overview

This repository is configured with:
- **GitHub Enterprise** with 30-day trial
- **GitHub Copilot Business** for AI-powered development
- **GitLab Integration** with CI/CD pipelines
- **Agent 5.0** orchestration system
- **E2B Sandbox** testing environment
- **Postman API** testing automation

## Quick Start

### 1. Prerequisites

- GitHub Enterprise organization: `Private-Claude-Enterprise`
- GitHub repository: `appsefilepro-cell/Private-Claude`
- GitLab project: `appsefilepro-group/appsefilepro-project`
- Admin access to both platforms
- Required API keys and tokens

### 2. Set Up Environment Variables

```bash
# Copy the template
cp .env.github.template .env

# Edit .env and fill in your actual values
nano .env  # or use your preferred editor

# Load environment variables
source .env
```

### 3. Run Activation Script

```bash
# Make script executable
chmod +x scripts/github_activator.py

# Run the activation
python scripts/github_activator.py

# Check the activation log
cat logs/github_activation.json
```

## Features Activated

### GitHub Enterprise Features

#### 1. **GitHub Copilot Business**
- ✅ Organization-wide Copilot activation
- ✅ Code completion with inline suggestions
- ✅ Copilot Chat for AI assistance
- ✅ PR code reviews with Copilot
- ✅ Documentation generation
- ✅ Context-aware suggestions

**Configuration**: `.github/copilot/copilot-config.yml`

#### 2. **Branch Protection Rules**
- ✅ **Main branch**: 2 required reviews, strict status checks
- ✅ **Develop branch**: 1 required review, flexible checks
- ✅ Required status checks: Copilot Review, E2B Tests, Security Scan
- ✅ No force pushes or deletions
- ✅ Required conversation resolution

#### 3. **Advanced Security**
- ✅ Secret scanning with push protection
- ✅ Custom secret patterns (E2B, Anthropic, AWS keys)
- ✅ CodeQL analysis for Python, JavaScript, TypeScript
- ✅ Dependabot alerts and automatic updates
- ✅ Dependency review on PRs
- ✅ SARIF upload for security reports

#### 4. **GitHub Actions**
- ✅ Automated workflow: `agent-5-automation.yml`
- ✅ Multi-stage pipeline (14 jobs)
- ✅ E2B sandbox testing
- ✅ Postman API collection tests
- ✅ Security scanning (Trivy, CodeQL)
- ✅ Staging and production deployments
- ✅ Cost optimization with caching

#### 5. **Webhooks**
- ✅ E2B Integration webhook
- ✅ Zapier Automation webhook
- ✅ Slack notifications
- ✅ Repository dispatch events

### GitLab Integration Features

#### 1. **GitLab CI/CD**
- ✅ Multi-stage pipeline configuration
- ✅ Security scanning (SAST, secret detection)
- ✅ Code quality checks
- ✅ E2B sandbox integration
- ✅ Postman API tests
- ✅ Automated deployments

**Configuration**: `.gitlab-ci.yml`

#### 2. **Merge Request Automation**
- ✅ Required approvals (1 for develop, 2 for main)
- ✅ Reset approvals on push
- ✅ Prevent author approval
- ✅ Prevent committer approval

#### 3. **GitLab Copilot**
- ✅ Code suggestions
- ✅ Code completion
- ✅ Chat assistance
- ✅ Code review
- ✅ Vulnerability explanations

**Configuration**: `config/integrations/gitlab_config.json`

#### 4. **Repository Mirroring**
- ✅ Bidirectional sync with GitHub
- ✅ Automatic sync on push
- ✅ Merge request to PR synchronization

## Workflow Architecture

### GitHub Actions Workflow

```
┌─────────────────────────────────────────────────────────┐
│  Trigger: Push to main/develop, PR, Manual              │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴──────────────┐
        │                           │
        ▼                           ▼
┌───────────────┐          ┌──────────────┐
│ Copilot       │          │ Code Quality │
│ Code Review   │          │ & Security   │
└───────┬───────┘          └──────┬───────┘
        │                         │
        └────────┬────────────────┘
                 │
        ┌────────┴──────────────┐
        │                       │
        ▼                       ▼
┌──────────────┐       ┌──────────────┐
│ E2B Tests    │       │ Postman Tests│
└──────┬───────┘       └──────┬───────┘
       │                      │
       └──────────┬───────────┘
                  │
                  ▼
         ┌────────────────┐
         │ Build & Deploy │
         └────────────────┘
```

### GitLab CI/CD Pipeline

```
Security → Quality → Test → E2B → Postman → Build → Deploy → Notify
   │          │        │      │       │        │       │        │
   ▼          ▼        ▼      ▼       ▼        ▼       ▼        ▼
Secret    Code      Unit   E2B     Postman  Docker  Staging  Slack
Detection Quality   Tests  Tests   Tests    Build   Deploy   Notify
SAST      Linting   Coverage       API      Docs    Prod
```

## GitHub Copilot Usage

### In Your IDE

1. **Install GitHub Copilot Extension**
   - VS Code: Install "GitHub Copilot" extension
   - JetBrains: Install "GitHub Copilot" plugin
   - Neovim: Install copilot.vim

2. **Sign in with GitHub**
   - Use your organization account
   - Copilot will automatically activate

3. **Start Coding**
   - Type code and Copilot suggests completions
   - Press Tab to accept suggestions
   - Use Ctrl+Enter to see more suggestions

### Copilot Chat

```
# Open Copilot Chat
/explain     - Explain selected code
/fix         - Suggest fixes for bugs
/test        - Generate unit tests
/doc         - Generate documentation
/optimize    - Suggest performance improvements
```

### PR Code Reviews

Copilot automatically reviews PRs and:
- Identifies security vulnerabilities
- Suggests code improvements
- Checks code quality
- Recommends refactoring

## E2B Integration

### Automated Testing

E2B sandboxes run on:
- Every push to main/develop
- Every pull request
- Manual workflow dispatch

### E2B Workflow

1. **Sandbox Creation**: `e2b_sandbox_manager.py`
2. **Code Execution**: Run tests in isolated environment
3. **Result Collection**: Gather logs and metrics
4. **Cleanup**: Destroy sandbox after tests

### Monitor E2B

```bash
# Check E2B status
python scripts/e2b_lifecycle.py --health-check

# Run E2B tests manually
python scripts/e2b_sandbox_manager.py --mode test

# View E2B logs
cat logs/e2b_execution.log
```

## Postman Integration

### API Testing

Postman collections run:
- After code quality checks
- Before deployment
- On schedule (daily)

### Postman Workflow

1. **Collection Sync**: `postman_sync.py`
2. **Newman Execution**: Run collection with Newman CLI
3. **Report Generation**: HTML reports with test results
4. **Result Upload**: Artifacts stored for 30 days

### Run Postman Tests

```bash
# Sync collection
python scripts/postman_sync.py --sync

# Run collection locally
newman run config/postman_complete_collection.json \
  --env-var "E2B_API_KEY=$E2B_API_KEY"
```

## Deployment Workflows

### Staging Deployment

- **Trigger**: Push to `develop` branch
- **Environment**: staging.private-claude.app
- **Approval**: Automatic
- **Auto-stop**: 7 days

### Production Deployment

- **Trigger**: Push to `main` branch
- **Environment**: private-claude.app
- **Approval**: Manual (requires 2 approvals)
- **Auto-stop**: Never

### Rollback

```bash
# Trigger rollback workflow
gh workflow run agent-5-automation.yml \
  --field deploy_environment=production \
  --field rollback=true
```

## Monitoring & Notifications

### Slack Integration

Notifications sent to:
- `#github-updates` - GitHub events
- `#gitlab-updates` - GitLab events
- `#deployments` - Deployment status

### Zapier Automation

Webhooks trigger Zapier workflows:
- Pipeline completion
- Deployment success/failure
- Security alerts
- E2B test results

### Audit Logs

```bash
# View activation log
cat logs/github_activation.json

# View GitHub Actions logs
gh run list --limit 10

# View GitLab pipeline logs
gitlab ci list --project appsefilepro-group/appsefilepro-project
```

## Security Best Practices

### Secrets Management

1. **Never commit secrets** to version control
2. **Use GitHub Secrets** for Actions workflows
3. **Use GitLab CI/CD Variables** for pipelines
4. **Rotate tokens** every 90 days
5. **Use environment-specific** secrets

### Secret Scanning

The system automatically scans for:
- API keys (E2B, Anthropic, OpenAI)
- GitHub/GitLab tokens
- AWS credentials
- Database connection strings
- SSH private keys
- Webhook URLs

### Security Scanning

**Every PR is scanned for:**
- Code vulnerabilities (CodeQL)
- Dependency vulnerabilities (Dependabot)
- Secret leaks (Secret scanning)
- License compliance
- Code quality issues

## Cost Management

### GitHub Enterprise Trial

- **Duration**: 30 days
- **Features**: Full Enterprise + Copilot
- **Post-trial**: Auto-downgrade to Pro
- **Budget**: $500/month

### Optimization Tips

1. **Cache dependencies** (saves ~70% CI time)
2. **Use concurrency groups** (cancel old runs)
3. **Skip CI on draft PRs**
4. **Auto-cancel redundant builds**
5. **Set workflow timeouts**

### Current Usage

```bash
# Check GitHub Actions minutes
gh api /repos/appsefilepro-cell/Private-Claude/actions/billing/usage

# Check Copilot seats
gh api /orgs/Private-Claude-Enterprise/copilot/billing
```

## Troubleshooting

### Activation Issues

**Problem**: Activation script fails with API errors

**Solution**:
```bash
# Check tokens are set
echo $GITHUB_TOKEN
echo $GITLAB_TOKEN

# Verify token scopes
gh auth status
gitlab user get --token $GITLAB_TOKEN
```

### Workflow Failures

**Problem**: GitHub Actions workflow fails

**Solution**:
```bash
# Check workflow logs
gh run view --log

# Re-run failed jobs
gh run rerun <run-id> --failed
```

### Copilot Not Working

**Problem**: Copilot suggestions not appearing

**Solution**:
1. Check Copilot status: Settings → Copilot
2. Verify organization access
3. Re-authenticate: Sign out and sign in
4. Check network connection

## Advanced Configuration

### Custom Copilot Prompts

Edit `.github/copilot/copilot-config.yml`:

```yaml
custom_prompts:
  code_generation:
    - name: "Custom Generator"
      template: "Your custom template"
```

### Custom Security Patterns

Edit `config/github_enterprise_advanced.json`:

```json
{
  "custom_patterns": [
    {
      "name": "Custom Pattern",
      "pattern": "your_regex_pattern",
      "enabled": true,
      "severity": "critical"
    }
  ]
}
```

### Custom GitLab Pipeline

Edit `.gitlab-ci.yml` to add custom jobs:

```yaml
custom-job:
  stage: test
  script:
    - echo "Your custom script"
```

## Support & Resources

### Documentation

- **GitHub Enterprise**: https://docs.github.com/enterprise-cloud
- **GitHub Copilot**: https://docs.github.com/copilot
- **GitLab CI/CD**: https://docs.gitlab.com/ee/ci/
- **E2B Documentation**: https://e2b.dev/docs
- **Agent 5.0**: `docs/AGENT_5_SETUP.md`

### Contact

- **Technical Issues**: tech-support@private-claude.app
- **Billing Questions**: billing@private-claude.app
- **Security Concerns**: security@private-claude.app

## Changelog

### 2025-12-22 - Initial Setup
- ✅ GitHub Enterprise configuration
- ✅ GitHub Copilot activation
- ✅ GitLab CI/CD integration
- ✅ E2B sandbox setup
- ✅ Postman automation
- ✅ Complete workflow pipelines

## Next Steps

1. **Set up environment variables** with real tokens
2. **Run activation script** to enable live features
3. **Configure Copilot** in your IDE
4. **Create first PR** to test the workflow
5. **Deploy to staging** to verify deployment
6. **Monitor usage** and optimize costs

---

**Status**: ✅ All systems configured and ready for activation

**Last Updated**: 2025-12-22

**Maintained by**: Agent 5.0 Orchestration System
