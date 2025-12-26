# ZAPIER AI CHATBOT INTEGRATION GUIDE
## OpenAI and Anthropic Integration with Intelligent Routing

**Chatbot URL:** https://zapier.com/app/chatbots/cmj36ng540hfn0n8q8xfz8o48
**Context ID:** 25466836
**Conversation ID:** 29b727ab-5285-44d3-a1f3-10c2240b2b19
**Email:** terobinsonwy@gmail.com

---

## OVERVIEW

Configure your Zapier chatbot to intelligently route questions to the most appropriate AI provider:
- **OpenAI GPT-4:** Code generation, quick technical responses
- **Anthropic Claude:** Legal analysis, complex reasoning, long documents
- **Google Gemini:** General queries, research, FREE tier for high volume

---

## STEP 1: ADD AI PROVIDERS TO CHATBOT

### 1.1 Access Chatbot Settings

1. Go to your [Zapier Chatbot](https://zapier.com/app/chatbots/cmj36ng540hfn0n8q8xfz8o48)
2. Click **Settings** in the left sidebar
3. Navigate to **AI Providers** section

### 1.2 Add OpenAI (GPT-4)

**Provider Configuration:**
```
Provider: OpenAI
API Key: [Your OPENAI_API_KEY from .env file]
Default Model: gpt-4o-mini
Max Tokens: 4096
Temperature: 0.7
```

**Steps:**
1. Click **Add Provider** → Select **OpenAI**
2. Paste your OpenAI API key (from `/home/user/Private-Claude/.env`)
3. Configure settings:
   - **Model:** `gpt-4o-mini` (most cost-effective)
   - **Max Tokens:** `4096` (good balance)
   - **Temperature:** `0.7` (creative but focused)
4. **Save** configuration

### 1.3 Add Anthropic (Claude)

**Provider Configuration:**
```
Provider: Anthropic
API Key: [Your ANTHROPIC_API_KEY from .env file]
Default Model: claude-3-5-sonnet-20241022
Max Tokens: 8192
Temperature: 0.7
```

**Steps:**
1. Click **Add Provider** → Select **Anthropic**
2. Paste your Anthropic API key (from `/home/user/Private-Claude/.env`)
3. Configure settings:
   - **Model:** `claude-3-5-sonnet-20241022` (best balance)
   - **Max Tokens:** `8192` (handles long documents)
   - **Temperature:** `0.7` (balanced reasoning)
4. **Save** configuration

### 1.4 Add Google Gemini (Optional)

**Provider Configuration:**
```
Provider: Google Gemini
API Key: AIzaSyBqAbzJdyg7sP5tIhCddWk4Q1EEmSZSCT4
Default Model: gemini-pro
Max Tokens: 2048
Temperature: 0.7
```

**Steps:**
1. Click **Add Provider** → Select **Google AI**
2. Paste your Gemini API key (already in `.env`)
3. Configure settings:
   - **Model:** `gemini-pro`
   - **Max Tokens:** `2048`
   - **Temperature:** `0.7`
4. **Save** configuration

---

## STEP 2: CONFIGURE INTELLIGENT ROUTING

### 2.1 Set Up Routing Instructions

Go to **Settings** → **Instructions** and add this routing logic:

```markdown
# INTELLIGENT AI ROUTING SYSTEM

You are an AI router with access to three specialized AI providers:
1. **OpenAI GPT-4o-mini** - Code generation, technical questions, quick responses
2. **Anthropic Claude 3.5 Sonnet** - Legal analysis, complex reasoning, long documents
3. **Google Gemini** - General queries, research, bulk operations (FREE)

## ROUTING RULES

### Use OpenAI GPT-4o-mini for:
- Code generation and programming questions
- Technical troubleshooting and debugging
- Quick factual responses
- API documentation and examples
- Software architecture questions
- Keywords: "code", "function", "script", "debug", "API", "programming"

### Use Anthropic Claude for:
- Legal document analysis and research
- Tax preparation and financial advice
- Complex multi-step reasoning problems
- Long document summarization (>10,000 words)
- Contract review and drafting
- Case law research
- Strategic planning and decision-making
- Keywords: "legal", "tax", "contract", "case", "analyze document", "strategy"

### Use Google Gemini (FREE) for:
- General knowledge questions
- Research and web search queries
- Public records searches
- Property title lookups
- High-volume simple queries
- When budget conservation is priority
- Keywords: "research", "search", "property", "records", "general"

## ROUTING LOGIC

1. **Analyze the user's question**
2. **Identify keywords and question type**
3. **Route to appropriate provider:**
   - If code-related → OpenAI
   - If legal/complex/long → Anthropic
   - If general/research/high-volume → Gemini
4. **If provider is unavailable, fallback to Gemini (FREE)**

## EXAMPLE ROUTING

User: "Write a Python function to calculate trading profit/loss"
→ Route to: **OpenAI GPT-4o-mini** (code generation)

User: "Analyze this 50-page probate case document"
→ Route to: **Anthropic Claude** (legal, long document)

User: "Search public records for property titles in Harris County"
→ Route to: **Google Gemini** (research, public records, FREE)

User: "Explain how to file Form 1023-EZ for nonprofit status"
→ Route to: **Anthropic Claude** (legal/tax, complex process)

User: "What's the current price of Bitcoin?"
→ Route to: **Google Gemini** (quick factual, FREE)
```

### 2.2 Advanced Routing with Context

Add this to enhance routing with conversation context:

```markdown
## CONTEXT-AWARE ROUTING

If the conversation is ongoing:
- **Continue with same provider** for consistency
- **Switch providers only if question type changes dramatically**
- **Example:** User asks about legal question (Claude), then asks for code to automate it (OpenAI)

## MULTI-PROVIDER RESPONSES

For complex queries requiring multiple providers:
1. Break down the question
2. Route each component to appropriate provider
3. Synthesize responses
4. **Example:** "Analyze this contract and write code to extract key terms"
   - Part 1 (analyze contract) → Anthropic Claude
   - Part 2 (write code) → OpenAI GPT-4
```

---

## STEP 3: CREATE ROUTING WORKFLOWS IN ZAPIER

### Workflow 1: Code Generation Router

**Trigger:** Chatbot receives message with code keywords

**Steps:**
1. **Trigger:** Chatbot (New Message)
2. **Filter by Zapier:**
   - Condition: Message contains "code", "function", "script", "debug", OR "programming"
3. **Code by Zapier (Python):**
   ```python
   import os
   import openai

   openai.api_key = os.environ['OPENAI_API_KEY']

   response = openai.chat.completions.create(
       model="gpt-4o-mini",
       messages=[
           {"role": "system", "content": "You are a code generation expert."},
           {"role": "user", "content": input_data['user_message']}
       ],
       max_tokens=4096
   )

   output = {
       'response': response.choices[0].message.content,
       'provider': 'OpenAI GPT-4o-mini',
       'tokens_used': response.usage.total_tokens
   }
   ```
4. **Chatbot:** Send response
5. **Google Sheets:** Log usage for cost tracking

### Workflow 2: Legal Analysis Router

**Trigger:** Chatbot receives message with legal keywords

**Steps:**
1. **Trigger:** Chatbot (New Message)
2. **Filter by Zapier:**
   - Condition: Message contains "legal", "contract", "case", "tax", OR "analyze"
3. **Code by Zapier (Python):**
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
               "content": input_data['user_message']
           }
       ]
   )

   output = {
       'response': message.content[0].text,
       'provider': 'Anthropic Claude 3.5 Sonnet',
       'tokens_used': message.usage.input_tokens + message.usage.output_tokens
   }
   ```
4. **Chatbot:** Send response
5. **Airtable:** Log legal query for case tracking
6. **Google Sheets:** Log usage for cost tracking

### Workflow 3: General Query Router (FREE)

**Trigger:** Chatbot receives general message

**Steps:**
1. **Trigger:** Chatbot (New Message)
2. **Filter by Zapier:**
   - Condition: Message does NOT contain code or legal keywords
3. **Code by Zapier (Python):**
   ```python
   import os
   import google.generativeai as genai

   genai.configure(api_key=os.environ['GEMINI_API_KEY'])

   model = genai.GenerativeModel('gemini-pro')
   response = model.generate_content(input_data['user_message'])

   output = {
       'response': response.text,
       'provider': 'Google Gemini (FREE)',
       'cost': 0
   }
   ```
4. **Chatbot:** Send response
5. **Google Sheets:** Log usage (cost: $0)

---

## STEP 4: CHATBOT KNOWLEDGE BASE

### Add Documentation to Chatbot

Go to **Settings** → **Knowledge Base** and add these documents:

1. **API Authentication Setup Guide**
   - Upload: `/home/user/Private-Claude/config/API_AUTHENTICATION_COMPLETE_SETUP.md`
   - Purpose: Chatbot can help users set up API keys

2. **Agent 5.0 Master Prompt**
   - Upload: `/home/user/Private-Claude/AGENT_5_MASTER_PROMPT.md`
   - Purpose: Chatbot understands the full system architecture

3. **Legal Automation Guide**
   - Upload: `/home/user/Private-Claude/COMPLETE_LEGAL_AUTOMATION_SUMMARY.md`
   - Purpose: Answer questions about legal document automation

4. **Trading System Configuration**
   - Upload: `/home/user/Private-Claude/OKX_TRADING_BOT_CONFIG.json`
   - Purpose: Help with trading bot setup

### Knowledge Base Routing

The chatbot will automatically:
- Search knowledge base for relevant documents
- Use OpenAI to generate responses based on documentation
- Cite sources from uploaded documents
- Provide accurate, context-aware answers

---

## STEP 5: TEST THE INTEGRATION

### Test 1: Code Generation (OpenAI)

**User Message:** "Write a Python function to calculate compound interest"

**Expected Behavior:**
- Routes to OpenAI GPT-4o-mini
- Returns Python code
- Logs to Google Sheets

### Test 2: Legal Analysis (Anthropic)

**User Message:** "Analyze this probate case: [paste document]"

**Expected Behavior:**
- Routes to Anthropic Claude
- Provides detailed legal analysis
- Logs to Airtable + Google Sheets

### Test 3: General Query (Gemini - FREE)

**User Message:** "What are the requirements for nonprofit status?"

**Expected Behavior:**
- Routes to Google Gemini (FREE)
- Returns informative answer
- Logs to Google Sheets with $0 cost

### Test 4: Multi-Step Routing

**User Message:** "Analyze this contract and write code to extract key dates"

**Expected Behavior:**
1. First: Routes to Claude for contract analysis
2. Then: Routes to OpenAI for code generation
3. Synthesizes both responses
4. Logs both API calls

---

## STEP 6: COST TRACKING AND OPTIMIZATION

### Create Cost Tracking Sheet

**Google Sheets Template:**

| Timestamp | Question Type | Provider | Model | Tokens Used | Cost | Response Time |
|-----------|---------------|----------|-------|-------------|------|---------------|
| 2025-12-25 10:30 | Code | OpenAI | gpt-4o-mini | 1,250 | $0.0008 | 2.3s |
| 2025-12-25 10:35 | Legal | Anthropic | claude-3.5-sonnet | 12,500 | $0.225 | 5.1s |
| 2025-12-25 10:40 | Research | Gemini | gemini-pro | 800 | $0 | 1.8s |

**Auto-calculate monthly totals:**
```
=SUMIF(B:B, "OpenAI", F:F)  → OpenAI total
=SUMIF(B:B, "Anthropic", F:F)  → Anthropic total
=SUMIF(B:B, "Gemini", F:F)  → Gemini total (always $0)
```

### Set Budget Alerts

**Zapier Workflow: Daily Budget Check**

1. **Schedule by Zapier:** Every day at 9 AM
2. **Google Sheets:** Get total costs for month
3. **Filter by Zapier:**
   - If total > $120 (80% of $150 budget)
4. **Email by Zapier:** Send budget alert
5. **Slack:** Post to #budget-alerts channel

---

## STEP 7: INTEGRATION WITH AGENT 5.0

### Connect Chatbot to Agent 5.0 System

**Workflow: Chatbot → Agent 5.0 Delegation**

**Trigger:** Chatbot receives complex multi-step task

**Steps:**
1. **Chatbot:** Receives request
2. **Filter by Zapier:**
   - Condition: Message contains "automate", "agent", or "system"
3. **Webhook by Zapier:**
   - Send to: `https://hooks.zapier.com/hooks/catch/YOUR_AGENT5_HOOK/`
   - Payload:
     ```json
     {
       "task": "{{user_message}}",
       "source": "chatbot",
       "priority": "normal",
       "timestamp": "{{timestamp}}"
     }
     ```
