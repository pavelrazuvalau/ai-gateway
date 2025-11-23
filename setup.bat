@echo off
REM AI Gateway Setup Script for Windows
REM Checks for Python and guides installation if needed

setlocal enabledelayedexpansion

echo.
echo ============================================================
echo   AI Gateway Setup - Windows
echo ============================================================
echo.

REM Check for Python
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Python found
    python --version
    goto :check_version
)

where python3 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Python 3 found
    python3 --version
    goto :check_version
)

REM Python not found
echo [ERROR] Python not found!
echo.
echo Python 3.8+ is required to run the setup script.
echo.
echo Installation options:
echo   1. Download installer automatically (recommended)
echo      This script will download Python installer to current directory
echo.
echo   2. Download from python.org manually
echo      https://www.python.org/downloads/windows/
echo.
echo   3. Install via Microsoft Store
echo      Search for "Python 3.11" in Microsoft Store
echo.
echo   4. Install via winget (if available)
echo      winget install Python.Python.3.11
echo.
set /p DOWNLOAD_CHOICE="Download Python installer automatically? [Y/n]: "
if /i "!DOWNLOAD_CHOICE!" NEQ "n" (
    echo.
    echo [INFO] Downloading Python installer using PowerShell...
    echo.
    
    REM Use PowerShell to download (built-in on Windows, no Python needed)
    powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $url = 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe'; $output = 'python-3.11.9-amd64.exe'; Write-Host '[INFO] Downloading from:' $url; $ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri $url -OutFile $output -UseBasicParsing; if (Test-Path $output) { Write-Host '[OK] Downloaded:' $output; Write-Host '[OK] File size:' ((Get-Item $output).Length / 1MB).ToString('F2') 'MB' } else { Write-Host '[ERROR] Download failed' } } catch { Write-Host '[ERROR] Download error:' $_.Exception.Message }"
    
    if exist "python-3.11.9-amd64.exe" (
        echo.
        echo [OK] Python installer downloaded: python-3.11.9-amd64.exe
        echo.
        set /p RUN_INSTALLER="Run installer now? [Y/n]: "
        if /i "!RUN_INSTALLER!" NEQ "n" (
            echo.
            echo IMPORTANT: Check "Add Python to PATH" during installation!
            echo.
            start /wait python-3.11.9-amd64.exe
        ) else (
            echo.
            echo To install later, run: python-3.11.9-amd64.exe
            echo IMPORTANT: Check "Add Python to PATH" during installation!
        )
        echo.
        echo After installing Python:
        echo   1. Close and reopen this terminal/command prompt
        echo   2. Run this script again: setup.bat
        echo.
        pause
        exit /b 1
    ) else (
        echo.
        echo [WARNING] Automatic download failed
        echo Opening download page in browser...
        start https://www.python.org/downloads/windows/
    )
) else (
    echo.
    set /p OPEN_BROWSER="Open Python download page in browser? [Y/n]: "
    if /i "!OPEN_BROWSER!" NEQ "n" (
        start https://www.python.org/downloads/windows/
    )
)

echo.
echo IMPORTANT: During installation, check "Add Python to PATH"
echo.
echo After installing Python:
echo   1. Close and reopen this terminal/command prompt
echo   2. Run this script again: setup.bat
echo.
pause
exit /b 1

:check_version
REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
if not defined PYTHON_VERSION (
    for /f "tokens=2" %%i in ('python3 --version 2^>^&1') do set PYTHON_VERSION=%%i
)

echo.
echo Checking Python version: !PYTHON_VERSION!
echo.

REM Extract major and minor version
for /f "tokens=1,2 delims=." %%a in ("!PYTHON_VERSION!") do (
    set MAJOR=%%a
    set MINOR=%%b
)

REM Remove leading/trailing spaces
set MAJOR=!MAJOR: =!
set MINOR=!MINOR: =!

if !MAJOR! LSS 3 (
    echo [ERROR] Python 3.8+ required, found version !PYTHON_VERSION!
    echo Please install Python 3.8 or higher.
    pause
    exit /b 1
)

if !MAJOR! EQU 3 (
    if !MINOR! LSS 8 (
        echo [ERROR] Python 3.8+ required, found version !PYTHON_VERSION!
        echo Please install Python 3.8 or higher.
        pause
        exit /b 1
    )
)

echo [OK] Python version is compatible
echo.

REM Check for Docker
where docker >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Docker not found!
    echo.
    echo Docker is required to run the containers.
    echo.
    echo Installation:
    echo   1. Download Docker Desktop for Windows:
    echo      https://www.docker.com/products/docker-desktop
    echo   2. Install and start Docker Desktop
    echo   3. Make sure Docker Desktop is running (check system tray)
    echo.
    echo Alternative: Use WSL2 with Docker
    echo   1. Install WSL2: wsl --install
    echo   2. In WSL, install Docker: curl -fsSL https://get.docker.com ^| sh
    echo.
    set /p DOCKER_NOW="Open Docker download page? [Y/n]: "
    if /i "!DOCKER_NOW!" NEQ "n" (
        start https://www.docker.com/products/docker-desktop
    )
    echo.
    pause
    exit /b 1
)

echo [OK] Docker found
docker --version
echo.

REM Check if Docker is running
docker ps >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Docker daemon is not running!
    echo.
    echo Please start Docker Desktop and make sure it's running.
    echo Check the system tray for Docker icon.
    echo.
    pause
    exit /b 1
)

echo [OK] Docker daemon is running
echo.

REM Run Python setup script
echo ============================================================
echo   Running Python setup script...
echo ============================================================
echo.

REM Run setup via CLI entry point
REM Use ai-gateway script (standard production practice)
python ai-gateway setup
if %ERRORLEVEL% NEQ 0 (
    python3 ai-gateway setup
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to run setup
        echo Make sure Python is installed and in PATH
        pause
        exit /b 1
    )
)

echo.
echo ============================================================
echo   Setup completed!
echo ============================================================
echo.
echo Next steps:
echo   1. Run: start.bat
echo   2. Access URLs will be shown after containers start
echo   3. Configure providers, API keys, and models via LiteLLM Admin UI
echo.
pause

