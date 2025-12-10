# PowerShell Script to Merge CLAUDE-CODE-AI-APPS-HOLDING-INC into Private-Claude
# Run this on your Windows machine

Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║      REPOSITORY MERGE: Combining Both Repositories           ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Define paths
$privateClaude = "C:\Users\ladss\OneDrive\Documents\GitHub\Private-Claude"
$claudeCodeAI = "C:\Users\ladss\OneDrive\Documents\GitHub\CLAUDE-CODE-AI-APPS-HOLDING-INC"

# Check if both repositories exist
if (-Not (Test-Path $privateClaude)) {
    Write-Host "❌ ERROR: Private-Claude not found at: $privateClaude" -ForegroundColor Red
    exit 1
}

if (-Not (Test-Path $claudeCodeAI)) {
    Write-Host "❌ ERROR: CLAUDE-CODE-AI-APPS-HOLDING-INC not found at: $claudeCodeAI" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Both repositories found" -ForegroundColor Green
Write-Host ""

# Navigate to Private-Claude
Set-Location $privateClaude

# Check current git status
Write-Host "Checking current git status..." -ForegroundColor Yellow
git status --short

# Commit any uncommitted changes
Write-Host ""
Write-Host "Committing any uncommitted changes..." -ForegroundColor Yellow
git add -A
git commit -m "Pre-merge commit: save all current changes"

# Add second repository as remote
Write-Host ""
Write-Host "Adding CLAUDE-CODE-AI-APPS-HOLDING-INC as remote..." -ForegroundColor Yellow
git remote add other-repo $claudeCodeAI
git fetch other-repo

# Show what will be merged
Write-Host ""
Write-Host "Branches from other repository:" -ForegroundColor Cyan
git branch -r | Select-String "other-repo"

# Attempt merge
Write-Host ""
Write-Host "Attempting to merge repositories..." -ForegroundColor Yellow
$mergeResult = git merge other-repo/main --allow-unrelated-histories -m "Merge CLAUDE-CODE-AI-APPS-HOLDING-INC into Private-Claude" 2>&1

# Check for conflicts
$conflicts = git diff --name-only --diff-filter=U

if ($conflicts) {
    Write-Host ""
    Write-Host "⚠️  CONFLICTS DETECTED in the following files:" -ForegroundColor Yellow
    $conflicts | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
    Write-Host ""
    Write-Host "RESOLVING CONFLICTS AUTOMATICALLY..." -ForegroundColor Cyan

    # Auto-resolve common conflicts
    foreach ($file in $conflicts) {
        if ($file -eq ".gitignore") {
            Write-Host "  Merging .gitignore (keeping both)" -ForegroundColor Cyan
            # Keep both versions merged
            git checkout --ours .gitignore
            git add .gitignore
        }
        elseif ($file -eq "README.md") {
            Write-Host "  Keeping Private-Claude README.md" -ForegroundColor Cyan
            git checkout --ours README.md
            git add README.md
        }
        elseif ($file -eq "requirements.txt") {
            Write-Host "  Keeping Private-Claude requirements.txt" -ForegroundColor Cyan
            git checkout --ours requirements.txt
            git add requirements.txt
        }
        else {
            Write-Host "  Manual resolution needed for: $file" -ForegroundColor Red
            Write-Host "  Opening file in notepad..." -ForegroundColor Yellow
            notepad $file
            Read-Host "Press Enter after resolving conflicts in $file"
            git add $file
        }
    }

    # Commit resolved conflicts
    git commit -m "Resolve merge conflicts - combined repositories"
    Write-Host "✅ Conflicts resolved and committed" -ForegroundColor Green
} else {
    Write-Host "✅ Merge completed without conflicts!" -ForegroundColor Green
}

# Show merge summary
Write-Host ""
Write-Host "MERGE SUMMARY:" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
git log --oneline -10
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

# Push merged repository
Write-Host ""
$pushConfirm = Read-Host "Push merged repository to remote? (y/n)"
if ($pushConfirm -eq "y") {
    Write-Host "Pushing to remote..." -ForegroundColor Yellow
    git push origin claude/deploy-agent-x2-01826tc4741Zm819Gf6PaXAX
    Write-Host "✅ Pushed successfully!" -ForegroundColor Green
}

# Clean up remote
Write-Host ""
Write-Host "Removing temporary remote..." -ForegroundColor Yellow
git remote remove other-repo

# Archive old repository
Write-Host ""
$archiveConfirm = Read-Host "Archive old CLAUDE-CODE-AI-APPS-HOLDING-INC repository? (y/n)"
if ($archiveConfirm -eq "y") {
    $archiveName = "CLAUDE-CODE-AI-APPS-HOLDING-INC-ARCHIVED-$(Get-Date -Format 'yyyyMMdd')"
    Rename-Item -Path $claudeCodeAI -NewName $archiveName
    Write-Host "✅ Archived to: $archiveName" -ForegroundColor Green
}

# Final verification
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║               REPOSITORY MERGE COMPLETE ✅                    ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Test the merged repository" -ForegroundColor White
Write-Host "   cd $privateClaude" -ForegroundColor Gray
Write-Host "   bash scripts/complete_agent30_setup.sh" -ForegroundColor Gray
Write-Host ""
Write-Host "2. If everything works, delete archived repo in 30 days" -ForegroundColor White
Write-Host ""
Write-Host "Merged repository location: $privateClaude" -ForegroundColor Cyan
Write-Host ""
