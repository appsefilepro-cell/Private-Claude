# AgentX5 Postman API Collection

Complete API testing collection for Agent 5.0 with 50+ endpoints across all systems.

## 📦 What's Included

- **Complete Collection:** 50+ API endpoints organized by system
- **3 Environments:** Local, Staging, Production
- **Auto-authentication:** Token refresh handled automatically
- **Global Tests:** Response time and status code validation
- **Pre-request Scripts:** Auto token management

---

## 🚀 Quick Start

### 1. Import Collection into Postman

**Option A: Import from File**
```bash
# In Postman:
# 1. Click "Import" button
# 2. Select "File" tab
# 3. Choose: AgentX5.postman_collection.json
# 4. Click "Import"
```

**Option B: Import via URL (if hosted)**
```
https://raw.githubusercontent.com/your-repo/postman/AgentX5.postman_collection.json
```

### 2. Import Environments

Import all 3 environment files:
- `local.postman_environment.json` - For localhost:8000 testing
- `staging.postman_environment.json` - For Railway staging
- `production.postman_environment.json` - For Railway production

### 3. Select Environment

In Postman top-right corner:
- Select "AgentX5 - Local Development" for local testing
- Select "AgentX5 - Staging" for staging tests
- Select "AgentX5 - Production" for production (CAREFUL!)

### 4. Authenticate

**Run these requests in order:**

1. **Register User** (if new user)
   - Folder: `Authentication`
   - Request: `Register User`
   - Updates email/password in body
   - Click "Send"

2. **Login**
   - Folder: `Authentication`
   - Request: `Login`
   - This will auto-save `access_token` and `refresh_token` to environment
   - Click "Send"

3. **Test Authentication**
   - Folder: `Authentication`
   - Request: `Get Current User`
   - Should return your user profile
   - Click "Send"

✅ **You're now authenticated!** All subsequent requests will use your token automatically.

---

## 📚 Collection Structure

### 1. Authentication (4 requests)
- Register User
- Login (saves tokens automatically)
- Refresh Token
- Get Current User

### 2. Trading Operations (8 requests)
- Get Trading Status
- Get All Trades
- Execute Trade
- Close Trade
- Run Backtest
- Get Live Signals
- Get Performance Analytics
- Set Risk Mode

**Example: Execute a Trade**
```json
POST /api/v1/trading/trades
{
  "pair": "GBPJPY",
  "pattern": "Inverse H&S",
  "direction": "BUY",
  "entry_price": 185.432,
  "take_profit": 186.132,
  "stop_loss": 185.082,
  "lot_size": 0.1,
  "account": "MT5_DEMO"
}
```

### 3. Legal Automation (6 requests)
- Generate Probate Petition
- Create Credit Dispute
- Get All Disputes
- File CFPB Complaint
- Generate Settlement Demand
- Calculate Damages

**Example: Generate Probate Petition**
```json
POST /api/v1/legal/documents/generate/probate
{
  "decedent_name": "Thurman Earl Robinson Sr.",
  "decedent_dod": "2025-02-15",
  "petitioner_name": "Thurman Malik Robinson Jr.",
  "estimated_estate_value": 300000,
  "elder_abuse_alleged": true
}
```

### 4. Case Management (6 requests)
- Get All Clients
- Create Client
- Get Client Details
- Create Matter/Case
- Get All Matters
- Add Case Task

### 5. Financial Management (5 requests)
- Generate Form 1040
- Generate Form 1065 (Partnership)
- Create Invoice
- Get All Invoices
- Get Credit Score

### 6. AI Orchestration (3 requests)
- Orchestrate AI Conversation
- Run ML Pattern Recognition
- Classify Legal Document

### 7. Notifications (4 requests)
- Send Notification
- Get Notification History
- Update Notification Preferences
- Test Notification

### 8. System & Monitoring (4 requests)
- Health Check
- System Status
- Get Metrics
- API Documentation

**Total: 40+ requests across 8 categories**

---

## 🔐 Authentication Flow

The collection handles authentication automatically:

1. **Initial Login:** Run the "Login" request
2. **Auto-save Tokens:** `access_token` and `refresh_token` saved to environment
3. **Auto-refresh:** Pre-request script checks token expiry and refreshes if needed
4. **Auto-include:** All requests include `Authorization: Bearer {access_token}` header

**Manual Token Refresh:**
If you need to manually refresh:
```
POST /api/v1/auth/refresh
{
  "refresh_token": "{{refresh_token}}"
}
```

---

## 🧪 Running Tests

### Run Entire Collection

1. Click collection name "AgentX5 - Complete API Collection"
2. Click "Run" button
3. Select environment (Local/Staging/Production)
4. Click "Run AgentX5 - Complete API Collection"

**Results:**
- All 40+ requests will run sequentially
- Tests will validate response times (<2000ms)
- Tests will validate status codes (200-204)
- Results dashboard shows pass/fail for each

### Run Individual Folder

Right-click any folder (e.g., "Trading Operations") → "Run folder"

### Run Single Request

Click request → Click "Send"

---

## 📊 Environment Variables

Each environment has these variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `base_url` | API base URL | `http://localhost:8000` |
| `api_version` | API version | `v1` |
| `access_token` | JWT access token | Auto-populated on login |
| `refresh_token` | JWT refresh token | Auto-populated on login |
| `token_expiry` | Token expiration timestamp | Auto-calculated |
| `user_email` | Your email | `terobinsony@gmail.com` |
| `environment_name` | Environment name | `local`, `staging`, `production` |

