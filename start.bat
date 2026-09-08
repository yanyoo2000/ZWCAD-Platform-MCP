@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] .venv is missing. Run install.bat first.
    pause
    exit /b 1
)

set "PYTHONUTF8=1"
echo Starting ZWCAD-2D MCP Server...
echo This is a stdio server; waiting without a web page is normal.
".venv\Scripts\python.exe" -m zwcad2d

if errorlevel 1 (
    echo.
    echo [ERROR] The server exited unexpectedly.
    pause
)
