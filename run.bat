@echo off
echo.
echo  ███████╗███████╗███╗   ██╗████████╗██╗███╗   ██╗███████╗██╗     ███╗   ███╗██╗███╗   ██╗██████╗
echo  ██╔════╝██╔════╝████╗  ██║╚══██╔══╝██║████╗  ██║██╔════╝██║     ████╗ ████║██║████╗  ██║██╔══██╗
echo  ███████╗█████╗  ██╔██╗ ██║   ██║   ██║██╔██╗ ██║█████╗  ██║     ██╔████╔██║██║██╔██╗ ██║██║  ██║
echo  ╚════██║██╔══╝  ██║╚██╗██║   ██║   ██║██║╚██╗██║██╔══╝  ██║     ██║╚██╔╝██║██║██║╚██╗██║██║  ██║
echo  ███████║███████╗██║ ╚████║   ██║   ██║██║ ╚████║███████╗███████╗██║ ╚═╝ ██║██║██║ ╚████║██████╔╝
echo  ╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═════╝
echo.
echo  AI-native cybersecurity platform
echo  Shield ID · Shield Phish · Shield Dev · Shield SOC
echo  ──────────────────────────────────────────────────
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python 3.10+ from python.org
    pause
    exit /b 1
)

REM Create .env if missing
if not exist .env (
    echo [SETUP] Creating .env from template...
    copy .env.example .env >nul
    echo [WARN]  Add your ANTHROPIC_API_KEY to .env before using AI features
    echo.
)

REM Create and activate venv
if not exist venv (
    echo [SETUP] Creating virtual environment...
    python -m venv venv
)

echo [SETUP] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo [SETUP] Installing dependencies...
pip install -r requirements.txt -q

echo.
echo [START] Launching SentinelMind API...
echo [INFO]  API docs: http://localhost:8000/docs
echo [INFO]  Health:   http://localhost:8000/health
echo.

python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
