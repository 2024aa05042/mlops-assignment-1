@echo off
REM Quick test runner script for Windows

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║   MLOps Testing ^& Code Quality Check Script (Windows)      ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Check Python
echo 🐍 Checking Python installation...
python --version
echo.

REM Create venv if needed
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate venv
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Install dependencies
echo 📦 Installing dependencies...
pip install -q -r requirements-dev.txt
echo.

echo ╔════════════════════════════════════════════════════════════╗
echo ║                    Running Linting Checks                 ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Flake8
echo 🎯 Running Flake8...
flake8 src\ deployment\app\ --count --statistics
if %ERRORLEVEL% EQU 0 (
    echo ✅ Flake8 passed
) else (
    echo ⚠️  Flake8 issues found (non-blocking)
)
echo.

REM Black
echo 🎨 Checking Black code format...
black --check src\ deployment\app\ >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Black format check passed
) else (
    echo ⚠️  Code format issues found
    echo    Run: black src\ deployment\app\ (to auto-fix)
)
echo.

REM Pylint
echo 🔍 Running Pylint...
pylint src\train_pipeline.py deployment\app\main.py --disable=all --enable=E,F >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Pylint passed
) else (
    echo ⚠️  Pylint issues found (non-blocking)
)
echo.

echo ╔════════════════════════════════════════════════════════════╗
echo ║                    Running Unit Tests                     ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Pytest with coverage
echo 🧪 Running pytest with coverage...
pytest tests\ -v --tb=short --cov=src --cov=deployment\app --cov-report=html --cov-report=term-missing -m "not slow"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ╔════════════════════════════════════════════════════════════╗
    echo ║                    Test Summary                           ║
    echo ╚════════════════════════════════════════════════════════════╝
    echo.
    echo ✅ All checks passed!
    echo.
    echo 📊 Coverage report generated in: htmlcov\index.html
    echo 📝 Open with: start htmlcov\index.html
    echo.
    exit /b 0
) else (
    echo.
    echo ╔════════════════════════════════════════════════════════════╗
    echo ║                    Test Summary                           ║
    echo ╚════════════════════════════════════════════════════════════╝
    echo.
    echo ❌ Some tests failed - review output above
    echo.
    exit /b 1
)
