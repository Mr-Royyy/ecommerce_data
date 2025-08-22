@echo off
REM ==============================================
REM Ecommerce Brazil Data Analysis - Full Launch
REM ==============================================

echo 🔹 Activating virtual environment...
call venv\Scripts\activate.bat

echo 🔹 Running ETL pipeline...
python -m orchestration.etl_flow
if %ERRORLEVEL% NEQ 0 (
    echo ❌ ETL failed. Exiting.
    pause
    exit /b %ERRORLEVEL%
)

echo 🔹 Launching dashboard...
streamlit run dashboard\app.py

pause
