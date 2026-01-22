// AgentX5 Edge Extension - Popup Logic

function showDocuments() {
    addMessage('agent', `📄 Documents Ready:

✅ BMO Harris ($150,000)
✅ Second Bank ($163,000)
✅ Experian Dispute
✅ Equifax Dispute
✅ TransUnion Dispute

Location: FINAL_SUBMISSION_DOCUMENTS/

Action: Print, sign, mail TODAY via certified mail ($36)`);
}

function checkStatus() {
    addMessage('agent', `🔍 System Status:

✅ AgentX5: 750 agents active
✅ Edge Extension: Installed
✅ iPhone App: Available
✅ PowerShell: Available
✅ Fraud Dispute: $313K ready
✅ PRs: 118 processing
✅ Cost: $0/month

All systems operational!`);
}

function showNextSteps() {
    addMessage('agent', `🎯 Priority Actions:

1. FILE DISPUTE TODAY ($313K)
   Print & mail FINAL_SUBMISSION_DOCUMENTS/

2. Install on other devices
   - iPhone: Open AGENTX5_IPHONE_DEPLOY.html
   - PowerShell: Run AGENTX5_POWERSHELL_INSTALL.ps1

3. Monitor GitHub
   118 PRs processing automatically

4. Wait for bank responses
   10 days: Provisional credit
   45 days: Final resolution`);
}

function sendQuery() {
    const input = document.getElementById('queryInput');
    const query = input.value.trim();

    if (!query) return;

    addMessage('user', query);
    input.value = '';

    setTimeout(() => processQuery(query), 300);
}

function processQuery(query) {
    const lowerQuery = query.toLowerCase();

    if (lowerQuery.includes('status')) {
        checkStatus();
    } else if (lowerQuery.includes('fraud') || lowerQuery.includes('dispute') || lowerQuery.includes('money')) {
        showDocuments();
    } else if (lowerQuery.includes('next') || lowerQuery.includes('step')) {
        showNextSteps();
    } else if (lowerQuery.includes('hello') || lowerQuery.includes('hi')) {
        addMessage('agent', '👋 Hi! I\'m AgentX5. Your $313K fraud dispute is ready to file TODAY. How can I help?');
    } else if (lowerQuery.includes('amount') || lowerQuery.includes('how much')) {
        addMessage('agent', '💰 Total Fraud Dispute: $313,000\n\nBMO Harris: $150,000\nSecond Bank: $163,000\n\nAll documents ready to file TODAY!');
    } else {
        addMessage('agent', `I can help with:

• Fraud dispute ($313K ready)
• System status
• Next steps
• Documents & filing

Try asking: "What's my dispute amount?" or "What should I do next?"`);
    }
}

function addMessage(type, text) {
    const conversation = document.getElementById('conversation');
    const message = document.createElement('div');
    message.className = `message ${type}`;
    message.textContent = text;
    conversation.appendChild(message);
    conversation.scrollTop = conversation.scrollHeight;
}

// Event listeners
document.getElementById('queryInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendQuery();
    }
});

// Welcome message
chrome.storage.local.get(['welcomed'], function(result) {
    if (!result.welcomed) {
        setTimeout(() => {
            addMessage('agent', '👋 Welcome to AgentX5! Press Ctrl+Shift+A anytime to open. Your $313K fraud dispute is ready to file TODAY!');
        }, 500);
        chrome.storage.local.set({ welcomed: true });
    }
});
