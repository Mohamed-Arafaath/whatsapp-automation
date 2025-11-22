@echo off
echo Starting WhatsApp Automation...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed! Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b
)

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Starting the application...
echo Open http://localhost:5001 in your browser
echo.

python app.py
pause
