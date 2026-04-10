@echo off
echo ========================================
echo GitHub User Report Agent Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Python found!
echo.

REM Check if .env exists
if not exist .env (
    echo [2/4] Creating .env file from template...
    copy .env.example .env
    echo.
    echo IMPORTANT: Your GROQ_API_KEY is already set!
    echo If you need to change it, get a new key from: https://console.groq.com/keys
    echo.
) else (
    echo [2/4] .env file already exists
)

echo.
echo [3/4] Installing dependencies (this may take a minute)...
pip install -r requirements.txt

echo.
echo [4/4] Setup complete!
echo.
echo ========================================
echo Next Steps:
echo ========================================
echo 1. Your API key is ready!
echo 2. Run: run.bat
echo 3. App will open automatically in your browser
echo 4. Enter any GitHub username to analyze
echo ========================================
echo.
pause