4. **Agent 5.0 Master CFO:**
   - Receives task via webhook
   - Analyzes and delegates to appropriate division
   - 219 agents execute task
5. **Chatbot:** Receives completion notification
6. **Email by Zapier:** Send results to user

**Example:**
- User asks chatbot: "Automate the migration of all OneDrive files to Dropbox"
- Chatbot routes to Agent 5.0
- Migration Division (15 agents) + Zapier Team (10 agents) execute
- User receives completion email

---

## QUICK REFERENCE

### Add API Key to Chatbot
1. Go to [Chatbot Settings](https://zapier.com/app/chatbots/cmj36ng540hfn0n8q8xfz8o48/settings)
2. Click **AI Providers** → **Add Provider**
3. Paste API key from `.env` file
4. Configure model and settings
5. Save

### Test Chatbot Routing
```
Test Message 1: "Write a Python script to parse JSON"
Expected: OpenAI GPT-4o-mini

Test Message 2: "Review this legal contract for risks"
Expected: Anthropic Claude

Test Message 3: "Search property records in Texas"
Expected: Google Gemini (FREE)
```

### View Usage Logs
- Google Sheets: [Chatbot Usage Log](link to your sheet)
- View by provider, date, cost
- Monthly budget tracking

---

## TROUBLESHOOTING

### Problem: Chatbot not routing correctly

**Solution:**
1. Check routing instructions in Settings
2. Verify keywords are triggering filters
3. Test with explicit provider names: "Use Claude to analyze..."

### Problem: API key not working

**Solution:**
1. Verify API key in chatbot settings
2. Check key is valid on provider platform
3. Test key with simple query
4. Regenerate key if needed

### Problem: High costs

**Solution:**
1. Review usage logs in Google Sheets
2. Route more queries to Gemini (FREE)
3. Use smaller models (gpt-4o-mini, claude-haiku)
4. Implement daily budget checks

### Problem: Slow responses

**Solution:**
1. Use faster models (gpt-4o-mini, gemini-pro)
2. Reduce max_tokens to speed up generation
3. Check API rate limits
4. Implement caching for common queries

---

## NEXT STEPS

1. ✅ **Add OpenAI to chatbot** (5 minutes)
2. ✅ **Add Anthropic to chatbot** (5 minutes)
3. ✅ **Configure routing instructions** (10 minutes)
4. ✅ **Create routing workflows** (20 minutes)
5. ✅ **Upload knowledge base documents** (5 minutes)
6. ✅ **Test with sample queries** (10 minutes)
7. ✅ **Set up cost tracking** (15 minutes)
8. ✅ **Integrate with Agent 5.0** (10 minutes)

**Total Setup Time: ~80 minutes**

---

## SUPPORT

### Zapier Chatbot Help
- Documentation: https://help.zapier.com/hc/en-us/articles/8495988744461-Chatbots-for-Zapier-Interfaces
- Support: https://zapier.com/app/support

### AI Provider Support
- OpenAI: https://help.openai.com/
- Anthropic: https://support.anthropic.com/
- Google Gemini: https://ai.google.dev/docs

---

**STATUS: ✅ READY FOR CONFIGURATION**

**Chatbot URL:** https://zapier.com/app/chatbots/cmj36ng540hfn0n8q8xfz8o48

**Integration Level:** Complete (OpenAI + Anthropic + Gemini + Agent 5.0)
