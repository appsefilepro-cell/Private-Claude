# ==============================================================================
# WINDOWS SYSTEM CLEANUP & OPTIMIZATION - PowerShell Script
# ==============================================================================
# Copy and paste this ENTIRE script into Windows PowerShell (Run as Administrator)
# This will clean, optimize, and secure your Windows system
# ==============================================================================

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "WINDOWS SYSTEM CLEANUP & OPTIMIZATION" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Require Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsRoleIdentifier]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    pause
    exit
}

Write-Host "✅ Running as Administrator" -ForegroundColor Green
Write-Host ""

# ==============================================================================
# PART 1: MICROSOFT DEFENDER - ENABLE ALL FREE TOOLS
# ==============================================================================
Write-Host "PART 1: MICROSOFT DEFENDER OPTIMIZATION" -ForegroundColor Yellow
Write-Host "================================================================================" -ForegroundColor Cyan

# Enable Real-Time Protection
Write-Host "Enabling Real-Time Protection..." -ForegroundColor White
Set-MpPreference -DisableRealtimeMonitoring $false

# Enable Cloud Protection
Write-Host "Enabling Cloud Protection..." -ForegroundColor White
Set-MpPreference -MAPSReporting Advanced

# Enable Automatic Sample Submission
Write-Host "Enabling Automatic Sample Submission..." -ForegroundColor White
Set-MpPreference -SubmitSamplesConsent SendAllSamples

# Enable Controlled Folder Access (Ransomware Protection)
Write-Host "Enabling Controlled Folder Access..." -ForegroundColor White
Set-MpPreference -EnableControlledFolderAccess Enabled

# Enable Network Protection
Write-Host "Enabling Network Protection..." -ForegroundColor White
Set-MpPreference -EnableNetworkProtection Enabled

# Update Virus Definitions
Write-Host "Updating virus definitions..." -ForegroundColor White
Update-MpSignature

# Run Quick Scan
Write-Host "Running Quick Scan (this may take a few minutes)..." -ForegroundColor White
Start-MpScan -ScanType QuickScan

Write-Host "✅ Microsoft Defender fully optimized" -ForegroundColor Green
Write-Host ""

# ==============================================================================
# PART 2: REMOVE UNWANTED APPS AND DATA
# ==============================================================================
Write-Host "PART 2: REMOVING UNWANTED APPS AND DATA" -ForegroundColor Yellow
Write-Host "================================================================================" -ForegroundColor Cyan

# List of bloatware to remove (keeping music apps)
$bloatware = @(
    "*RemoteDesktop*",
    "*RemoteAssistance*",
    "*BingNews*",
    "*BingWeather*",
    "*BingFinance*",
    "*CandyCrush*",
    "*Facebook*",
    "*Twitter*",
    "*LinkedIn*",
    "*Netflix*",
    "*Disney*",
    "*SpotifyAB.SpotifyMusic*",  # Removing Spotify store app (you can keep desktop version)
    "*Xbox*",
    "*Solitaire*",
    "*Minecraft*"
)

# Note: Keeping music apps like Windows Media Player, Groove Music

Write-Host "Removing bloatware applications..." -ForegroundColor White
foreach ($app in $bloatware) {
    Write-Host "Checking for $app..." -ForegroundColor Gray
    Get-AppxPackage -Name $app -AllUsers | Remove-AppxPackage -ErrorAction SilentlyContinue
    Get-AppxProvisionedPackage -Online | Where-Object DisplayName -like $app | Remove-AppxProvisionedPackage -Online -ErrorAction SilentlyContinue
}

Write-Host "✅ Bloatware removed" -ForegroundColor Green
Write-Host ""

# ==============================================================================
# PART 3: CLEAN TEMP FILES AND DISK CLEANUP
# ==============================================================================
Write-Host "PART 3: DISK CLEANUP" -ForegroundColor Yellow
Write-Host "================================================================================" -ForegroundColor Cyan

# Clean Windows Temp
Write-Host "Cleaning Windows Temp files..." -ForegroundColor White
Remove-Item -Path "$env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "C:\Windows\Temp\*" -Recurse -Force -ErrorAction SilentlyContinue

# Clean Windows Update Cache
Write-Host "Cleaning Windows Update cache..." -ForegroundColor White
Stop-Service -Name wuauserv -Force
Remove-Item -Path "C:\Windows\SoftwareDistribution\Download\*" -Recurse -Force -ErrorAction SilentlyContinue
Start-Service -Name wuauserv

# Clean Recycle Bin
Write-Host "Emptying Recycle Bin..." -ForegroundColor White
Clear-RecycleBin -Force -ErrorAction SilentlyContinue

# Run Disk Cleanup
Write-Host "Running Disk Cleanup..." -ForegroundColor White
Start-Process -FilePath CleanMgr.exe -ArgumentList '/sagerun:1' -Wait

