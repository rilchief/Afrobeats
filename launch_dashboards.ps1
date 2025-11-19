# Dashboard Launcher Scripts
# Save time with one-click dashboard launching

Write-Host "🎵 Afrobeats Observatory Dashboard Launcher" -ForegroundColor Cyan
Write-Host ""
Write-Host "Choose your dashboard:" -ForegroundColor Yellow
Write-Host "1. Enhanced Streamlit Dashboard (Recommended)" -ForegroundColor Green
Write-Host "2. Plotly Dash Dashboard (Production)" -ForegroundColor Green
Write-Host "3. Launch Both Dashboards" -ForegroundColor Green
Write-Host ""

$choice = Read-Host "Enter choice (1, 2, or 3)"

$projectRoot = "c:\Users\Rilwan\OneDrive\DATA SCIENCE COURSE\Newtest"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "🚀 Launching Enhanced Streamlit Dashboard..." -ForegroundColor Cyan
        Write-Host "📍 URL: http://localhost:8501" -ForegroundColor Yellow
        Write-Host "⌨️  Press Ctrl+C to stop" -ForegroundColor Magenta
        Write-Host ""
        cd $projectRoot
        streamlit run scripts/dashboard.py
    }
    "2" {
        Write-Host ""
        Write-Host "🚀 Launching Plotly Dash Dashboard..." -ForegroundColor Cyan
        Write-Host "📍 URL: http://localhost:8050" -ForegroundColor Yellow
        Write-Host "⌨️  Press Ctrl+C to stop" -ForegroundColor Magenta
        Write-Host ""
        cd $projectRoot
        python scripts/dashboard_dash.py
    }
    "3" {
        Write-Host ""
        Write-Host "🚀 Launching Both Dashboards..." -ForegroundColor Cyan
        Write-Host "📍 Streamlit: http://localhost:8501" -ForegroundColor Yellow
        Write-Host "📍 Dash: http://localhost:8050" -ForegroundColor Yellow
        Write-Host "⌨️  Close this window to stop both" -ForegroundColor Magenta
        Write-Host ""
        
        cd $projectRoot
        
        # Launch Streamlit in background
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "streamlit run scripts/dashboard.py"
        
        # Wait a moment
        Start-Sleep -Seconds 2
        
        # Launch Dash in current window
        python scripts/dashboard_dash.py
    }
    default {
        Write-Host "❌ Invalid choice. Please run again and select 1, 2, or 3." -ForegroundColor Red
    }
}
