@echo off
setlocal
cd /d "%~dp0"

py -3 --version >nul 2>nul
if %errorlevel%==0 (
    set "PYTHON_CMD=py -3"
) else (
    python --version >nul 2>nul
    if errorlevel 1 (
        echo [ERROR] Python 3.10 or newer was not found.
        echo Install Python and enable "Add Python to PATH", then retry.
        pause
        exit /b 1
    )
    set "PYTHON_CMD=python"
)

%PYTHON_CMD% -c "import sys; raise SystemExit(sys.version_info[0] in range(3) or (sys.version_info[0] == 3 and sys.version_info[1] in range(10)))"
if errorlevel 1 (
    echo [ERROR] Python 3.10 or newer is required by FastMCP 2.x.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Creating virtual environment...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 goto :failed
) else (
    echo [1/3] Existing virtual environment found.
)

echo [2/3] Updating pip...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :failed

echo [3/3] Installing package and dependencies...
".venv\Scripts\python.exe" -m pip install -e .
if errorlevel 1 goto :failed

echo.
echo Installation completed.
echo Next: edit mcp.example.json and replace D:\YOUR_PATH.
pause
exit /b 0

:failed
echo.
echo [ERROR] Installation failed. Review the messages above.
pause
exit /b 1
