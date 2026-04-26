@echo off
REM Nexus 2.0 End-to-End Test Runner
REM =================================

echo.
echo ******************************************
echo *     NEXUS 2.0 E2E TEST RUNNER          *
echo ******************************************
echo.

REM Check if server is running
echo Checking if server is running...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Server not running at http://localhost:8000
    echo Please start the server first:
    echo    uvicorn app.main:app --reload
    echo.
    pause
    exit /b 1
)

echo Server is running!
echo.

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found in PATH
    pause
    exit /b 1
)

REM Check if httpx is installed
echo Checking dependencies...
python -c "import httpx" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing httpx...
    pip install httpx
)

echo.
echo Starting E2E tests...
echo ===========================================
echo.

python test_e2e.py

if %errorlevel% == 0 (
    echo.
    echo 🎉 ALL TESTS PASSED!
) else (
    echo.
    echo ⚠️  SOME TESTS FAILED
)

echo.
pause
