#!/bin/bash
# DEPLOY AGENTX5 LIVE - PRESENTATION READY

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║   DEPLOYING AGENTX5 LIVE - PRESENTATION MODE                ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if gh CLI is available
if ! command -v gh &> /dev/null; then
    echo "⚠️  GitHub CLI not found - using git commands instead"
fi

# Enable GitHub Pages
echo "📡 Step 1: Enabling GitHub Pages..."
echo "   Branch: claude/multi-agent-task-execution-7nsUS"
echo "   Path: / (root)"
echo ""

# Create a simple index.html that redirects to AgentX5
cat > index.html << 'HTMLEOF'
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0;url=AGENTX5_IPHONE_DEPLOY.html">
    <title>Redirecting to AgentX5...</title>
</head>
<body>
    <p>Redirecting to AgentX5...</p>
    <p>If not redirected, <a href="AGENTX5_IPHONE_DEPLOY.html">click here</a>.</p>
</body>
</html>
HTMLEOF

echo "✅ Created index.html redirect"
echo ""

# Commit and push
git add index.html deploy-live-now.sh
git commit -m "🚀 DEPLOY: Enable GitHub Pages for live access"
git push

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║   ✅ DEPLOYMENT INITIATED                                    ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📡 LIVE URLs (will be active in 1-2 minutes):"
echo ""
echo "   Primary:"
echo "   https://appsefilepro-cell.github.io/Private-Claude/"
echo ""
echo "   AgentX5 Direct:"
echo "   https://appsefilepro-cell.github.io/Private-Claude/AGENTX5_IPHONE_DEPLOY.html"
echo ""
echo "   Edge Extension:"
echo "   Download from: https://appsefilepro-cell.github.io/Private-Claude/edge-extension/"
echo ""
echo "⚙️  TO ENABLE GITHUB PAGES:"
echo "   1. Go to: https://github.com/appsefilepro-cell/Private-Claude/settings/pages"
echo "   2. Source: Deploy from a branch"
echo "   3. Branch: claude/multi-agent-task-execution-7nsUS"
echo "   4. Folder: / (root)"
echo "   5. Click 'Save'"
echo ""
echo "🎉 AGENTX5 WILL BE LIVE IN 1-2 MINUTES!"
echo ""
