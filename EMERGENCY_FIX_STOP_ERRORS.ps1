# EMERGENCY FIX - STOP ALL AGENT PROCESSES
# =========================================
# Run this immediately to stop all Python/Agent processes causing issues

Write-Host "========================================" -ForegroundColor Red
Write-Host "EMERGENCY FIX - STOPPING ALL AGENTS" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""

# Stop all Python processes
Write-Host "Stopping all Python processes..." -ForegroundColor Yellow
Get-Process python* -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process pythonw* -ErrorAction SilentlyContinue | Stop-Process -Force

# Stop any AgentX processes
Write-Host "Stopping AgentX processes..." -ForegroundColor Yellow
Get-Process *agent* -ErrorAction SilentlyContinue | Stop-Process -Force

# Stop any background tasks
Write-Host "Stopping scheduled tasks..." -ForegroundColor Yellow
Get-ScheduledTask | Where-Object {$_.TaskName -like "*agent*" -or $_.TaskName -like "*python*"} | Stop-ScheduledTask -ErrorAction SilentlyContinue

# Kill any stuck PowerShell windows
Write-Host "Closing extra PowerShell windows..." -ForegroundColor Yellow
Get-Process powershell -ErrorAction SilentlyContinue | Where-Object {$_.Id -ne $PID} | Stop-Process -Force

# Clear temp files
Write-Host "Clearing temp files..." -ForegroundColor Yellow
Remove-Item -Path "$env:TEMP\*agent*" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$env:TEMP\*python*" -Recurse -Force -ErrorAction SilentlyContinue

# Stop Windows Speech (text-to-speech)
Write-Host "Stopping text-to-speech..." -ForegroundColor Yellow
Get-Process -Name "TextInputHost" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "narrator" -ErrorAction SilentlyContinue | Stop-Process -Force

# Check CPU usage
Write-Host ""
Write-Host "Checking CPU usage..." -ForegroundColor Green
Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 ProcessName, CPU, Id | Format-Table

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "EMERGENCY FIX COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "All agent processes have been stopped." -ForegroundColor Green
Write-Host "Your CPU should return to normal now." -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Close any remaining black windows" -ForegroundColor White
Write-Host "2. Run the REMEDIATION_PLAN.ps1 script" -ForegroundColor White
Write-Host "3. DO NOT run any agent scripts until fixed" -ForegroundColor White

Pause
