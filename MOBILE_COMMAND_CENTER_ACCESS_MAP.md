# 📱 Mobile Command Center: Agent X5.0 Access Map
**Purpose:** 24/7 Monitoring and Control from iPhone/iPad/Mobile Devices.

## 1. Essential Apps to Download
To manage your infrastructure on the go, install these apps from the App Store:

| App Name | Purpose | Configuration |
| :--- | :--- | :--- |
| **GitHub** | Code & History | Sign in to `appsefilepro-cell` to view all repos and commit history. |
| **Vercel** | Dashboard Control | Monitor the AI Chatbox deployment and logs. |
| **OKX** | Trading Monitor | Monitor the 5x $100 demo accounts and live trades. |
| **Termius** | SSH/Linux Access | Connect to your Sandbox/Linux environment via SSH. |
| **Notion** | Documentation | Access the Agent X5.0 knowledge base and project maps. |
| **Zapier** | Automation | Monitor and trigger workflows (E2B -> Google Sheets). |

## 2. Master Access Points (URLs)
| Environment | Access Point | Description |
| :--- | :--- | :--- |
| **Main Repo** | [Private-Claude](https://github.com/appsefilepro-cell/Private-Claude) | Core logic, trading bots, and agent orchestration. |
| **Vercel Chatbox** | [Vercel Dashboard](https://github.com/appsefilepro-cell/PRIVATE-CLAUDE-AGENTX5-VERCEL-AI---CHATBOT-WITH-RENER) | Master AI communication point (Gemini Bridge). |
| **E2B Sandbox** | [E2B Dashboard](https://e2b.dev/dashboard) | Monitor active sandboxes and execution logs. |
| **Trading Logs** | `/home/ubuntu/Private-Claude/logs/okx_trading.log` | Real-time trading output (Access via Termius). |

## 3. Quick Control Commands (via Termius/SSH)
Use these snippets to quickly check system health from your phone:

- **Check Trading Status**:
  ```bash
  tail -f /home/ubuntu/Private-Claude/logs/okx_trading.log
  ```
- **Check Agent Heartbeat**:
  ```bash
  cat /home/ubuntu/Private-Claude/AGENT_X5_STATUS_REPORT.json
  ```
- **Restart Trading Loop**:
  ```bash
  cd /home/ubuntu/Private-Claude && python3 scripts/okx_24_7_trading.py
  ```

## 4. Fail-Safe Protocol
If Replit or a local server fails:
1. Open the **Vercel AI Chatbox** on your iPhone.
2. Use the `getAgentStatus` tool to identify the failure point.
3. Use `executeAgentTask` to trigger a remote restart of the Sandbox environment.

---
*Your system is always active. You are always in control.*
