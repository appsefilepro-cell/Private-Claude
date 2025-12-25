# PowerShell Fix Script - Navigate to Repository and Run Agent 3.0
# This fixes the "file not found" errors

Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          AGENT 3.0 - AUTO FIX & SETUP SCRIPT                 ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Find the Private-Claude repository
$possiblePaths = @(
    "C:\Users\ladss\OneDrive\Documents\GitHub\Private-Claude",
    "C:\Users\ladss\Documents\GitHub\Private-Claude",
    "C:\Users\ladss\Private-Claude",
    "C:\Users\ladss\OneDrive\Private-Claude"
)

$repoPath = $null
foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        $repoPath = $path
        Write-Host "✅ Found repository at: $path" -ForegroundColor Green
        break
    }
}

if (-not $repoPath) {
    Write-Host "❌ ERROR: Private-Claude repository not found!" -ForegroundColor Red
    Write-Host "Searched locations:" -ForegroundColor Yellow
    $possiblePaths | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }
    Write-Host ""
    Write-Host "Please clone the repository first:" -ForegroundColor Yellow
    Write-Host "  cd C:\Users\ladss\OneDrive\Documents\GitHub" -ForegroundColor Gray
    Write-Host "  git clone <repository-url> Private-Claude" -ForegroundColor Gray
    Read-Host "Press Enter to exit"
    exit 1
}

# Navigate to repository
Set-Location $repoPath
Write-Host "📂 Changed directory to: $repoPath" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host "  $pythonVersion" -ForegroundColor Gray

# Pull latest changes
Write-Host ""
Write-Host "Pulling latest changes from GitHub..." -ForegroundColor Yellow
git pull origin claude/deploy-agent-x2-01826tc4741Zm819Gf6PaXAX

# Install/update dependencies
Write-Host ""
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet

# Run complete setup
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║               RUNNING COMPLETE AGENT 3.0 SETUP               ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

# 1. Activate all systems
Write-Host "STEP 1: Activating all systems..." -ForegroundColor Cyan
python scripts/activate_all_systems.py

# 2. Run integration tests
Write-Host ""
Write-Host "STEP 2: Running integration tests..." -ForegroundColor Cyan
python tests/integration_test_suite.py

# 3. Test Zapier (if after 3am)
Write-Host ""
Write-Host "STEP 3: Testing Zapier integrations..." -ForegroundColor Cyan
python tests/test_zapier_integrations.py

# 4. Run backtest
Write-Host ""
Write-Host "STEP 4: Running 24-hour backtest..." -ForegroundColor Cyan
python pillar-a-trading/backtesting/backtesting_engine.py

# Success message
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                  SETUP COMPLETE ✅                            ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Repository location: $repoPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now run commands from this directory:" -ForegroundColor White
Write-Host "  python scripts/activate_all_systems.py" -ForegroundColor Gray
Write-Host "  python tests/integration_test_suite.py" -ForegroundColor Gray
Write-Host "  python pillar-a-trading/backtesting/backtesting_engine.py" -ForegroundColor Gray
Write-Host ""

Read-Host "Press Enter to exit"
