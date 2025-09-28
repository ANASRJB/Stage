@echo off
echo Starting FastAPI Server...
echo.
cd /d "C:\Users\MSI\Documents\chatbot\Stage\fast_api"
echo Current directory: %CD%
echo.
echo Activating Python environment...
call "C:\Users\MSI\Documents\chatbot\venv\Scripts\activate.bat"
echo.
echo Starting uvicorn server on http://localhost:8000
echo.
python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
pause
