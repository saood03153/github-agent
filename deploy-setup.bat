@echo off
echo ========================================
echo GitHub Agent - Git Setup and Push
echo ========================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo Git is not installed!
    echo Installing Git...
    winget install Git.Git
    echo.
    echo Git installed! Please restart this script.
    pause
    exit /b 1
)

echo Step 1: Initializing Git repository...
git init

echo.
echo Step 2: Adding all files...
git add .

echo.
echo Step 3: Creating initial commit...
git commit -m "Initial commit - GitHub User Report Agent"

echo.
echo ========================================
echo Next Steps:
echo ========================================
echo 1. Create a new repository on GitHub:
echo    Visit: https://github.com/new
echo    Name: github-agent
echo    Make it PUBLIC
echo.
echo 2. Copy this command and replace YOUR_USERNAME:
echo.
echo    git remote add origin https://github.com/YOUR_USERNAME/github-agent.git
echo    git branch -M main
echo    git push -u origin main
echo.
echo 3. Then go to: https://share.streamlit.io
echo    - Sign in with GitHub
echo    - Click "New app"
echo    - Select your repository
echo    - Add GROQ_API_KEY in Advanced settings ^> Secrets
echo    - Deploy!
echo.
echo ========================================
pause
