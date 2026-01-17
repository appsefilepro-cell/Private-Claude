#!/bin/bash
#
# List Open Pull Requests - Simple wrapper script
# This script provides multiple methods to list open PRs
#

set -e

OWNER="${GITHUB_OWNER:-appsefilepro-cell}"
REPO="${GITHUB_REPO:-Private-Claude}"
LIMIT="${1:-10}"

echo "========================================================================================================"
echo "  GitHub Pull Requests Viewer - $OWNER/$REPO"
echo "========================================================================================================"
echo ""

# Method 1: Try using GitHub CLI (gh) if available
if command -v gh &> /dev/null; then
    echo "✓ Using GitHub CLI (gh)"
    echo ""
    echo "Fetching open pull requests..."
    echo ""
    
    gh pr list \
        --repo "$OWNER/$REPO" \
        --state open \
        --limit "$LIMIT" \
        --json number,title,author,createdAt,url,labels,isDraft \
        --template '{{range .}}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PR #{{.number}}: {{.title}}
Author: {{.author.login}}
Created: {{.createdAt}}
Status: {{if .isDraft}}🟢 Draft{{else}}✅ Ready for Review{{end}}
URL: {{.url}}
{{if .labels}}Labels: {{range .labels}}{{.name}} {{end}}{{end}}
{{end}}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
'
    
    echo ""
    echo "✅ Done!"
    exit 0
fi

# Method 2: Try using Python script
if command -v python3 &> /dev/null; then
    echo "ℹ GitHub CLI not found, trying Python script..."
    echo ""
    
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    python3 "$SCRIPT_DIR/list_open_pull_requests.py" "$LIMIT"
    exit $?
fi

# Method 3: Fallback - provide manual instructions
echo "❌ Neither GitHub CLI (gh) nor Python 3 found."
echo ""
echo "Please install one of the following:"
echo ""
echo "1. GitHub CLI: https://cli.github.com/"
echo "   brew install gh  # macOS"
echo "   sudo apt install gh  # Ubuntu/Debian"
echo ""
echo "2. Python 3:"
echo "   sudo apt install python3  # Ubuntu/Debian"
echo "   brew install python3  # macOS"
echo ""
echo "Or visit directly: https://github.com/$OWNER/$REPO/pulls"
echo ""
exit 1
