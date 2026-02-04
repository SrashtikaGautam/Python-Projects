@echo off
REM Batch script to run the Glamour Salon application on Windows

title Glamour Salon Application

echo 🚀 Starting Glamour Salon Application...
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.7 or higher
    echo.
    pause
    exit /b 1
)

REM Check if required packages are installed
echo 🔍 Checking required packages...
pip show streamlit >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Streamlit not found. Installing requirements...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ Failed to install requirements
        pause
        exit /b 1
    )
)

REM Initialize database
echo 🔧 Initializing database...
python -c "from app_restored import init_db; init_db(); print('✅ Database initialized')"
if %errorlevel% neq 0 (
    echo ❌ Failed to initialize database
    pause
    exit /b 1
)

echo.
echo 🎨 Launching Glamour Salon Application...
echo ========================================
echo The app will open in your browser shortly.
echo Press Ctrl+C in this window to stop the application.
echo.
echo Note: If the browser doesn't open automatically, visit http://localhost:8501
echo.

REM Run the Streamlit application
python -m streamlit run app_restored.py

pause