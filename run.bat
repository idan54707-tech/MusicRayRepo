@echo off
echo Starting musicRay Backend Server...

REM בדיקה אם virtual environment קיים
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment לא נמצא. הרץ קודם install.bat
    pause
    exit /b 1
)

REM הפעלת virtual environment
call venv\Scripts\activate.bat

REM בדיקה אם uvicorn מותקן
python -c "import uvicorn" >nul 2>&1
if errorlevel 1 (
    echo ERROR: uvicorn לא מותקן. הרץ קודם install.bat
    pause
    exit /b 1
)

REM יצירת תיקיית storage
if not exist "storage" mkdir storage

echo.
echo 🚀 מריץ שרת musicRay על http://localhost:8000
echo לעצירה: לחץ Ctrl+C
echo.

REM הרצת השרת
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
