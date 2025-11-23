@echo off
REM Virtual Key Setup Script for Windows
REM Wrapper for universal Python script

cd /d "%~dp0"

REM Check if .env exists
if not exist ".env" (
    echo [ERROR] .env file not found
    echo Run setup.bat first to generate configuration
    pause
    exit /b 1
)

REM Run the universal Python script
if exist "setup_virtual_key.py" (
    python setup_virtual_key.py
) else (
    REM Fallback to module import
    python -m src.setup_virtual_key
)

pause

