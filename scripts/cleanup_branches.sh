#!/bin/bash
# Branch Cleanup Script for Private-Claude Repository
# This script identifies and optionally deletes merged/stale branches

echo "========================================"
echo "BRANCH CLEANUP SCRIPT - Agent X5"
echo "========================================"
echo ""

# List all remote branches
echo "Total remote branches: $(git branch -r | wc -l)"
echo ""

# Identify branches to delete
echo "BRANCHES TO DELETE (CodeRabbit, old copilot branches):"
echo "--------------------------------------------------------"

# CodeRabbit branches (should be deleted)
echo ""
echo "1. CodeRabbit branches:"
git branch -r | grep -i coderabbit

# Merged copilot branches (can be deleted)
echo ""
echo "2. Old copilot branches (already merged):"
git branch -r --merged origin/main 2>/dev/null | grep copilot | head -20

# Claude branches (check if merged)
echo ""
echo "3. Claude branches:"
git branch -r | grep claude

echo ""
echo "========================================"
echo "TO DELETE BRANCHES, RUN THESE COMMANDS ON GITHUB:"
echo "========================================"
echo ""
echo "1. Go to: https://github.com/appsefilepro-cell/Private-Claude/branches"
echo "2. Click 'Stale' tab to see old branches"
echo "3. Delete branches you no longer need"
echo ""
echo "Or use gh CLI:"
echo "  gh api repos/appsefilepro-cell/Private-Claude/git/refs/heads/coderabbitai/utg/8657ee7 -X DELETE"
echo ""
echo "========================================"
echo "RECOMMENDED BRANCHES TO KEEP:"
echo "========================================"
echo "- main (production)"
echo "- claude/setup-multi-agent-config-BCEZa (current work)"
echo "- Any branches with open PRs"
echo ""
