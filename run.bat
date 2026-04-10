@echo off
echo ========================================
echo Starting GitHub User Report Agent...
echo ========================================
echo.

REM Check if .env exists
if not exist .env (
    echo ERROR: .env file not found!
    echo Please copy .env.example to .env and add your API key
    pause
    exit /b 1
)

REM Check if GROQ_API_KEY is set (basic check)
findstr /C:"GROQ_API_KEY=your_groq_api_key_here" .env >nul
if not errorlevel 1 (
    echo WARNING: Please set your GROQ_API_KEY in .env file!
    echo Get your API key from: https://console.groq.com/keys
    echo.
    pause
)

echo Starting Streamlit app...
echo.
echo The app will open automatically in your browser
echo Press Ctrl+C to stop the server
echo.
streamlit run streamlit_app.py
