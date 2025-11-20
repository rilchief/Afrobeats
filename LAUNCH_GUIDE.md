# Quick Launch Guide

## Launch Streamlit Dashboard

### Option 1: Double-click the launcher (Easiest)
Simply double-click `start_streamlit.bat` in File Explorer.

### Option 2: From PowerShell or Command Prompt
```powershell
.\start_streamlit.bat
```

### Option 3: Direct command
```powershell
python -m streamlit run scripts\dashboard.py
```

The dashboard will automatically open in your browser at http://localhost:8501

---

## Launch Static Web Dashboard

### Option 1: Double-click the launcher
Double-click `start_web_dashboard.bat` in File Explorer.

### Option 2: Direct command
```powershell
cd web
python -m http.server 8000
```

Then navigate to http://localhost:8000/index.html in your browser.

---

## Stopping the Servers

Press `Ctrl+C` in the terminal window where the server is running.

---

## Troubleshooting

**Port already in use?**
```powershell
# For Streamlit (use different port)
streamlit run scripts\dashboard.py --server.port 8502

# For web server (use different port)
python -m http.server 9000
```

**Python not found?**
Ensure Python 3.13+ is installed and accessible. The launcher auto-detects `python3.13.exe` but will fall back to the first `python` found on `PATH`.

---

## Desktop Shortcut (Optional)

To create a desktop shortcut:
1. Right-click `start_streamlit.bat`
2. Select "Send to" → "Desktop (create shortcut)"
3. Rename the shortcut to "Afrobeats Dashboard"
4. (Optional) Right-click → Properties → Change icon for custom appearance

Now you can launch the dashboard directly from your desktop!
