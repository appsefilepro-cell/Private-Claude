# GITHUB WORKFLOWS - 5 MINUTE ACTIVATION GUIDE

**Quick Start:** Get all 11 workflows running in 5 minutes

---

## STEP 1: SET GITHUB SECRETS (3 minutes)

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"** for each secret below

### Required Secrets (Copy-Paste Ready)

```plaintext
# Secret Name: OKX_API_KEY
# Value: a5b57cd3-0bee-44f-b8e9-7c5b330a5c28

# Secret Name: OKX_SECRET_KEY
# Value: <your_okx_secret_key>

# Secret Name: OKX_PASSPHRASE
# Value: <your_okx_passphrase>

# Secret Name: E2B_API_KEY
# Value: e2b_fcc08e8c733b3eab00bdb3ad5857f5966afc2773

# Secret Name: GEMINI_API_KEY
# Value: AIzaSyBqAbzJdyg7sP5tIhCddWk4Q1EEmSZSCT4

# Secret Name: ZAPIER_WEBHOOK_URL
# Value: <your_zapier_webhook_url>

# Secret Name: SLACK_WEBHOOK_GITHUB
# Value: <your_slack_webhook_url>

# Secret Name: ANTHROPIC_API_KEY
# Value: <your_anthropic_api_key>

# Secret Name: OPENAI_API_KEY (optional)
# Value: <your_openai_api_key>

# Secret Name: POSTMAN_API_KEY (optional)
# Value: <your_postman_api_key>
```

### Optional Secrets (for advanced features)
```plaintext
# Secret Name: COPILOT_API_TOKEN
# Value: <your_github_copilot_token>
```

---

## STEP 2: TRIGGER YOUR FIRST WORKFLOW (1 minute)

### Option A: Via GitHub Web Interface (Easiest)

1. Go to **Actions** tab in your repository
2. Click on **"Run Everything - Agent 5.0 Complete System"**
3. Click **"Run workflow"** dropdown button
4. Select branch: `claude/setup-e2b-webhooks-CPFBo`
5. Click green **"Run workflow"** button
6. ✅ Watch it execute!

### Option B: Via GitHub CLI (If installed)

```bash
gh workflow run "run-everything.yml"
```

### Option C: Via Git Push (Automatic)

```bash
# Make any small change
echo "# Activated $(date)" >> ACTIVATION_LOG.txt
git add ACTIVATION_LOG.txt
git commit -m "Activate all workflows"
git push origin claude/setup-e2b-webhooks-CPFBo
```

---

## STEP 3: VERIFY WORKFLOWS ARE RUNNING (1 minute)

### Check Status

1. Go to **Actions** tab
2. You should see workflows running:
   - Green circle = Running
   - Green checkmark = Success
   - Red X = Failed (check logs)

### Expected Results

**Immediately Running:**
- ✅ Run Everything - Agent 5.0 Complete System
- ✅ Continuous Testing (if scheduled)

**Will Run on Schedule:**
- ⏰ Trading Marathon 24/7 (every 15 minutes)
- ⏰ Continuous Testing (every 15 minutes)
- ⏰ Daily Market Data (daily)

**Will Run on PR:**
- 📝 Copilot Assisted Development
- 📝 Copilot Review
- 📝 Agent 5 Automation

---

## ALL 11 WORKFLOWS EXPLAINED

### 1. **run-everything.yml** 🚀
- **Triggers:** Push, Schedule (15min), Manual
- **Purpose:** Runs all Agent 5.0 systems
- **Jobs:** Activate Agent 5.0, MT5 trading, OKX trading, reporting
- **Status:** ✅ READY

### 2. **trading-marathon-24-7.yml** 📊
- **Triggers:** Schedule (15min), Manual
- **Purpose:** 24/7 trading automation
- **Jobs:** Health check, OKX trading, MT5 monitoring, metrics
- **Status:** ✅ READY
- **Note:** Most comprehensive trading workflow

### 3. **continuous-testing.yml** 🧪
- **Triggers:** Schedule (15min), Push, Manual
- **Purpose:** System health monitoring
- **Jobs:** Smoke tests, API tests, Python tests, E2B tests
- **Status:** ✅ READY

