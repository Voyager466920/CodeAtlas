@echo off
echo Starting File Structure Visualization Tool...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Please install Python 3.8 or higher.
    pause
    exit /b
)

REM Install dependencies if needed (optional, can be commented out to speed up start)
REM pip install -r backend/requirements.txt

REM Run the backend
set PYTHONPATH=%CD%
python backend/main.py

pause
