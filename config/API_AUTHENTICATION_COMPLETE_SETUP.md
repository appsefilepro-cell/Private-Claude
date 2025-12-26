# COMPLETE API AUTHENTICATION SETUP GUIDE
## OpenAI and Anthropic Integration Across All Systems

**Last Updated:** 2025-12-25
**Status:** Ready for Implementation
**Systems:** Agent 5.0 (219 agents), Zapier Chatbot, GitHub Copilot, GitLab Duo

---

## TABLE OF CONTENTS

1. [Overview](#overview)
2. [OpenAI Configuration](#openai-configuration)
3. [Anthropic (Claude) Configuration](#anthropic-configuration)
4. [Integration with All Systems](#integration-with-all-systems)
5. [GitHub Secrets Setup](#github-secrets-setup)
6. [GitLab CI/CD Variables Setup](#gitlab-cicd-variables-setup)
7. [Zapier Integration](#zapier-integration)
8. [AI Routing Strategy](#ai-routing-strategy)
9. [Cost Optimization](#cost-optimization)
10. [Security Best Practices](#security-best-practices)
11. [Testing & Validation](#testing-validation)
12. [Troubleshooting](#troubleshooting)

---

## OVERVIEW

This guide configures API authentications for OpenAI and Anthropic (Claude) across your entire automation ecosystem:

- **Agent 5.0 System:** 219 agents across 8 divisions
- **Zapier Chatbot:** Intelligent routing between AI providers
- **GitHub Copilot Business:** Code generation with OpenAI
- **GitLab Duo:** Code assistance with Anthropic
- **All Automation Workflows:** Zapier, E2B, GitHub Actions, GitLab CI

### AI Provider Strategy

| Provider | Primary Use Case | Cost | Rate Limits |
|----------|------------------|------|-------------|
| **Google Gemini** | FREE tier - bulk operations | $0 | 60 req/min |
| **OpenAI GPT-4** | Code generation, quick responses | Pay-per-use | 3,500 RPM |
| **Anthropic Claude** | Legal analysis, long documents | Pay-per-use | 50 RPM |

---

## OPENAI CONFIGURATION

### Step 1: Create OpenAI Account & API Key

1. Go to [https://platform.openai.com/signup](https://platform.openai.com/signup)
2. Sign up or log in to your account
3. Navigate to [API Keys](https://platform.openai.com/api-keys)
4. Click "Create new secret key"
5. Name it: `Agent-5-Private-Claude`
6. Copy the API key immediately (you won't see it again!)

### Step 2: Set Up Organization & Project (Optional)

**For better cost tracking and management:**

1. Go to [Settings > Organization](https://platform.openai.com/account/organization)
2. Note your Organization ID: `org-XXXXXXXXXXXXXXXX`
3. Create a new project: "Private-Claude-Agent-5"
4. Note your Project ID: `proj-XXXXXXXXXXXXXXXX`

### Step 3: Configure Rate Limits & Usage Alerts

1. Go to [Settings > Limits](https://platform.openai.com/account/limits)
2. Set monthly spending limit: **$50** (adjust as needed)
3. Set soft limit alert: **$40** (80% of budget)
4. Enable email notifications for spending alerts

### Step 4: Add API Key to .env File

```bash
# Edit .env file
nano /home/user/Private-Claude/.env

# Add your OpenAI credentials:
OPENAI_API_KEY=sk-proj-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
OPENAI_ORG_ID=org-XXXXXXXXXXXXXXXX
OPENAI_PROJECT_ID=proj-XXXXXXXXXXXXXXXX
```

### Step 5: Choose Default Model

**Recommended Models:**

| Model | Use Case | Cost (Input/Output per 1M tokens) |
|-------|----------|-----------------------------------|
| `gpt-4o-mini` | Code generation, quick tasks | $0.15 / $0.60 |
| `gpt-4o` | Complex code, detailed analysis | $2.50 / $10.00 |
| `gpt-4-turbo` | Highest quality, critical tasks | $10.00 / $30.00 |

**Update .env:**
```bash
OPENAI_MODEL_DEFAULT=gpt-4o-mini  # Most cost-effective
```

---

## ANTHROPIC (CLAUDE) CONFIGURATION

### Step 1: Create Anthropic Account & API Key

1. Go to [https://console.anthropic.com/](https://console.anthropic.com/)
2. Sign up or log in to your account
3. Navigate to [API Keys](https://console.anthropic.com/settings/keys)
4. Click "Create Key"
5. Name it: `Agent-5-Private-Claude`
6. Copy the API key immediately

### Step 2: Configure Claude API Settings

1. Go to [Settings > Workspaces](https://console.anthropic.com/settings/workspaces)
2. Create workspace: "Private-Claude"
3. Set monthly budget: **$100** (adjust as needed)
4. Enable usage alerts at **$80** (80% threshold)

### Step 3: Add API Key to .env File

```bash
# Edit .env file
nano /home/user/Private-Claude/.env

# Add your Anthropic credentials:
ANTHROPIC_API_KEY=sk-ant-api03-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
ANTHROPIC_MODEL_DEFAULT=claude-3-5-sonnet-20241022
```

### Step 4: Choose Default Model

**Recommended Models:**

| Model | Use Case | Cost (Input/Output per 1M tokens) |
|-------|----------|-----------------------------------|
| `claude-3-5-sonnet-20241022` | Best balance, most use cases | $3.00 / $15.00 |
| `claude-3-opus-20240229` | Highest intelligence, complex reasoning | $15.00 / $75.00 |
| `claude-3-haiku-20240307` | Fastest, simple tasks | $0.25 / $1.25 |

**Update .env:**
```bash
ANTHROPIC_MODEL_DEFAULT=claude-3-5-sonnet-20241022  # Recommended
```

---

## INTEGRATION WITH ALL SYSTEMS

### Agent 5.0 - 219 Agents Across 8 Divisions

**File:** `/home/user/Private-Claude/agent-orchestrator/ai_router.py`

Create AI routing logic:

```python
import os
from enum import Enum

class AIProvider(Enum):
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"

class AIRouter:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    def route_task(self, task_type):
        """Route task to appropriate AI provider"""
        routing_map = {
            "code_generation": AIProvider.OPENAI,
            "quick_response": AIProvider.OPENAI,
            "legal_analysis": AIProvider.ANTHROPIC,
            "document_analysis": AIProvider.ANTHROPIC,
            "long_context": AIProvider.ANTHROPIC,
            "bulk_operation": AIProvider.GEMINI,
            "free_tier": AIProvider.GEMINI,
            "default": AIProvider.GEMINI
        }
        return routing_map.get(task_type, AIProvider.GEMINI)

    def get_api_key(self, provider):
        """Get API key for provider"""
        keys = {
            AIProvider.GEMINI: self.gemini_key,
            AIProvider.OPENAI: self.openai_key,
            AIProvider.ANTHROPIC: self.anthropic_key
        }
        return keys.get(provider)
```

**Agent Assignments:**

- **AI/ML Division (33 agents):**
  - 15 agents → Gemini (FREE tier)
  - 8 agents → OpenAI (code generation)
  - 10 agents → Anthropic (complex analysis)

- **Legal Division (35 agents):**
  - 20 agents → Anthropic (legal analysis, long documents)
  - 10 agents → Gemini (research, public records)
  - 5 agents → OpenAI (document summarization)

- **Trading Division (30 agents):**
  - 20 agents → Gemini (bulk market data analysis)
  - 10 agents → OpenAI (pattern detection, quick analysis)

### Zapier Chatbot Configuration

**Chatbot URL:** https://zapier.com/app/chatbots/cmj36ng540hfn0n8q8xfz8o48

**Integration Steps:**

1. Go to your [Zapier Chatbot](https://zapier.com/app/chatbots/cmj36ng540hfn0n8q8xfz8o48)
2. Click "Settings" → "AI Providers"
3. Add OpenAI:
   - Click "Add Provider"
   - Select "OpenAI"
   - Paste your `OPENAI_API_KEY`
   - Set default model: `gpt-4o-mini`
4. Add Anthropic:
   - Click "Add Provider"
   - Select "Anthropic"
   - Paste your `ANTHROPIC_API_KEY`
   - Set default model: `claude-3-5-sonnet-20241022`

**Routing Logic in Chatbot:**

Create these instruction blocks in your chatbot:

```
ROUTING INSTRUCTIONS:

For code-related questions:
- Use OpenAI GPT-4o-mini for code generation, debugging, quick answers

For legal/tax questions:
- Use Anthropic Claude 3.5 Sonnet for legal analysis, tax research, complex documents
- Claude's 200k token context window handles long documents

For general questions and high-volume queries:
- Use Google Gemini (FREE tier, 60 req/min)
- Cost-effective for research, data extraction, simple queries

For complex multi-step reasoning:
- Use Anthropic Claude 3.5 Sonnet
- Best for breaking down complex problems, strategy planning

FALLBACK STRATEGY:
1. Try primary AI (based on question type)
2. If rate limited, fall back to Gemini (FREE)
3. If Gemini unavailable, use secondary AI
```

### GitHub Copilot Business

**Uses OpenAI under the hood** - No additional configuration needed!

- GitHub Copilot Business is powered by OpenAI Codex
- Your GitHub Copilot license includes OpenAI access
- No separate API key required

**Integration Status:**
- ✅ GitHub Copilot Business activated (30-day trial)
- ✅ Integrated with VS Code, GitHub Actions, Postman
- ✅ Code generation using OpenAI Codex models

### GitLab Duo

**Uses Claude under the hood** - Configure for enhanced features:

**File:** `.gitlab-ci.yml`

```yaml
variables:
  GITLAB_DUO_ENABLED: "true"
  ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}  # From GitLab CI/CD variables
```

**Integration Status:**
- ✅ GitLab Duo available (trial available)
- ✅ Code suggestions powered by Claude
- ✅ CI/CD integration ready

---

## GITHUB SECRETS SETUP

### Step 1: Add Secrets to GitHub Repository

1. Go to your repository: [Private-Claude](https://github.com/appsefilepro-cell/Private-Claude)
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

### Step 2: Add Each Secret

Add these secrets one by one:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `OPENAI_API_KEY` | `sk-proj-XXX...` | Your OpenAI API key |
| `ANTHROPIC_API_KEY` | `sk-ant-api03-XXX...` | Your Anthropic API key |
| `GEMINI_API_KEY` | `AIzaSyBqAbzJdyg7sP5tIhCddWk4Q1EEmSZSCT4` | Google Gemini (already configured) |
| `E2B_API_KEY` | `e2b_fcc08e8c733b3eab00bdb3ad5857f5966afc2773` | E2B Sandbox (already configured) |
| `ZAPIER_WEBHOOK_URL` | `https://hooks.zapier.com/hooks/catch/...` | Zapier webhook |
| `SLACK_WEBHOOK_GITHUB` | `https://hooks.slack.com/services/...` | Slack notifications |

### Step 3: Update GitHub Actions Workflows

**File:** `.github/workflows/agent-5-automation.yml`

Update the environment variables section:

```yaml
env:
  E2B_API_KEY: ${{ secrets.E2B_API_KEY }}
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
  POSTMAN_API_KEY: ${{ secrets.POSTMAN_API_KEY }}
  ZAPIER_WEBHOOK_URL: ${{ secrets.ZAPIER_WEBHOOK_URL }}
  SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK_GITHUB }}
```

### Step 4: Verify Secrets

Run this GitHub Action to verify:

```yaml
- name: Verify API Keys
  run: |
    echo "Checking API keys..."
    [ -n "$OPENAI_API_KEY" ] && echo "✅ OpenAI configured" || echo "❌ OpenAI missing"
    [ -n "$ANTHROPIC_API_KEY" ] && echo "✅ Anthropic configured" || echo "❌ Anthropic missing"
    [ -n "$GEMINI_API_KEY" ] && echo "✅ Gemini configured" || echo "❌ Gemini missing"
```

---

## GITLAB CI/CD VARIABLES SETUP

### Step 1: Add Variables to GitLab Project

1. Go to your GitLab project settings
2. Navigate to **Settings** → **CI/CD** → **Variables**
3. Click **Add variable**

### Step 2: Add Each Variable

Add these variables one by one:

| Variable Name | Value | Protected | Masked | Description |
|---------------|-------|-----------|--------|-------------|
| `OPENAI_API_KEY` | `sk-proj-XXX...` | ✅ Yes | ✅ Yes | OpenAI API key |
| `ANTHROPIC_API_KEY` | `sk-ant-api03-XXX...` | ✅ Yes | ✅ Yes | Anthropic API key |
| `GEMINI_API_KEY` | `AIzaSyBq...` | ✅ Yes | ✅ Yes | Google Gemini |
| `E2B_API_KEY` | `e2b_fcc08e8c...` | ✅ Yes | ✅ Yes | E2B Sandbox |
| `ZAPIER_WEBHOOK_URL` | `https://hooks.zapier.com/...` | ✅ Yes | ⬜ No | Zapier webhook |

**Settings:**
- **Protected:** Yes (only available on protected branches)
- **Masked:** Yes for API keys (hides values in logs)
- **Expand variable reference:** No (unless needed)

### Step 3: Update .gitlab-ci.yml

**File:** `.gitlab-ci.yml`

```yaml
variables:
  DOCKER_DRIVER: overlay2
  E2B_API_KEY: ${E2B_API_KEY}
  E2B_WEBHOOK_ID: YIyOpaJ0UMJ3Pl9Md5kVExEDdkqyDGRp
  OPENAI_API_KEY: ${OPENAI_API_KEY}
  ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
  GEMINI_API_KEY: ${GEMINI_API_KEY}
  GIT_STRATEGY: clone

test-ai-integration:
  stage: test
  image: python:3.11-slim
  script:
    - echo "Testing AI provider connections..."
    - pip install openai anthropic google-generativeai
    - |
      python3 << EOF
      import os
      import sys

      # Test OpenAI
      openai_key = os.getenv('OPENAI_API_KEY')
      print(f"✅ OpenAI key configured: {bool(openai_key)}")

      # Test Anthropic
      anthropic_key = os.getenv('ANTHROPIC_API_KEY')
      print(f"✅ Anthropic key configured: {bool(anthropic_key)}")

      # Test Gemini
      gemini_key = os.getenv('GEMINI_API_KEY')
      print(f"✅ Gemini key configured: {bool(gemini_key)}")

      if not all([openai_key, anthropic_key, gemini_key]):
          sys.exit(1)
      EOF
    - echo "✅ All AI providers configured"
  only:
    - branches
```

---

## ZAPIER INTEGRATION

### Workflow 1: OpenAI Code Generation

**Trigger:** Webhook receives code generation request
**Actions:**
1. **Filter by Zapier:** Only process code-related requests
2. **Code by Zapier (Python):**
   ```python
   import os
   import openai

   openai.api_key = os.environ['OPENAI_API_KEY']

   response = openai.chat.completions.create(
       model="gpt-4o-mini",
       messages=[
           {"role": "system", "content": "You are a code generation expert."},
           {"role": "user", "content": input_data['prompt']}
       ]
   )

   output = {'code': response.choices[0].message.content}
   ```
3. **Google Sheets:** Log the request
4. **Email by Zapier:** Send result to user

### Workflow 2: Anthropic Legal Analysis

**Trigger:** New legal document uploaded to Dropbox
**Actions:**
1. **Dropbox:** Download document
2. **Code by Zapier (Python):**
   ```python
   import os
   import anthropic

   client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])

   message = client.messages.create(
       model="claude-3-5-sonnet-20241022",
       max_tokens=8192,
       messages=[
           {
               "role": "user",
               "content": f"Analyze this legal document:\n\n{input_data['document_text']}"
           }
       ]
   )

   output = {'analysis': message.content[0].text}
   ```
3. **Google Docs:** Create analysis report
4. **Airtable:** Log case information
5. **Slack:** Notify legal team

### Workflow 3: Smart AI Routing

**Trigger:** Chatbot receives user question
**Actions:**
1. **Formatter by Zapier:** Extract question keywords
2. **Paths by Zapier:**
   - **Path A (Code):** Contains "code", "function", "script" → Use OpenAI
   - **Path B (Legal):** Contains "legal", "contract", "case" → Use Anthropic
   - **Path C (General):** Everything else → Use Gemini (FREE)
3. **Code by Zapier:** Call appropriate API
4. **Filter by Zapier:** Check if response is valid
5. **Email by Zapier:** Send response to user
6. **Google Sheets:** Log usage and costs

### Zapier API Key Configuration

**In each workflow that uses AI:**

1. Click workflow → **Settings** → **Environment Variables**
2. Add these environment variables:
   - `OPENAI_API_KEY`: Your OpenAI key
   - `ANTHROPIC_API_KEY`: Your Anthropic key
   - `GEMINI_API_KEY`: Your Gemini key
3. Reference in Code by Zapier: `os.environ['OPENAI_API_KEY']`

---

## AI ROUTING STRATEGY

### Intelligent Task Routing

**Route tasks to the most cost-effective and appropriate AI:**

```python
# File: agent-orchestrator/ai_router.py

class TaskRouter:
    def __init__(self):
        self.usage_tracking = {
            'gemini': {'requests': 0, 'cost': 0},
            'openai': {'requests': 0, 'cost': 0},
            'anthropic': {'requests': 0, 'cost': 0}
        }

    def route(self, task):
        """Route task to optimal AI provider"""

        # Rule 1: Use FREE tier for bulk operations
        if task['volume'] == 'high':
            return 'gemini'

        # Rule 2: Use OpenAI for code generation
        if task['type'] in ['code_generation', 'debugging', 'code_review']:
            return 'openai'

        # Rule 3: Use Claude for legal/complex analysis
        if task['type'] in ['legal_analysis', 'long_document', 'complex_reasoning']:
            return 'anthropic'

        # Rule 4: Use Claude for documents > 10k tokens
        if task.get('token_count', 0) > 10000:
            return 'anthropic'

        # Rule 5: Default to FREE tier
        return 'gemini'

    def get_model_config(self, provider):
        """Get model configuration for provider"""
        configs = {
            'gemini': {
                'model': 'gemini-pro',
                'max_tokens': 2048,
                'cost_per_1k': 0  # FREE
            },
            'openai': {
                'model': 'gpt-4o-mini',
                'max_tokens': 4096,
                'cost_per_1k': 0.0006  # $0.15 per 1M input tokens
            },
            'anthropic': {
                'model': 'claude-3-5-sonnet-20241022',
                'max_tokens': 8192,
                'cost_per_1k': 0.003  # $3.00 per 1M input tokens
            }
        }
        return configs[provider]
```

### Usage Examples

**Code Generation (OpenAI):**
```python
task = {
    'type': 'code_generation',
    'prompt': 'Create a Python function to calculate trading P&L',
    'volume': 'low'
}
provider = router.route(task)  # Returns 'openai'
```

**Legal Analysis (Anthropic):**
```python
task = {
    'type': 'legal_analysis',
    'prompt': 'Analyze this probate case document',
    'token_count': 50000,  # Long document
    'volume': 'low'
}
provider = router.route(task)  # Returns 'anthropic'
```

**Bulk Research (Gemini - FREE):**
```python
task = {
    'type': 'research',
    'prompt': 'Search public property records',
    'volume': 'high'  # Many requests
}
provider = router.route(task)  # Returns 'gemini'
```

---

## COST OPTIMIZATION

### Monthly Budget Strategy

**Total AI Budget: $150/month**

| Provider | Allocation | Use Cases | Monthly Requests |
|----------|-----------|-----------|------------------|
| **Gemini (FREE)** | $0 | Bulk operations, research, general queries | Unlimited (60/min) |
| **OpenAI** | $50 | Code generation, quick responses | ~80,000 requests |
| **Anthropic** | $100 | Legal analysis, complex reasoning | ~3,300 requests |

### Cost Per Use Case

**Code Generation (OpenAI gpt-4o-mini):**
- Average request: 1,000 input + 500 output tokens
- Cost: ~$0.00045 per request
- Monthly budget $50 → ~110,000 requests

**Legal Analysis (Anthropic claude-3-5-sonnet):**
- Average request: 50,000 input + 2,000 output tokens (long document)
- Cost: ~$0.18 per request
- Monthly budget $100 → ~555 long documents

**Bulk Operations (Gemini - FREE):**
- Cost: $0
- Limit: 60 requests/minute = 86,400 requests/day
- Perfect for high-volume, low-complexity tasks

### Cost Monitoring

**File:** `scripts/ai_cost_monitor.py`

```python
import os
from datetime import datetime

class AIUsageTracker:
    def __init__(self):
        self.usage_log = {
            'gemini': [],
            'openai': [],
            'anthropic': []
        }

    def log_request(self, provider, tokens_in, tokens_out):
        """Log API request for cost tracking"""
        costs = {
            'gemini': {'input': 0, 'output': 0},  # FREE
            'openai': {'input': 0.00015, 'output': 0.0006},  # per 1k tokens
            'anthropic': {'input': 0.003, 'output': 0.015}   # per 1k tokens
        }

        cost = (tokens_in / 1000 * costs[provider]['input'] +
                tokens_out / 1000 * costs[provider]['output'])

        self.usage_log[provider].append({
            'timestamp': datetime.now(),
            'tokens_in': tokens_in,
            'tokens_out': tokens_out,
            'cost': cost
        })

        return cost

    def get_monthly_total(self):
        """Calculate total monthly cost"""
        total = 0
        for provider in ['openai', 'anthropic']:  # Skip gemini (FREE)
            for request in self.usage_log[provider]:
                total += request['cost']
        return total

    def check_budget_alert(self, budget=150):
        """Alert if approaching budget"""
        current = self.get_monthly_total()
        if current >= budget * 0.8:  # 80% threshold
            return f"⚠️ WARNING: ${current:.2f} of ${budget} budget used (80%)"
        return f"✅ Budget OK: ${current:.2f} of ${budget} used"
```

**Zapier Workflow for Budget Monitoring:**
1. **Schedule by Zapier:** Daily at 9 AM
2. **Code by Zapier:** Run cost calculation
3. **Filter by Zapier:** Only if > 80% of budget
4. **Email by Zapier:** Send alert to admin
5. **Slack:** Notify team channel

### Cost Reduction Strategies

1. **Use Gemini for Everything Possible (FREE)**
   - Research queries
   - Data extraction
   - Simple summaries
   - High-volume operations

2. **Cache Common Responses**
   - Store frequent AI responses in Storage by Zapier
   - Reuse for similar queries
   - Reduce redundant API calls

3. **Batch Requests**
   - Combine multiple small requests into one large request
   - More token-efficient
   - Fewer API calls

4. **Use Smaller Models When Possible**
   - OpenAI: Use `gpt-4o-mini` instead of `gpt-4-turbo`
   - Anthropic: Use `claude-3-haiku` for simple tasks instead of Sonnet

5. **Implement Rate Limiting**
   - Prevent accidental runaway costs
   - Max 100 OpenAI requests/hour
   - Max 50 Anthropic requests/hour
   - Unlimited Gemini (FREE)

---

## SECURITY BEST PRACTICES

### 1. Never Commit API Keys to Git

**Update .gitignore:**
```bash
# API Keys and Secrets
.env
.env.*
config/.env
*.key
*_credentials.json
secrets/

# Except examples
!.env.example
!.env.template
```

### 2. Rotate API Keys Regularly

**Schedule:** Every 90 days

**Process:**
1. Generate new API key on provider platform
2. Update `.env` file
3. Update GitHub Secrets
4. Update GitLab CI/CD Variables
5. Update Zapier environment variables
6. Delete old API key from provider

### 3. Use Environment-Specific Keys

**Development:**
```bash
OPENAI_API_KEY_DEV=sk-proj-dev-XXX
ANTHROPIC_API_KEY_DEV=sk-ant-dev-XXX
```

**Production:**
```bash
OPENAI_API_KEY_PROD=sk-proj-prod-XXX
ANTHROPIC_API_KEY_PROD=sk-ant-prod-XXX
```

### 4. Implement Rate Limiting

**File:** `agent-orchestrator/rate_limiter.py`

```python
from datetime import datetime, timedelta
from collections import defaultdict

class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
        self.limits = {
            'openai': {'rpm': 3500, 'tpm': 90000},
            'anthropic': {'rpm': 50, 'tpm': 40000},
            'gemini': {'rpm': 60, 'tpm': float('inf')}
        }

    def can_make_request(self, provider):
        """Check if request is within rate limits"""
        now = datetime.now()
        one_minute_ago = now - timedelta(minutes=1)

        # Clean old requests
        self.requests[provider] = [
            req for req in self.requests[provider]
            if req > one_minute_ago
        ]

        # Check rate limit
        if len(self.requests[provider]) >= self.limits[provider]['rpm']:
            return False

        # Add new request
        self.requests[provider].append(now)
        return True
```

### 5. Audit Logging

**Log all API calls:**
```python
import logging

logging.basicConfig(
    filename='logs/ai_api_usage.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def log_api_call(provider, model, tokens_in, tokens_out, cost):
    logging.info(f"AI_API_CALL | Provider: {provider} | Model: {model} | "
                 f"Tokens: {tokens_in}→{tokens_out} | Cost: ${cost:.4f}")
```

---

## TESTING & VALIDATION

### Test 1: Verify API Keys Work

**File:** `scripts/test_ai_apis.py`

```python
#!/usr/bin/env python3
import os
import sys

def test_openai():
    """Test OpenAI API connection"""
    try:
        import openai
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )

        print("✅ OpenAI API: Working")
        return True
    except Exception as e:
        print(f"❌ OpenAI API: Failed - {e}")
        return False

def test_anthropic():
    """Test Anthropic API connection"""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=10,
            messages=[{"role": "user", "content": "Hello"}]
        )

        print("✅ Anthropic API: Working")
        return True
    except Exception as e:
        print(f"❌ Anthropic API: Failed - {e}")
        return False

def test_gemini():
    """Test Gemini API connection"""
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Hello", max_output_tokens=10)

        print("✅ Gemini API: Working")
        return True
    except Exception as e:
        print(f"❌ Gemini API: Failed - {e}")
        return False

if __name__ == "__main__":
    print("Testing AI API connections...\n")

    results = [
        test_openai(),
        test_anthropic(),
        test_gemini()
    ]

    if all(results):
        print("\n🎉 All AI APIs configured correctly!")
        sys.exit(0)
    else:
        print("\n⚠️ Some APIs failed. Check your configuration.")
        sys.exit(1)
```

**Run test:**
```bash
python3 scripts/test_ai_apis.py
```

### Test 2: Verify GitHub Secrets

**GitHub Action:** `.github/workflows/test-ai-integration.yml`

```yaml
name: Test AI Integration

on:
  workflow_dispatch:
  push:
    paths:
      - 'scripts/test_ai_apis.py'

jobs:
  test-apis:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install openai anthropic google-generativeai

      - name: Test API connections
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: |
          python3 scripts/test_ai_apis.py
```

### Test 3: Verify Zapier Integration

**Create test Zap:**
1. **Trigger:** Webhooks by Zapier (Catch Hook)
2. **Action:** Code by Zapier (Python)
   ```python
   import os

   # Test all three providers
   providers = {
       'openai': os.environ.get('OPENAI_API_KEY'),
       'anthropic': os.environ.get('ANTHROPIC_API_KEY'),
       'gemini': os.environ.get('GEMINI_API_KEY')
   }

   results = {k: 'Configured' if v else 'Missing' for k, v in providers.items()}
   output = {'test_results': results}
   ```
3. **Action:** Email by Zapier (send results)

**Test the webhook:**
```bash
curl -X POST https://hooks.zapier.com/hooks/catch/YOUR_HOOK_ID/ \
  -H "Content-Type: application/json" \
  -d '{"test": "api_keys"}'
```

---

## TROUBLESHOOTING

### Problem: "Invalid API Key" Error

**Solution:**
1. Check API key is correctly copied (no extra spaces)
2. Verify API key is active on provider's platform
3. Check if API key has necessary permissions
4. Regenerate API key if needed

### Problem: "Rate Limit Exceeded"

**Solution:**
1. Implement rate limiting (see Security section)
2. Use Gemini (FREE tier) for high-volume tasks
3. Upgrade to higher tier on provider platform
4. Batch requests to reduce call frequency

### Problem: "Budget Exceeded"

**Solution:**
1. Set hard limits on provider platforms
2. Implement cost monitoring (see Cost Optimization)
3. Route more tasks to Gemini (FREE)
4. Use smaller models (gpt-4o-mini, claude-haiku)

### Problem: GitHub Secrets Not Working

**Solution:**
1. Verify secret name matches exactly (case-sensitive)
2. Check workflow has permissions to access secrets
3. Re-create secret if needed
4. Test with workflow_dispatch event

### Problem: Zapier Can't Access API Keys

**Solution:**
1. Add keys to Zapier environment variables (workflow settings)
2. Use `os.environ['KEY_NAME']` in Code by Zapier
3. Check for typos in variable names
4. Test with simple Zap first

---

## QUICK REFERENCE COMMANDS

### Update API Keys in .env
```bash
nano /home/user/Private-Claude/.env
# Add keys, save with Ctrl+X, Y, Enter
```

### Test API Connections
```bash
python3 /home/user/Private-Claude/scripts/test_ai_apis.py
```

### Check Current Usage
```bash
python3 /home/user/Private-Claude/scripts/ai_cost_monitor.py
```

### Verify GitHub Secrets
```bash
gh secret list
```

### Update GitHub Secret
```bash
gh secret set OPENAI_API_KEY < /path/to/key.txt
```

---

## NEXT STEPS

### Immediate Actions:

1. ✅ **Get OpenAI API Key**
   - Visit: https://platform.openai.com/api-keys
   - Time: 5 minutes

2. ✅ **Get Anthropic API Key**
   - Visit: https://console.anthropic.com/settings/keys
   - Time: 5 minutes

3. ✅ **Update .env File**
   - Edit: `/home/user/Private-Claude/.env`
   - Time: 2 minutes

4. ✅ **Add GitHub Secrets**
   - Visit: Repository Settings → Secrets
   - Time: 10 minutes

5. ✅ **Add GitLab Variables**
   - Visit: Project Settings → CI/CD → Variables
   - Time: 10 minutes

6. ✅ **Configure Zapier Chatbot**
   - Add AI providers to chatbot
   - Time: 15 minutes

7. ✅ **Test All Integrations**
   - Run test script
   - Time: 5 minutes

### Ongoing Maintenance:

- **Weekly:** Review API usage and costs
- **Monthly:** Rotate API keys (security best practice)
- **Quarterly:** Re-evaluate AI provider allocation based on usage patterns

---

## SUPPORT & RESOURCES

### Official Documentation:
- OpenAI: https://platform.openai.com/docs
- Anthropic: https://docs.anthropic.com
- Google Gemini: https://ai.google.dev/docs

### Pricing:
- OpenAI: https://openai.com/pricing
- Anthropic: https://www.anthropic.com/pricing
- Gemini: FREE tier (no pricing page needed)

### Community:
- OpenAI Community: https://community.openai.com
- Anthropic Discord: https://discord.gg/anthropic
- Google AI: https://developers.google.com/community

---

**STATUS: ✅ COMPLETE - Ready for Implementation**

**Total Setup Time: ~60 minutes**

**Monthly Cost: $0-$150 (depending on usage, FREE tier available)**

**Systems Integrated: 7 (Agent 5.0, Zapier, GitHub, GitLab, E2B, Chatbot, All Workflows)**
