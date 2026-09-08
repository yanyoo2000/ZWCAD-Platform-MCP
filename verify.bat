@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] .venv is missing. Run install.bat first.
    pause
    exit /b 1
)

echo [0/3] Ensuring editable install is up to date...
".venv\Scripts\python.exe" -m pip install -e .
if errorlevel 1 (
    echo.
    echo [ERROR] Editable install failed.
    pause
    exit /b 1
)

echo [1/3] Running unit tests...
".venv\Scripts\python.exe" -m unittest discover -s tests -v
if errorlevel 1 (
    echo.
    echo [ERROR] Verification failed.
    pause
    exit /b 1
)

echo [2/3] Running MCP stdio smoke test...
".venv\Scripts\python.exe" "tests\smoke_stdio.py"
if errorlevel 1 (
    echo.
    echo [ERROR] MCP stdio smoke test failed.
    pause
    exit /b 1
)

echo.
echo [3/3] Static and stdio verification passed. CAD tests must be run from an MCP client.
pause
