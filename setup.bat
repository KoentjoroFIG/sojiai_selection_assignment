@echo off
REM ============================================================
REM Setup Script for AD Extractor & Evaluator Project (Windows)
REM ============================================================

echo.
echo ========================================
echo AD Extractor Setup Script (Windows)
echo ========================================
echo.

REM Check if Python is installed
set PYTHON_CMD=
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
) else (
    py --version >nul 2>&1
    if not errorlevel 1 (
        set PYTHON_CMD=py
    ) else (
        echo [ERROR] Python is not installed or not in PATH
        echo Please install Python 3.12+ from https://www.python.org/downloads/
        echo.
        echo Make sure to:
        echo 1. Install Python from python.org
        echo 2. Check 'Add Python to PATH' during installation
        echo 3. Disable the Windows Store Python stub in Settings ^> Apps ^> Advanced app settings ^> App execution aliases
        pause
        exit /b 1
    )
)

echo [1/5] Python detected:
%PYTHON_CMD% --version
echo.

REM Create virtual environment
echo [2/5] Creating virtual environment...
if exist .venv (
    REM Check if venv is valid by looking for activation script
    if exist .venv\Scripts\activate.bat (
        echo Virtual environment already exists. Skipping creation.
    ) else (
        echo [WARNING] Existing .venv folder is invalid. Removing and recreating...
        rmdir /s /q .venv
        %PYTHON_CMD% -m venv .venv
        if errorlevel 1 (
            echo [ERROR] Failed to create virtual environment
            pause
            exit /b 1
        )
        echo Virtual environment created successfully.
    )
) else (
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
)
echo.

REM Activate virtual environment and install dependencies
echo [3/5] Activating virtual environment and installing dependencies...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

cd ad_extractor
pip install --upgrade pip
if errorlevel 1 (
    echo [WARNING] pip upgrade had issues, continuing...
)
pip install -r requirement.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    cd ..
    pause
    exit /b 1
)
cd ..
echo Dependencies installed successfully.
echo.

REM Check for .env file
echo [4/5] Checking environment configuration...
if exist ad_extractor\.env (
    echo .env file found.
) else (
    echo [WARNING] .env file not found. Creating template...
    (
        echo LLM_API_KEY=your_openai_api_key_here
        echo BASE_URL=https://api.openai.com/v1
    ) > ad_extractor\.env
    echo.
    echo [ACTION REQUIRED] Please edit ad_extractor\.env and add your OpenAI API key
    echo   Example: LLM_API_KEY=sk-proj-...
)
echo.

REM Create output directory if it doesn't exist
if not exist output (
    mkdir output
    echo Created output directory.
)

echo [5/5] Setup complete!
echo.
echo ========================================
echo Next Steps:
echo ========================================
echo 1. Edit ad_extractor\.env and add your OpenAI API key (if not done already)
echo 2. Activate the virtual environment:
echo    .venv\Scripts\activate
echo 3. Start the application:
echo    cd ad_extractor
echo    python main.py
echo.
echo The API will be available at: http://localhost:8000
echo Interactive docs at: http://localhost:8000/docs
echo ========================================
echo.

pause