**To view/edit:**
1. Click environment name (top-right)
2. Click eye icon to view
3. Click edit icon to modify

---

## 🎯 Common Workflows

### Workflow 1: Execute Trade and Check Status

1. **Login** → Authenticate
2. **Execute Trade** → Create new trade
3. **Get All Trades** → Verify trade created
4. **Get Trading Status** → Check account balance
5. **Get Performance Analytics** → View performance metrics

### Workflow 2: Generate Legal Documents

1. **Login** → Authenticate
2. **Create Client** → Add new client
3. **Create Matter** → Create case
4. **Generate Probate Petition** → Create documents
5. **Add Case Task** → Schedule follow-up

### Workflow 3: Credit Repair

1. **Login** → Authenticate
2. **Create Credit Dispute** → File dispute with bureau
3. **Get All Disputes** → Check dispute status
4. **File CFPB Complaint** → Escalate if needed
5. **Get Credit Score** → Monitor improvements

### Workflow 4: Tax Filing

1. **Login** → Authenticate
2. **Generate Form 1040** → Individual tax return
3. **Generate Form 1065** → Partnership return
4. **Create Invoice** → Bill client for services
5. **Get All Invoices** → Track payments

---

## 🔧 Troubleshooting

### Issue: "Unauthorized" Error (401)

**Solution:**
1. Run "Login" request first
2. Check environment has `access_token` populated
3. If token expired, run "Refresh Token" request

### Issue: "Not Found" Error (404)

**Solution:**
1. Verify environment is correct (local vs staging vs production)
2. Check `base_url` in environment settings
3. Ensure API server is running (`uvicorn api.main:app --reload`)

### Issue: "Connection Refused"

**Solution:**
1. If using Local environment, start API server:
   ```bash
   uvicorn api.main:app --reload
   ```
2. Verify server is running at http://localhost:8000
3. Test health check: http://localhost:8000/api/v1/health

### Issue: Slow Response Times

**Solution:**
1. Check which environment you're using
2. Staging/Production may be slower than local
3. First request after idle may take longer (cold start)

### Issue: Test Failures

**Solution:**
1. Check response body for error details
2. Verify request body JSON is valid
3. Check required fields are populated
4. Review API documentation: http://localhost:8000/api/docs

---

## 📖 API Documentation

**Interactive Swagger Docs:**
- Local: http://localhost:8000/api/docs
- Staging: https://agentx5-staging.up.railway.app/api/docs
- Production: https://agentx5.up.railway.app/api/docs

**ReDoc Alternative:**
- Local: http://localhost:8000/api/redoc
- Staging: https://agentx5-staging.up.railway.app/api/redoc
- Production: https://agentx5.up.railway.app/api/redoc

---

## 🚦 CI/CD Integration

### Newman (CLI Runner)

Run collection from command line:

```bash
# Install Newman
npm install -g newman

# Run collection with local environment
newman run AgentX5.postman_collection.json \
  --environment local.postman_environment.json \
  --reporters cli,json \
  --reporter-json-export results.json

# Run with staging environment
newman run AgentX5.postman_collection.json \
  --environment staging.postman_environment.json
```

### GitLab CI Integration

Already configured in `.gitlab-ci.yml`:

```yaml
test:api:postman:
  stage: test
  image: postman/newman:latest
  script:
    - newman run postman/AgentX5.postman_collection.json \
        --environment postman/staging.postman_environment.json \
        --reporters cli,json \
        --reporter-json-export postman-results.json
```

This runs automatically on every commit!

---

## 📈 Usage Metrics

**Expected Usage:**
- Total Requests: 40+
- Average Response Time: <500ms (local), <1500ms (production)
- Test Pass Rate: 95%+

**Track in Postman:**
1. Run entire collection
2. View results dashboard
3. Check "Analytics" tab for trends

---

## 🤝 Contributing

To add new endpoints to this collection:

1. **In Postman:**
   - Right-click appropriate folder
   - Select "Add Request"
   - Configure request (method, URL, body, tests)
   - Click "Save"

2. **Export Updated Collection:**
   - Click collection (...)  menu
   - Select "Export"
   - Choose "Collection v2.1"
   - Save to `postman/AgentX5.postman_collection.json`

3. **Commit to Git:**
   ```bash
   git add postman/AgentX5.postman_collection.json
   git commit -m "Add new API endpoint: [endpoint name]"
   git push
   ```

---

## 📞 Support

**Issues?**
- Check API docs: http://localhost:8000/api/docs
- Review this README
- Check GitLab CI pipeline logs
- Email: terobinsony@gmail.com

**Useful Commands:**
```bash
# Start API server
uvicorn api.main:app --reload

# Check API health
curl http://localhost:8000/api/v1/health

# Run Newman tests
newman run postman/AgentX5.postman_collection.json \
  --environment postman/local.postman_environment.json
```

---

## ✅ Checklist

Before using this collection:

- [ ] Imported collection into Postman
- [ ] Imported all 3 environments
- [ ] Selected correct environment (Local/Staging/Production)
- [ ] API server is running (if using Local)
- [ ] Ran "Login" request successfully
- [ ] Verified `access_token` is populated in environment
- [ ] Tested "Get Current User" request
- [ ] Ready to test other endpoints!

---

**Version:** 5.0.0
**Last Updated:** December 26, 2024
**Maintainer:** Thurman Malik Robinson Jr. (terobinsony@gmail.com)
