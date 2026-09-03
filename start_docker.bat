@echo off
cd /d "%~dp0"
docker compose up --build -d
if errorlevel 1 (
  echo.
  echo Docker could not start the dashboard. Make sure Docker Desktop is running.
  pause
  exit /b 1
)
start "" http://localhost:8768
echo MCIT PMO Dashboard is running at http://localhost:8768
pause
