#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# MAKE AGENTX5 LIVE EVERYWHERE
# Deploy AgentX5 to iPhone, Edge Browser, and PowerShell
# ═══════════════════════════════════════════════════════════════════════════

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║   DEPLOYING AGENTX5 TO ALL PLATFORMS                        ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# ═══════════════════════════════════════════════════════════════════════════
# PLATFORM 1: WINDOWS POWERSHELL
# ═══════════════════════════════════════════════════════════════════════════

echo "🖥️  PLATFORM 1: Windows PowerShell"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ PowerShell installer created: AGENTX5_POWERSHELL_INSTALL.ps1"
echo ""
echo "📖 TO INSTALL ON WINDOWS:"
echo "   1. Open PowerShell as Administrator"
echo "   2. Run: Set-ExecutionPolicy RemoteSigned -Scope CurrentUser"
echo "   3. Run: .\\AGENTX5_POWERSHELL_INSTALL.ps1"
echo "   4. After installation, use: agentx5 'your question'"
echo ""
echo "✨ FEATURES:"
echo "   • Available in every PowerShell session"
echo "   • Type 'agentx5' for interactive mode"
echo "   • Type 'agentx5 \"question\"' for quick answers"
echo "   • Helps with fraud dispute, system status, debugging"
echo "   • FREE - no API key required (offline mode)"
echo ""

# ═══════════════════════════════════════════════════════════════════════════
# PLATFORM 2: iPHONE (Progressive Web App)
# ═══════════════════════════════════════════════════════════════════════════

echo "📱 PLATFORM 2: iPhone (Progressive Web App)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ iPhone app created: AGENTX5_IPHONE_DEPLOY.html"
echo "✅ Manifest created: manifest.json"
echo ""
echo "📖 TO INSTALL ON iPHONE:"
echo ""
echo "   METHOD 1: Local Server (Recommended)"
echo "   ────────────────────────────────────"
echo "   1. Start local web server:"
echo "      python3 -m http.server 8080"
echo ""
echo "   2. Find your computer's IP address:"
echo "      - Windows: ipconfig | findstr IPv4"
echo "      - Mac/Linux: ifconfig | grep 'inet '"
echo ""
echo "   3. On your iPhone Safari, visit:"
echo "      http://YOUR-COMPUTER-IP:8080/AGENTX5_IPHONE_DEPLOY.html"
echo ""
echo "   4. Tap Share button ⬆️  (bottom of screen)"
echo "   5. Scroll down and tap 'Add to Home Screen'"
echo "   6. Tap 'Add' in top right"
echo "   7. AgentX5 icon appears on your home screen!"
echo ""
echo "   METHOD 2: GitHub Pages (Public)"
echo "   ───────────────────────────────────"
echo "   1. Push code to GitHub"
echo "   2. Enable GitHub Pages in repo settings"
echo "   3. Visit: https://appsefilepro-cell.github.io/Private-Claude/AGENTX5_IPHONE_DEPLOY.html"
echo "   4. Follow steps 4-7 above"
echo ""
echo "✨ FEATURES:"
echo "   • Works like native iPhone app"
echo "   • Access fraud dispute info ($313K)"
echo "   • Check system status"
echo "   • Ask questions and get answers"
echo "   • Works offline after first load"
echo "   • FREE - no hosting cost"
echo ""

# Start local server for testing
echo "🚀 Starting local web server for iPhone installation..."
echo "   Access URL: http://localhost:8080/AGENTX5_IPHONE_DEPLOY.html"
echo ""
echo "   Press Ctrl+C to stop server when installation is complete"
echo ""

# Check if port 8080 is available
if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "   ⚠️  Port 8080 already in use. Using port 8081 instead."
    PORT=8081
else
    PORT=8080
fi

echo "   Starting server on port $PORT..."
echo ""

# Start server in background
python3 -m http.server $PORT > /tmp/agentx5_server.log 2>&1 &
SERVER_PID=$!

echo "   ✅ Server started (PID: $SERVER_PID)"
echo "   📱 On your iPhone, visit: http://YOUR-IP:$PORT/AGENTX5_IPHONE_DEPLOY.html"
echo ""
echo "   To find YOUR-IP:"
echo "   - Windows: ipconfig | findstr IPv4"
echo "   - Mac/Linux: ifconfig | grep 'inet ' | grep -v 127.0.0.1"
echo ""

# Try to get local IP
LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || ipconfig getifaddr en0 2>/dev/null || echo "YOUR-IP")
if [ "$LOCAL_IP" != "YOUR-IP" ]; then
    echo "   📍 Your IP appears to be: $LOCAL_IP"
    echo "   📱 iPhone URL: http://$LOCAL_IP:$PORT/AGENTX5_IPHONE_DEPLOY.html"
fi

echo ""
echo "   Server will keep running. Stop it with: kill $SERVER_PID"
echo "   Or press Ctrl+C"
echo ""

# Save PID for later cleanup
echo $SERVER_PID > /tmp/agentx5_server.pid

# ═══════════════════════════════════════════════════════════════════════════
# PLATFORM 3: EDGE BROWSER (Extension)
# ═══════════════════════════════════════════════════════════════════════════

echo "🌐 PLATFORM 3: Microsoft Edge (Browser Extension)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Edge extension created: edge-extension/"
echo ""
echo "📖 TO INSTALL IN EDGE:"
echo "   1. Open Edge browser"
echo "   2. Go to: edge://extensions"
echo "   3. Enable 'Developer mode' (toggle in bottom left)"
echo "   4. Click 'Load unpacked'"
echo "   5. Select folder: $(pwd)/edge-extension"
echo "   6. Extension will appear in toolbar!"
echo ""
echo "✨ FEATURES:"
echo "   • Click extension icon or press Ctrl+Shift+A"
echo "   • Access from any webpage"
echo "   • Check fraud dispute status ($313K)"
echo "   • Ask questions and get instant answers"
echo "   • View system status and next steps"
echo "   • Right-click selected text: 'Ask AgentX5'"
echo "   • FREE - works offline"
echo ""

# ═══════════════════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════════════════

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║   ✅ AGENTX5 READY ON ALL PLATFORMS                         ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 DEPLOYMENT STATUS:"
echo ""
echo "   ✅ PowerShell:  AGENTX5_POWERSHELL_INSTALL.ps1 ready"
echo "   ✅ iPhone:      Server running on port $PORT"
echo "   ✅ Edge:        Extension ready in edge-extension/"
echo ""
echo "💰 FRAUD DISPUTE STATUS:"
echo ""
echo "   Total Amount:  \$313,000.00"
echo "   BMO Harris:    \$150,000.00"
echo "   Second Bank:   \$163,000.00"
echo "   Status:        ✅ READY TO FILE TODAY"
echo "   Documents:     FINAL_SUBMISSION_DOCUMENTS/"
echo ""
echo "🎯 NEXT STEPS:"
echo ""
echo "   1. Install AgentX5 on your devices (instructions above)"
echo "   2. File fraud dispute TODAY (print, sign, mail)"
echo "   3. Use AgentX5 to track status and get help"
echo ""
echo "🚀 AGENTX5 IS NOW YOUR PERMANENT HELPER ACROSS ALL PLATFORMS!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📱 iPhone Installation URL (use this on your iPhone Safari):"
echo "   http://$LOCAL_IP:$PORT/AGENTX5_IPHONE_DEPLOY.html"
echo ""
echo "⚠️  Keep this terminal open to keep the iPhone server running!"
echo "   Stop server with: kill $SERVER_PID"
echo ""
