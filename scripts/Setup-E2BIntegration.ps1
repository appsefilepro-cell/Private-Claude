# E2B Integration Setup Script for Windows PowerShell
# Run as Administrator for full functionality

param(
    [switch]$SkipPrerequisites,
    [switch]$TestOnly
)

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "E2B INTEGRATION SETUP FOR WINDOWS" -ForegroundColor Cyan
Write-Host "======================================`n" -ForegroundColor Cyan

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "⚠️  Warning: Not running as Administrator" -ForegroundColor Yellow
    Write-Host "Some operations may require elevated privileges`n" -ForegroundColor Yellow
}

# Set base directory
$rootDir = Split-Path -Parent $PSScriptRoot
$configDir = Join-Path $rootDir "config"
$scriptsDir = Join-Path $rootDir "scripts"

# Function to check prerequisites
function Test-Prerequisites {
    Write-Host "🔍 Checking prerequisites..." -ForegroundColor Yellow

    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ Python not found. Install from https://python.org" -ForegroundColor Red
        return $false
    }

    # Check pip
    try {
        pip --version | Out-Null
        Write-Host "✅ pip installed" -ForegroundColor Green
    } catch {
        Write-Host "❌ pip not found" -ForegroundColor Red
        return $false
    }

    # Check git
    try {
        git --version | Out-Null
        Write-Host "✅ Git installed" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Git not found (optional)" -ForegroundColor Yellow
    }

    return $true
}

# Function to install Python dependencies
function Install-PythonDependencies {
    Write-Host "`n📦 Installing Python dependencies..." -ForegroundColor Yellow

    $requirements = Join-Path $rootDir "requirements.txt"

    if (Test-Path $requirements) {
        pip install -r $requirements --quiet
        Write-Host "✅ Dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "⚠️  requirements.txt not found, installing core packages..." -ForegroundColor Yellow
        pip install requests python-dotenv --quiet
    }
}

# Function to setup environment file
function Setup-EnvironmentFile {
    Write-Host "`n🔧 Setting up environment configuration..." -ForegroundColor Yellow

    $envTemplate = Join-Path $configDir ".env.template"
    $envFile = Join-Path $configDir ".env"

    if (-not (Test-Path $envFile)) {
        Copy-Item $envTemplate $envFile
        Write-Host "✅ Created .env file from template" -ForegroundColor Green
        Write-Host "📝 Please edit config\.env with your API keys" -ForegroundColor Cyan
    } else {
        Write-Host "✅ .env file already exists" -ForegroundColor Green
    }
}

# Function to verify configuration files
function Test-ConfigurationFiles {
    Write-Host "`n📋 Verifying configuration files..." -ForegroundColor Yellow

    $configFiles = @(
        "e2b_webhook_config.json",
        "zapier_connector.json",
        "github_webhook_integration.json",
        "mcp_server_config.json",
        "postman_collection.json",
        "API_KEYS_REFERENCE.md"
    )

    $allExist = $true
    foreach ($file in $configFiles) {
        $path = Join-Path $configDir $file
        if (Test-Path $path) {
            Write-Host "✅ $file" -ForegroundColor Green
        } else {
            Write-Host "❌ $file missing" -ForegroundColor Red
            $allExist = $false
        }
    }

    return $allExist
}

# Function to test API connections
function Test-APIConnections {
    Write-Host "`n🔌 Testing API connections..." -ForegroundColor Yellow

    # Load environment variables
    $envFile = Join-Path $configDir ".env"
    if (Test-Path $envFile) {
        Get-Content $envFile | ForEach-Object {
            if ($_ -match '^([^#][^=]+)=(.+)$') {
                $key = $matches[1].Trim()
                $value = $matches[2].Trim()
                [Environment]::SetEnvironmentVariable($key, $value, "Process")
            }
        }
    }

    # Test E2B API
    $e2bKey = $env:E2B_API_KEY
    if ($e2bKey -and $e2bKey -ne "your_e2b_api_key_here") {
        try {
            $headers = @{
                "Authorization" = "Bearer $e2bKey"
                "Content-Type" = "application/json"
            }
            $response = Invoke-RestMethod -Uri "https://api.e2b.dev/sandboxes" -Method POST -Headers $headers -Body '{"template":"python3","timeout":300}' -TimeoutSec 30 -ErrorAction Stop
            Write-Host "✅ E2B API connected" -ForegroundColor Green
        } catch {
            Write-Host "⚠️  E2B API test failed (check API key)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "⏳ E2B API key not configured" -ForegroundColor Yellow
    }

    # Test Gemini API
    $geminiKey = $env:GEMINI_API_KEY
    if ($geminiKey -and $geminiKey -ne "your_gemini_api_key_here") {
        try {
            $uri = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key=$geminiKey"
            $body = @{
                contents = @(
                    @{
                        parts = @(@{ text = "Say Hello" })
                    }
                )
            } | ConvertTo-Json -Depth 10

            $response = Invoke-RestMethod -Uri $uri -Method POST -Body $body -ContentType "application/json" -TimeoutSec 15 -ErrorAction Stop
            Write-Host "✅ Gemini API connected" -ForegroundColor Green
        } catch {
            Write-Host "⚠️  Gemini API test failed" -ForegroundColor Yellow
        }
    } else {
        Write-Host "⏳ Gemini API key not configured" -ForegroundColor Yellow
    }
}

# Function to start webhook server
function Start-WebhookServer {
    Write-Host "`n🚀 Starting webhook server..." -ForegroundColor Yellow

    $handlerScript = Join-Path $scriptsDir "e2b_webhook_handler.py"

    if (Test-Path $handlerScript) {
        Write-Host "Starting E2B webhook handler..." -ForegroundColor Cyan
        Write-Host "Press Ctrl+C to stop the server`n" -ForegroundColor Gray

        python $handlerScript
    } else {
        Write-Host "❌ Webhook handler not found: $handlerScript" -ForegroundColor Red
    }
}

# Main execution
try {
    if (-not $SkipPrerequisites) {
        if (-not (Test-Prerequisites)) {
            Write-Host "`n❌ Prerequisites check failed" -ForegroundColor Red
            exit 1
        }

        Install-PythonDependencies
    }

    Setup-EnvironmentFile

    $configsExist = Test-ConfigurationFiles

    if ($TestOnly) {
        Test-APIConnections
    }

    Write-Host "`n======================================" -ForegroundColor Cyan
    Write-Host "📊 SETUP SUMMARY" -ForegroundColor Cyan
    Write-Host "======================================" -ForegroundColor Cyan

    if ($configsExist) {
        Write-Host "✅ All configuration files present" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Some configuration files missing" -ForegroundColor Yellow
    }

    Write-Host "`n📝 NEXT STEPS:" -ForegroundColor Cyan
    Write-Host "1. Edit config\.env with your API keys" -ForegroundColor White
    Write-Host "2. Run: .\scripts\Setup-E2BIntegration.ps1 -TestOnly" -ForegroundColor White
    Write-Host "3. Import config\postman_collection.json to Postman" -ForegroundColor White
    Write-Host "4. Start webhook server (run without parameters)" -ForegroundColor White

    Write-Host "`n✨ Setup complete!`n" -ForegroundColor Green

} catch {
    Write-Host "`n❌ Error during setup: $_" -ForegroundColor Red
    exit 1
}
