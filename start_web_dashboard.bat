@echo off
echo Starting Afrobeats Playlist Observatory - Static Web Dashboard
echo ============================================================
echo.
echo Dashboard will open at: http://localhost:8000/index.html
echo Press Ctrl+C to stop the server
echo.

cd web
C:\Users\Rilwan\AppData\Local\Microsoft\WindowsApps\python3.13.exe -m http.server 8000

pause
