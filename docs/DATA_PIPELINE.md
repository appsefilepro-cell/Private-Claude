# Agent X5.0 Data Pipeline

## How Information Flows Through the System

```
┌─────────────────────────────────────────────────────────────────┐
│                         INPUT SOURCES                           │
├─────────────────────────────────────────────────────────────────┤
│  Documents    │  APIs        │  User Input  │  Webhooks        │
│  (PDF, DOCX)  │  (Trading)   │  (Forms)     │  (TradingView)   │
└───────┬───────┴──────┬───────┴──────┬───────┴───────┬──────────┘
        │              │              │               │
        ▼              ▼              ▼               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATA INGESTION LAYER                         │
├─────────────────────────────────────────────────────────────────┤
│  • Document Parser (PyMuPDF, python-docx)                       │
│  • API Connectors (ccxt, httpx)                                 │
│  • Form Processor (Google Forms → Zapier)                       │
│  • Webhook Receiver (FastAPI endpoints)                         │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PROCESSING LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│  Master CFO Agent (orchestrates all 219 agents)                 │
│  ├── AI/ML Division (33 agents) - Analysis & Research          │
│  ├── Legal Division (35 agents) - Document Processing          │
│  ├── Trading Division (30 agents) - Market Analysis            │
│  ├── Financial Division (20 agents) - Tax & CFO Suite          │
│  └── Integration Division (30 agents) - Data Flow              │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    STORAGE LAYER                                │
├─────────────────────────────────────────────────────────────────┤
│  • Google Sheets (trading logs, dashboards)                     │
│  • SharePoint (documents, case files)                           │
│  • Airtable (client database, case management)                  │
│  • Local Files (logs, reports, configs)                         │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OUTPUT LAYER                                 │
├─────────────────────────────────────────────────────────────────┤
│  • Slack Notifications                                          │
│  • Email Alerts                                                 │
│  • Generated Documents (DOCX, PDF)                              │
│  • Trading Signals                                              │
│  • Dashboard Updates                                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow by Use Case

### 1. Legal Document Processing
```
PDF Upload → PyMuPDF Extract → Claude Analysis → Template Fill → DOCX Output → SharePoint
```

### 2. Trading Signal Processing
```
TradingView Alert → Webhook → Filter (>70%) → Claude + ChatGPT → Decision → Google Sheets → Slack
```

### 3. Client Intake
```
Google Form → Zapier → Airtable Record → Welcome Email → Calendar Event → Slack Notification
```

### 4. Bonds Trading
```
Schedule (Hourly) → Treasury API → Gemini Analysis → Google Sheets Log → Slack (if opportunity)
```

---

## Error Handling

| Stage | Error Type | Recovery Action |
|-------|------------|-----------------|
| Ingestion | API timeout | Retry 3x with backoff |
| Processing | AI API error | Fallback to alternate AI |
| Storage | Write failure | Queue for retry |
| Output | Notification fail | Log and retry |

---

## Rate Limits

| Service | Limit | Our Usage |
|---------|-------|-----------|
| Anthropic | 1000/min | ~10/min |
| OpenAI | 3500/min | ~5/min |
| Gemini | 60/min | ~5/min |
| OKX | 20/sec | ~1/sec |
| Treasury | No limit | 24/day |
| Zapier | 100/month | 96/month |