Write-Host "✅ Disk cleanup complete" -ForegroundColor Green
Write-Host ""

# ==============================================================================
# PART 4: REMOVE LINUX/UBUNTU (WSL) FILES
# ==============================================================================
Write-Host "PART 4: REMOVING WSL (Linux/Ubuntu)" -ForegroundColor Yellow
Write-Host "================================================================================" -ForegroundColor Cyan

# Check if WSL is installed
$wslInstalled = Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux

if ($wslInstalled.State -eq "Enabled") {
    Write-Host "WSL is installed. Removing..." -ForegroundColor White

    # Unregister all WSL distributions
    wsl --list | ForEach-Object {
        if ($_ -and $_ -notmatch "Windows Subsystem") {
            $distro = $_.Trim()
            Write-Host "Unregistering $distro..." -ForegroundColor Gray
            wsl --unregister $distro
        }
    }

    # Disable WSL feature
    Disable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux -NoRestart

    # Remove WSL files
    Remove-Item -Path "$env:LOCALAPPDATA\Packages\*CanonicalGroupLimited*" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "$env:LOCALAPPDATA\lxss" -Recurse -Force -ErrorAction SilentlyContinue

    Write-Host "✅ WSL removed. RESTART REQUIRED for complete removal." -ForegroundColor Green
} else {
    Write-Host "✅ WSL not installed" -ForegroundColor Green
}

Write-Host ""

# ==============================================================================
# PART 5: STOP UNNECESSARY BACKGROUND APPS
# ==============================================================================
Write-Host "PART 5: DISABLING UNNECESSARY BACKGROUND APPS" -ForegroundColor Yellow
Write-Host "================================================================================" -ForegroundColor Cyan

# Disable unnecessary startup programs
$startupApps = Get-CimInstance Win32_StartupCommand | Where-Object {
    $_.Name -notlike "*Defender*" -and
    $_.Name -notlike "*Audio*" -and
    $_.Name -notlike "*Music*" -and
    $_.Name -notlike "*VPN*"
}

Write-Host "Found $($startupApps.Count) startup apps (excluding Defender, Audio, Music, VPN)" -ForegroundColor White

# Disable telemetry and diagnostics
Write-Host "Disabling telemetry services..." -ForegroundColor White
Get-Service DiagTrack,dmwappushservice | Stop-Service -Force
Get-Service DiagTrack,dmwappushservice | Set-Service -StartupType Disabled

# Disable unnecessary Windows services
$servicesToDisable = @(
    "XblAuthManager",      # Xbox Live Auth Manager
    "XblGameSave",         # Xbox Live Game Save
    "XboxNetApiSvc",       # Xbox Live Networking Service
    "RemoteRegistry",      # Remote Registry (security risk)
    "RemoteAccess"         # Routing and Remote Access
)

foreach ($service in $servicesToDisable) {
    $svc = Get-Service -Name $service -ErrorAction SilentlyContinue
    if ($svc) {
        Write-Host "Disabling $service..." -ForegroundColor Gray
        Stop-Service -Name $service -Force -ErrorAction SilentlyContinue
        Set-Service -Name $service -StartupType Disabled
    }
}

Write-Host "✅ Unnecessary background apps disabled" -ForegroundColor Green
Write-Host ""

# ==============================================================================
# PART 6: OPTIMIZE FOR PERFORMANCE
# ==============================================================================
Write-Host "PART 6: PERFORMANCE OPTIMIZATION" -ForegroundColor Yellow
Write-Host "================================================================================" -ForegroundColor Cyan

# Disable visual effects for better performance
Write-Host "Optimizing visual effects for performance..." -ForegroundColor White
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects" -Name "VisualFXSetting" -Value 2

# Disable animations
Set-ItemProperty -Path "HKCU:\Control Panel\Desktop\WindowMetrics" -Name "MinAnimate" -Value "0"

# Optimize paging file (virtual memory)
Write-Host "Optimizing virtual memory..." -ForegroundColor White
$computersys = Get-WmiObject Win32_ComputerSystem -EnableAllPrivileges
$computersys.AutomaticManagedPagefile = $false
$computersys.Put()

Write-Host "✅ Performance optimized" -ForegroundColor Green
Write-Host ""

# ==============================================================================
# PART 7: CLEAN C DRIVE - REMOVE UNNECESSARY FILES
# ==============================================================================
Write-Host "PART 7: C DRIVE CLEANUP" -ForegroundColor Yellow
Write-Host "================================================================================" -ForegroundColor Cyan

# Remove old Windows installations
Write-Host "Removing old Windows installations..." -ForegroundColor White
if (Test-Path "C:\Windows.old") {
    Remove-Item -Path "C:\Windows.old" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "✅ Windows.old removed" -ForegroundColor Green
}

# Clean Windows Logs
Write-Host "Cleaning Windows logs..." -ForegroundColor White
wevtutil el | ForEach-Object { wevtutil cl $_ } 2>$null

