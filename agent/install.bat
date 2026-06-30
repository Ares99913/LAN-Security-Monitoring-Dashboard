@echo off
cd /d "%~dp0"

echo ============================
echo   509 Server Agent Install
echo ============================

python --version >nul 2>&1
if errorlevel 1 (
    py --version >nul 2>&1
    if errorlevel 1 (
        echo Python not install.
        pause
        exit /b 1
    )
    py -m pip install psutil requests
    echo.
    echo Agent Starting...
    py agent.py
) else (
    python -m pip install psutil requests
    echo.
    echo Agent Starting...
    python agent.py
)

pause