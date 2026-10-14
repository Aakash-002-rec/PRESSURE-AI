@echo off
echo ===================================================
echo Starting PRESSURE-AI Platform (Backend & Frontend)
echo ===================================================

echo Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "PRESSURE-AI Backend" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 2 /nobreak >nul

echo Starting Vite Frontend on http://127.0.0.1:5173 ...
start "PRESSURE-AI Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo Both servers have been launched in separate windows!
echo Backend API Docs: http://127.0.0.1:8000/docs
echo Frontend Web App: http://127.0.0.1:5173
echo ===================================================
pause
