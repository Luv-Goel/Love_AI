@echo off
title Love AI Launcher
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8

echo =======================================
echo     Starting Love AI Components
echo =======================================

echo [1/3] Starting love_engine...
start "love_engine" cmd /k ".\venv\Scripts\love_engine.exe --config love_engine_config.yaml --port 6667"

echo [2/3] Starting love_smith Proxy...
start "love_smith Proxy" cmd /k ".\venv\Scripts\love_smith-proxy.exe --port 6665 --backend vllm --backend-url http://127.0.0.1:6667 --budget-mode manual --budget-tokens 16384"

echo [3/3] Starting Auth Gateway (Admin UI)...
start "Auth Gateway" cmd /k ".\venv\Scripts\uvicorn.exe gateway:app --port 6670"

echo.
echo Waiting 5 seconds for services to boot...
timeout /t 5 /nobreak > nul

echo Opening Admin Dashboard...
start http://127.0.0.1:6670/
