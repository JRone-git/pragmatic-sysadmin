@echo off
echo ============================================================
echo   NEXUS-BREACH // Decentralized Rogue AI Command Center
echo   Starting servers...
echo ============================================================
echo.

echo [1/2] Starting backend server on port 8000...
start "NEXUS-BREACH Backend" cmd /k "cd /d %~dp0backend && python main.py"

echo [2/2] Starting frontend dev server on port 3000...
timeout /t 2 /nobreak >nul
start "NEXUS-BREACH Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ============================================================
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:3000
echo ============================================================
echo.
echo Opening browser in 5 seconds...
timeout /t 5 /nobreak >nul
start http://localhost:3000