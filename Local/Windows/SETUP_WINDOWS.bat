@echo off
echo ==========================================
echo      WHATSAPP AUTOMATION SETUP
echo ==========================================
echo.

REM Check for Winget (Windows Package Manager)
winget --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Winget not found. Please update Windows App Installer from Microsoft Store.
    echo Falling back to manual checks...
) else (
    echo Checking for Python...
    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo Python not found. Installing Python 3.11...
        winget install -e --id Python.Python.3.11 --scope machine
        echo Please restart this script after Python installation completes!
        pause
        exit /b
    ) else (
        echo Python is already installed.
    )

    echo.
    echo Checking for Google Chrome...
    if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
        echo Chrome is already installed.
    ) else (
        if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
            echo Chrome is already installed.
        ) else (
            echo Chrome not found. Installing Google Chrome...
            winget install -e --id Google.Chrome
        )
    )
)

echo.
echo Installing Python dependencies...

if not exist "requirements.txt" (
    echo ❌ Error: Cannot find requirements.txt
    echo ⚠️  Make sure you are running this script from inside the folder!
    pause
    exit /b
)

pip install -r requirements.txt

echo.
echo ==========================================
echo      SETUP COMPLETE!
echo ==========================================
echo.
echo You can now run "RUN_WINDOWS.bat" to start the app.
echo.
pause
