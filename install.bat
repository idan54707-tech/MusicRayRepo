@echo off
echo Installing musicRay Backend...

REM בדיקה אם Python מותקן
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python לא מותקן. אנא התקן Python 3.8+ מ-https://python.org
    pause
    exit /b 1
)

echo Python נמצא, מתקין תלויות...

REM יצירת virtual environment
if not exist "venv" (
    echo יוצר virtual environment...
    python -m venv venv
)

REM הפעלת virtual environment
call venv\Scripts\activate.bat

REM שדרוג pip
echo משדרג pip...
python -m pip install --upgrade pip

REM התקנת תלויות (CPU version)
echo מתקין תלויות...
pip install -r requirements-cpu.txt

echo.
echo ✅ התקנה הושלמה בהצלחה!
echo.
echo להרצת השרת:
echo   1. הפעל: venv\Scripts\activate.bat
echo   2. הרץ: python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
echo.
pause
