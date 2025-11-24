@echo off
REM AI Gateway Start Script for Windows
REM Checks configuration and starts containers

setlocal enabledelayedexpansion

cd /d "%~dp0"

REM Check Python before calling Python check module
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found!
    echo.
    echo Python is required for unified dependency checks.
    echo Please install Python 3.8+ or use fallback checks.
    echo.
    REM Fallback to simple checks
    goto :fallback_checks
)

REM Initialize via unified Python module
python src\check_dependencies.py start "Starting AI Gateway" "🚀" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Dependency check failed!
    echo Fix errors and run the script again.
    pause
    exit /b 1
)
goto :continue

:fallback_checks
echo.
echo ============================================================
echo   AI Gateway - Starting Services
echo ============================================================
echo.

REM Check for .env file
if not exist ".env" (
    echo [ERROR] .env file not found!
    echo.
    echo Configuration file is missing. Please run setup first:
    echo   setup.bat
    echo.
    pause
    exit /b 1
)

echo [OK] .env file found
echo.

REM Check for Docker
where docker >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker not found!
    echo Please install Docker Desktop for Windows.
    pause
    exit /b 1
)

REM Check if Docker is running
docker ps >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker daemon is not running!
    echo Please start Docker Desktop.
    pause
    exit /b 1
)

echo [OK] Docker is ready
echo.

:continue

REM Check for docker-compose.override.yml
set COMPOSE_CMD=docker compose
if exist "docker-compose.override.yml" (
    echo [INFO] Using docker-compose.override.yml with your settings
    set COMPOSE_CMD=!COMPOSE_CMD! -f docker-compose.yml -f docker-compose.override.yml
) else (
    set COMPOSE_CMD=!COMPOSE_CMD! -f docker-compose.yml
)

echo.
echo Starting containers...
echo.

%COMPOSE_CMD% up -d

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to start containers
    pause
    exit /b 1
)

echo.
echo [OK] Containers started!
echo.

REM Determine access URLs
findstr /C:"USE_NGINX=yes" .env >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    for /f "tokens=2 delims==" %%i in ('findstr /C:"LITELLM_EXTERNAL_PORT=" .env') do set LITELLM_UI_PORT=%%i
    if not defined LITELLM_UI_PORT set LITELLM_UI_PORT=4000
    
    findstr /C:"USE_SSL=yes" .env >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        for /f "tokens=2 delims==" %%i in ('findstr /C:"SSL_DOMAIN=" .env') do set SSL_DOMAIN=%%i
        if defined SSL_DOMAIN (
            echo Access URLs (HTTPS):
            echo   https://!SSL_DOMAIN! - Open WebUI
            echo   https://!SSL_DOMAIN!/api/litellm/ - LiteLLM API
            echo   https://!SSL_DOMAIN!/api/litellm/ui/ - LiteLLM Admin UI (via nginx)
            echo   https://!SSL_DOMAIN!:!LITELLM_UI_PORT!/ui/ - LiteLLM Admin UI (direct access)
            echo.
            echo For VPS with different virtual hosts:
            echo   https://webui.!SSL_DOMAIN! - Open WebUI (if separate vhost configured)
            echo   https://litellm.!SSL_DOMAIN! - LiteLLM (if separate vhost configured)
        )
    ) else (
        for /f "tokens=2 delims==" %%i in ('findstr /C:"NGINX_PORT=" .env') do set NGINX_PORT=%%i
        if not defined NGINX_PORT set NGINX_PORT=80
        if defined NGINX_PORT (
            echo Access URLs (HTTP):
            echo   http://localhost:!NGINX_PORT! - Open WebUI
            echo   http://localhost:!NGINX_PORT!/api/litellm/ - LiteLLM API
            echo   http://localhost:!NGINX_PORT!/api/litellm/ui/ - LiteLLM Admin UI (via nginx)
            echo   http://localhost:!LITELLM_UI_PORT!/ui/ - LiteLLM Admin UI (direct access)
            echo.
            echo For VPS (replace localhost with IP or domain):
            echo   http://YOUR_VPS_IP:!NGINX_PORT! - Open WebUI
            echo   http://YOUR_VPS_IP:!NGINX_PORT!/api/litellm/ - LiteLLM API
            echo   http://YOUR_VPS_IP:!LITELLM_UI_PORT!/ui/ - LiteLLM Admin UI
            echo.
            echo For VPS with different virtual hosts:
            echo   http://webui.YOUR_DOMAIN:!NGINX_PORT! - Open WebUI (if separate vhost configured)
            echo   http://litellm.YOUR_DOMAIN:!NGINX_PORT! - LiteLLM (if separate vhost configured)
        )
    )
) else (
    for /f "tokens=2 delims==" %%i in ('findstr /C:"WEBUI_EXTERNAL_PORT=" .env') do set WEBUI_PORT=%%i
    for /f "tokens=2 delims==" %%i in ('findstr /C:"LITELLM_EXTERNAL_PORT=" .env') do set LITELLM_PORT=%%i
    if not defined WEBUI_PORT set WEBUI_PORT=3000
    if not defined LITELLM_PORT set LITELLM_PORT=4000
    if defined WEBUI_PORT (
        echo Access URLs (without nginx):
        echo   http://localhost:!WEBUI_PORT! - Open WebUI
    )
    if defined LITELLM_PORT (
        echo   http://localhost:!LITELLM_PORT! - LiteLLM API
        echo   http://localhost:!LITELLM_PORT!/ui/ - LiteLLM Admin UI
    )
    echo.
    echo For VPS (replace localhost with IP or domain):
    echo   http://YOUR_VPS_IP:!WEBUI_PORT! - Open WebUI
    echo   http://YOUR_VPS_IP:!LITELLM_PORT! - LiteLLM API
    echo   http://YOUR_VPS_IP:!LITELLM_PORT!/ui/ - LiteLLM Admin UI
)

echo.
echo Useful commands:
echo   docker compose ps          - Check container status
echo   docker compose logs -f     - View logs
echo   docker compose down        - Stop containers
echo.
pause

