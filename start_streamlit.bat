@echo off
setlocal ENABLEDELAYEDEXPANSION

echo === Afrobeats Playlist Observatory - Streamlit Launcher ===
echo.

:: Determine port (allow override via STREAMLIT_PORT env or first arg)
set PORT=%STREAMLIT_PORT%
if "%PORT%"=="" set PORT=%1
if "%PORT%"=="" set PORT=8501

:: Resolve Python executable
set PY_EXE=C:\Users\Rilwan\AppData\Local\Microsoft\WindowsApps\python3.13.exe
if not exist "%PY_EXE%" (
	where python >nul 2>&1 && for /f "delims=" %%p in ('where python') do set PY_EXE=%%p
)

if not exist "%PY_EXE%" (
	echo [ERROR] Python executable not found. Install Python 3.11+ and re-run.
	goto :EOF
)

:: Check Streamlit availability
"%PY_EXE%" -c "import streamlit" 1>nul 2>nul
if errorlevel 1 (
	echo [INFO] Streamlit not found. Installing now...
	"%PY_EXE%" -m pip install --quiet streamlit || (
		echo [ERROR] Failed to install Streamlit. Exiting.
		goto :EOF
	)
)

echo Launching Streamlit on port %PORT% ...
echo URL: http://localhost:%PORT%
echo Press Ctrl+C in this window to stop.
echo.

"%PY_EXE%" -m streamlit run scripts\dashboard.py --server.port %PORT% --server.headless true

endlocal
