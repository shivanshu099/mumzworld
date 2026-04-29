@echo off
echo ==============================================
echo        Starting Mumzworld Application
echo ==============================================

:: Check if the virtual environment exists, if not create it
if not exist venv\Scripts\activate.bat (
    echo [INFO] Virtual environment not found. Creating one...
    python -m venv venv
    echo [INFO] Virtual environment created successfully.
)

:: Activate the virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

:: Install dependencies
echo [INFO] Installing required packages...
pip install -r requirements.txt

:: Run the Streamlit application
echo [INFO] Launching Streamlit app...
streamlit run app.py

pause
