@echo off
REM Virtual Key Setup Script for Windows
REM Wrapper for Python module

setlocal enabledelayedexpansion

cd /d "%~dp0"

REM Run dependency checks using unified function
call src\script_init.bat init_script_with_checks setup "Virtual Key Setup" "🔑"
if %ERRORLEVEL% NEQ 0 (
    pause
    exit /b 1
)

REM Check if .env exists
if not exist ".env" (
    echo [ERROR] .env file not found
    echo Run setup.bat first to generate configuration
    pause
    exit /b 1
)

REM Run the Python module
python -m src.virtual_key

pause

