@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM Change to script directory
cd /d "%~dp0"
title Glamour Salon - Quick Start

echo 🚀 Starting Glamour Salon...
echo ========================================

REM Pick Python executable
set "PY=python"
where python >nul 2>&1
if %errorlevel% neq 0 (
    where py >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ Python not found in PATH. Please install Python 3.7+
        pause
        exit /b 1
    ) else (
        set "PY=py -3"
    )
)

REM Activate virtual environment if present
if exist ".venv\Scripts\activate.bat" call ".venv\Scripts\activate.bat"
if exist "venv\Scripts\activate.bat" call "venv\Scripts\activate.bat"
if exist "env\Scripts\activate.bat"  call "env\Scripts\activate.bat"

REM Ensure required packages
echo 🔍 Checking dependencies...
%PY% -m pip show streamlit >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Installing requirements...
    %PY% -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Initialize database
echo 🔧 Initializing database...
%PY% -c "from app_restored import init_db; init_db(); print('✅ Database initialized')"
if %errorlevel% neq 0 (
    echo ❌ Database initialization failed
    pause
    exit /b 1
)

echo.
echo 🎨 Launching Glamour Salon (Streamlit)...
echo Visit http://localhost:8501 if the browser does not open automatically.
echo.

REM Run the app
%PY% -m streamlit run app_restored.py

echo.
echo 👋 Application stopped.
pause
endlocal
