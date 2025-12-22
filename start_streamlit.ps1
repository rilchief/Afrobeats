#!/usr/bin/env pwsh
# Launch Streamlit Dashboard for Afrobeats Playlist Observatory

Write-Host "Starting Afrobeats Playlist Observatory - Streamlit Dashboard" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Dashboard will open at: http://localhost:8501/" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

Set-Location "$PSScriptRoot"
& "C:\Users\Rilwan\AppData\Local\Microsoft\WindowsApps\python3.13.exe" -m streamlit run scripts\dashboard.py