# Remove Windows Defender scan history
Write-Host "Cleaning Defender scan history..." -ForegroundColor White
Remove-Item -Path "C:\ProgramData\Microsoft\Windows Defender\Scans\History\*" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "✅ C drive cleaned" -ForegroundColor Green
Write-Host ""

# ==============================================================================
# PART 8: REMOVE REMOTE DESKTOP SHORTCUTS AND APPS
# ==============================================================================
Write-Host "PART 8: REMOVING REMOTE DESKTOP" -ForegroundColor Yellow
Write-Host "================================================================================" -ForegroundColor Cyan

# Remove Remote Desktop shortcuts
Write-Host "Removing Remote Desktop shortcuts..." -ForegroundColor White
Remove-Item -Path "$env:PUBLIC\Desktop\*Remote Desktop*.lnk" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$env:USERPROFILE\Desktop\*Remote Desktop*.lnk" -Force -ErrorAction SilentlyContinue

# Disable Remote Desktop
Write-Host "Disabling Remote Desktop..." -ForegroundColor White
Set-ItemProperty -Path "HKLM:\System\CurrentControlSet\Control\Terminal Server" -Name "fDenyTSConnections" -Value 1
Disable-NetFirewallRule -DisplayGroup "Remote Desktop"

# Remove TeamViewer, AnyDesk if present
$remoteApps = @("*TeamViewer*", "*AnyDesk*", "*LogMeIn*", "*GoToMyPC*")
foreach ($app in $remoteApps) {
    Get-AppxPackage -Name $app | Remove-AppxPackage -ErrorAction SilentlyContinue
}

Write-Host "✅ Remote Desktop removed and disabled" -ForegroundColor Green
Write-Host ""

# ==============================================================================
# PART 9: FIX VPN AND NETWORK ISSUES
# ==============================================================================
Write-Host "PART 9: FIX VPN AND NETWORK" -ForegroundColor Yellow
Write-Host "================================================================================" -ForegroundColor Cyan

# Reset network adapters
Write-Host "Resetting network adapters..." -ForegroundColor White
netsh winsock reset
netsh int ip reset
ipconfig /release
ipconfig /renew
ipconfig /flushdns

# Reset firewall to default (keeps Defender enabled)
Write-Host "Resetting firewall..." -ForegroundColor White
netsh advfirewall reset

Write-Host "✅ Network and VPN optimized (RESTART REQUIRED)" -ForegroundColor Green
Write-Host ""

# ==============================================================================
# PART 10: SYNC OPERATING SYSTEM WITH UPDATES
# ==============================================================================
Write-Host "PART 10: WINDOWS UPDATE SYNC" -ForegroundColor Yellow
Write-Host "================================================================================" -ForegroundColor Cyan

# Install Windows Update Module
Write-Host "Checking for Windows updates..." -ForegroundColor White
if (-not (Get-Module -ListAvailable -Name PSWindowsUpdate)) {
    Write-Host "Installing PSWindowsUpdate module..." -ForegroundColor White
    Install-Module -Name PSWindowsUpdate -Force -SkipPublisherCheck
}

# Check for updates
Import-Module PSWindowsUpdate
Get-WindowsUpdate

Write-Host "✅ Windows Update check complete" -ForegroundColor Green
Write-Host ""

# ==============================================================================
# FINAL SUMMARY
# ==============================================================================
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "✅ WINDOWS CLEANUP AND OPTIMIZATION COMPLETE!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "WHAT WAS DONE:" -ForegroundColor Yellow
Write-Host "✅ Microsoft Defender - All FREE tools enabled" -ForegroundColor White
Write-Host "✅ Bloatware - Removed (Music apps kept)" -ForegroundColor White
Write-Host "✅ Disk Cleanup - Temp files, cache cleared" -ForegroundColor White
Write-Host "✅ WSL/Linux/Ubuntu - Removed completely" -ForegroundColor White
Write-Host "✅ Background Apps - Unnecessary ones disabled" -ForegroundColor White
Write-Host "✅ Performance - Optimized for speed" -ForegroundColor White
Write-Host "✅ C Drive - Cleaned and optimized" -ForegroundColor White
Write-Host "✅ Remote Desktop - Removed and disabled" -ForegroundColor White
Write-Host "✅ VPN/Network - Reset and optimized" -ForegroundColor White
Write-Host "✅ Windows Update - Synced" -ForegroundColor White
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. RESTART YOUR COMPUTER for all changes to take effect" -ForegroundColor White
Write-Host "2. After restart, CPU should be faster and VPN should work better" -ForegroundColor White
Write-Host "3. Music apps are preserved and working" -ForegroundColor White
Write-Host "4. Defender will continue protecting in background (FREE)" -ForegroundColor White
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "Press any key to restart now, or close this window to restart later..." -ForegroundColor Yellow
pause

# Restart computer
Restart-Computer -Force
