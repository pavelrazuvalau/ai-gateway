@echo off
REM Common initialization module for Windows batch scripts
REM Usage: call src\script_init.bat init_script_with_checks <script_type> <script_name> <emoji>
REM Example: call src\script_init.bat init_script_with_checks start "Starting AI Gateway" "🚀"

setlocal enabledelayedexpansion

if "%1"=="init_script_with_checks" goto :init_script_with_checks
goto :eof

:init_script_with_checks
REM Universal function to initialize script with dependency checks
REM Parameters: script_type script_name emoji
set SCRIPT_TYPE=%~2
set SCRIPT_NAME=%~3
set EMOJI=%~4
if "!EMOJI!"=="" set EMOJI=🚀

REM Check Python before calling Python check module
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found!
    echo.
    echo Python is required for unified dependency checks.
    echo Please install Python 3.8+ or use fallback checks.
    echo.
    REM Fallback to simple checks
    call :fallback_checks "!SCRIPT_TYPE!" "!SCRIPT_NAME!" "!EMOJI!"
    if %ERRORLEVEL% NEQ 0 (
        exit /b 1
    )
) else (
    REM Initialize via unified Python module
    python src\check_dependencies.py "!SCRIPT_TYPE!" "!SCRIPT_NAME!" "!EMOJI!" 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo [ERROR] Dependency check failed!
        echo Fix errors and run the script again.
        exit /b 1
    )
)
exit /b 0

:fallback_checks
REM Fallback checks when Python is not available
set FALLBACK_TYPE=%~1
set FALLBACK_NAME=%~2
set FALLBACK_EMOJI=%~3

echo.
echo ============================================================
echo   !FALLBACK_EMOJI! !FALLBACK_NAME!
echo ============================================================
echo.

REM Check for .env file (for scripts that need it)
if "!FALLBACK_TYPE!"=="start" goto :check_env
if "!FALLBACK_TYPE!"=="test" goto :check_env
if "!FALLBACK_TYPE!"=="setup" goto :check_docker_only
goto :check_docker

:check_env
if not exist ".env" (
    echo [ERROR] .env file not found!
    echo.
    echo Configuration file is missing. Please run setup first:
    echo   setup.bat
    echo.
    exit /b 1
)
echo [OK] .env file found
echo.

:check_docker
REM Check for Docker (for scripts working with containers)
if "!FALLBACK_TYPE!"=="start" goto :check_docker_required
if "!FALLBACK_TYPE!"=="stop" goto :check_docker_required
if "!FALLBACK_TYPE!"=="monitoring" goto :check_docker_required
goto :fallback_done

:check_docker_required
where docker >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker not found!
    echo Please install Docker Desktop for Windows.
    exit /b 1
)

REM Check if Docker is running
docker ps >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker daemon is not running!
    echo Please start Docker Desktop.
    exit /b 1
)

echo [OK] Docker is ready
echo.

:check_docker_only
REM Only check Docker, not .env
where docker >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Docker not found!
    echo Docker is recommended but not required for setup.
    echo.
) else (
    docker ps >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [WARNING] Docker daemon is not running!
        echo Docker is recommended but not required for setup.
        echo.
    ) else (
        echo [OK] Docker is ready
        echo.
    )
)

:fallback_done
exit /b 0

