@echo off
echo Starting HablaConmigo Spanish Learning App...

REM Start Ollama in a separate window
echo Starting Ollama...
start "Ollama" ollama serve

REM Wait a moment for Ollama to initialize
timeout /t 3 /nobreak >nul

REM Activate virtual environment
call venv\Scripts\activate

REM Install/update requirements if needed
echo Checking dependencies...
pip install -r requirements.txt --quiet

REM Start the app
python app.py

pause
