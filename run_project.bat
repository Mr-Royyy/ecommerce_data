@echo off
REM =====================================================
REM  E-Commerce Brazil Data Project - Auto Runner
REM =====================================================

echo.
echo [1/5] Checking virtual environment...
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [2/5] Upgrading pip...
pip install --upgrade pip

echo.
echo [3/5] Installing dependencies...
pip install -r requirements.txt

echo.
echo [4/5] Running ETL pipeline...
python -m etl.clean_data

echo.
echo [5/5] Launching Streamlit dashboard...
streamlit run dashboard\app.py

pause
