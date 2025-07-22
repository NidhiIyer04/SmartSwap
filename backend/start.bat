@echo off
echo 🚀 Starting SmartSwapML Backend...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate

REM Install requirements
echo 📚 Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  No .env file found. Copying from .env.example...
    copy .env.example .env
    echo 📝 Please edit .env file with your configuration.
    echo    You can continue with default settings for demo purposes.
    pause
)

REM Start the application
echo 🌟 Starting FastAPI server...
echo 📊 API Documentation: http://localhost:8000/docs
echo 🔍 Health Check: http://localhost:8000/health
echo 🛑 Press Ctrl+C to stop the server
echo.

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