### 4. **agent-5-automation.yml** 🤖
- **Triggers:** Push, PR, Manual
- **Purpose:** Complete automation pipeline
- **Jobs:** Copilot review, quality, docs, E2B, Postman, security, build, deploy
- **Status:** ✅ READY
- **Note:** Most comprehensive pipeline (14 jobs)

### 5. **copilot-assisted-development.yml** 🔍
- **Triggers:** PR, Push
- **Purpose:** Copilot code review and assistance
- **Jobs:** Code review, PR suggestions, quality, docs, tests, performance
- **Status:** ✅ READY

### 6. **copilot-review.yml** 📝
- **Triggers:** PR
- **Purpose:** Automated code review
- **Jobs:** Copilot review, security scan
- **Status:** ✅ READY

### 7. **daily-market-data.yml** 📈
- **Triggers:** Schedule (daily), Manual
- **Purpose:** Collect market data
- **Status:** ✅ READY

### 8. **deploy-with-copilot-e2b.yml** 🚢
- **Triggers:** Push, Manual
- **Purpose:** Deploy to E2B sandbox
- **Jobs:** E2B deployment, testing
- **Status:** ✅ READY

### 9. **github-gitlab-sync.yml** 🔄
- **Triggers:** Push
- **Purpose:** Bidirectional GitHub/GitLab sync
- **Status:** ✅ READY

### 10. **zapier-enterprise-deployment.yml** ⚡
- **Triggers:** Push, Manual
- **Purpose:** Zapier automation deployment
- **Jobs:** Zapier sync, GitLab trigger
- **Status:** ✅ READY

### 11. **auto-complete-tasks.yml** ✅
- **Triggers:** Schedule, Manual
- **Purpose:** Automated task completion
- **Status:** ✅ READY

---

## TROUBLESHOOTING

### Workflow Fails with "Secret not found"
**Solution:** Make sure you added the secret in Step 1 with the EXACT name shown above (case-sensitive)

### Workflow Stuck on "Queued"
**Solution:**
- GitHub free tier has concurrent job limits
- Wait for other workflows to complete
- Or upgrade to GitHub Pro

### Workflow Shows Yellow Warning
**Solution:**
- Yellow/warnings are OK - many steps have `continue-on-error: true`
- Check logs to see if it's just missing optional dependencies
- Workflow can still succeed with warnings

### "This workflow requires approval"
**Solution:**
- First-time workflow runs may need approval
- Go to Actions → Approve workflow run
- Future runs will be automatic

### E2B Tests Fail
**Solution:**
- E2B API key may need activation
- Check E2B_API_KEY secret is set correctly
- E2B may have usage limits on free tier

### Postman Tests Fail
**Solution:**
- If you don't have Postman API key, workflow continues anyway
- Tests marked as `continue-on-error: true`
- Not critical for system operation

---

## MONITORING YOUR WORKFLOWS

### View Workflow Runs
```
GitHub → Actions → Select workflow → Click on run number
```

### View Logs
```
Click on run → Click on job name → Expand step to see logs
```

### Download Artifacts
```
Click on run → Scroll to "Artifacts" → Download (reports, logs, etc.)
```

### Get Notifications
- Set up GitHub notifications: Settings → Notifications
- Slack webhooks will send notifications when configured
- Zapier workflows will post to Google Sheets

---

## SCHEDULED WORKFLOWS

These run automatically without any action:

| Workflow | Frequency | Next Run |
|----------|-----------|----------|
| trading-marathon-24-7.yml | Every 15 min | Continuous |
| continuous-testing.yml | Every 15 min | Continuous |
| daily-market-data.yml | Daily | Once per day |
| run-everything.yml | Every 15 min | Continuous |

**To view schedule:** Open workflow file and check `schedule:` → `cron:` section

**Cron format:**
- `*/15 * * * *` = Every 15 minutes
- `0 0 * * *` = Daily at midnight UTC

---

## MANUAL TRIGGERS

All workflows support manual triggering via:

1. **GitHub Web:**
   - Actions → Select workflow → Run workflow

2. **GitHub CLI:**
   ```bash
   gh workflow run "workflow-name.yml"
   ```

