@echo off
REM AI Gateway stop script for Windows

setlocal enabledelayedexpansion

cd /d "%~dp0"

REM Run dependency checks using unified function
call src\script_init.bat init_script_with_checks stop "Stopping AI Gateway" "🛑"
if %ERRORLEVEL% NEQ 0 (
    pause
    exit /b 1
)

REM Determine command
set COMPOSE_CMD=docker compose

REM Check docker-compose.override.yml
if exist "docker-compose.override.yml" (
    set COMPOSE_CMD=docker compose -f docker-compose.yml -f docker-compose.override.yml
) else (
    set COMPOSE_CMD=docker compose -f docker-compose.yml
)

REM Check running containers
%COMPOSE_CMD% ps -q >nul 2>&1
if %errorlevel% neq 0 (
    echo ℹ️  No running containers
    echo.
    echo Containers are already stopped or were not started.
    pause
    exit /b 0
)

echo 📋 Running containers:
%COMPOSE_CMD% ps
echo.

REM Confirm stop
set /p CONFIRM="Stop all containers? [Y/n]: "
if /i "%CONFIRM%"=="n" (
    echo Stop cancelled
    pause
    exit /b 0
)

echo.
echo 🛑 Stopping containers...
echo.

REM Stop containers
%COMPOSE_CMD% down

if %errorlevel% equ 0 (
    echo.
    echo ✅ Containers stopped!
    echo.
    
    REM Optionally: remove volumes
    set /p REMOVE_VOLUMES="Remove volumes (data will be lost)? [y/N]: "
    if /i "!REMOVE_VOLUMES!"=="y" (
        echo.
        echo ⚠️  Removing volumes...
        %COMPOSE_CMD% down -v
        echo ✅ Volumes removed
    )
) else (
    echo.
    echo ❌ Error stopping containers
    pause
    exit /b 1
)

echo.
echo 💡 To start use:
echo   start.bat
echo.
pause

