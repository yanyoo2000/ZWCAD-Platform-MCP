@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python launcher not found. Install Python 3.9+ first.
  exit /b 1
)
py -3 -m venv .venv
if errorlevel 1 exit /b 1
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 exit /b 1
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 exit /b 1
echo Installation complete. Run start.bat or configure WorkBuddy with workbuddy-mcp.json.
endlocal