3. **GitHub API:**
   ```bash
   curl -X POST \
     -H "Authorization: token YOUR_GITHUB_TOKEN" \
     -H "Accept: application/vnd.github.v3+json" \
     https://api.github.com/repos/OWNER/REPO/actions/workflows/WORKFLOW_ID/dispatches \
     -d '{"ref":"claude/setup-e2b-webhooks-CPFBo"}'
   ```

---

## ADVANCED: WORKFLOW INPUTS

Some workflows accept inputs when manually triggered:

### trading-marathon-24-7.yml
```yaml
force_trade: boolean (force immediate trade)
test_mode: boolean (run in test mode, no real trades)
```

### agent-5-automation.yml
```yaml
deploy_environment: choice (staging | production)
run_full_tests: boolean
```

### copilot-assisted-development.yml
```yaml
review_type: choice (full | security | performance | quality)
```

**How to use:**
1. Actions → Select workflow → Run workflow
2. Fill in input fields
3. Click "Run workflow"

---

## COST & USAGE

### GitHub Actions Free Tier
- **2,000 minutes/month** for public repos
- **500 MB storage** for artifacts

### Current Usage Estimate
- **Each workflow run:** 2-10 minutes
- **Scheduled workflows:** ~15 min × 96 runs/day = 1,440 min/day
- **Monthly:** ~43,200 minutes

**⚠️ WARNING:** You'll exceed free tier with all scheduled workflows running continuously

**Solutions:**
1. Reduce schedule frequency (e.g., hourly instead of every 15 min)
2. Disable some scheduled workflows
3. Upgrade to GitHub Pro ($4/month for 3,000 minutes)
4. Use self-hosted runners (FREE unlimited)

### Optimizing Usage

**Option 1: Reduce Schedule Frequency**
Edit workflow files and change:
```yaml
# Before
- cron: '*/15 * * * *'  # Every 15 minutes

# After
- cron: '0 * * * *'     # Every hour (saves 75% of runs)
# or
- cron: '0 */6 * * *'   # Every 6 hours (saves 96% of runs)
```

**Option 2: Disable Non-Critical Scheduled Workflows**
Comment out or remove `schedule:` sections in:
- `daily-market-data.yml` (run manually when needed)
- `run-everything.yml` (keep manual trigger only)

**Option 3: Self-Hosted Runner**
```bash
# Set up on your own server (FREE unlimited minutes)
# Follow: https://docs.github.com/en/actions/hosting-your-own-runners
```

---

## QUICK REFERENCE

### Most Important Workflows to Run First

1. **run-everything.yml** - Comprehensive system test
2. **continuous-testing.yml** - Health monitoring
3. **agent-5-automation.yml** - Full automation pipeline

### Workflows That Need Secrets

| Workflow | Required Secrets |
|----------|-----------------|
| trading-marathon-24-7.yml | OKX_*, ZAPIER_WEBHOOK_URL, SLACK_WEBHOOK |
| agent-5-automation.yml | E2B_API_KEY, ANTHROPIC_API_KEY, POSTMAN_API_KEY |
| All workflows | ZAPIER_WEBHOOK_URL (for notifications) |

### Workflows Safe to Run Without Secrets

- continuous-testing.yml (most tests have fallbacks)
- copilot-assisted-development.yml (uses GITHUB_TOKEN)
- github-gitlab-sync.yml (uses GITHUB_TOKEN)

---

## SUCCESS CHECKLIST

- [ ] All secrets added to GitHub repository
- [ ] At least one workflow successfully run
- [ ] Workflow logs reviewed (no critical errors)
- [ ] Artifacts downloaded (if any)
- [ ] Slack/Zapier webhooks configured (optional)
- [ ] Scheduled workflows showing in Actions tab
- [ ] Understanding of which workflows run automatically vs. manually

---

## NEXT STEPS

After workflows are running:

1. **Build Zapier Automations** - See `config/ZAPIER_COPILOT_COMPLETE_DELEGATION.json`
2. **Test Robinhood Integration** - See `cfo-suite/robinhood_cfo_integration.py`
3. **Monitor Results** - Check Google Sheets dashboards (once Zapier connected)
4. **Launch Fiverr Gigs** - Start generating revenue
5. **Expand System** - Add more agents, workflows, integrations

---

**Generated by:** GitLab Duo Business Copilot
**Date:** 2025-12-26
**Time to Activate:** 5 minutes
**System Status After Activation:** FULLY OPERATIONAL ✅
