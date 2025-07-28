@echo off
echo Starting eBook Manager Development Environment...
echo.

echo [1/2] Starting Vite development server...
start "Vite Dev Server" cmd /k "cd /d %~dp0 && npm run dev"

echo [2/2] Waiting for Vite server to start...
timeout /t 3 /nobreak > nul

echo Starting Electron application...
npx electron .

pause
