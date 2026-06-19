$ErrorActionPreference = "Stop"

Write-Host "Starting love_index on port 8090..."
Start-Process -FilePath "cmd.exe" -ArgumentList "/c startlove_index.bat > ..\love_index.log 2>&1" -WorkingDirectory "D:\github\i_love_love_ai_ultra_final\love_ai\love_index" -WindowStyle Minimized

Write-Host "Starting love_engine on port 6667..."
Start-Process -FilePath "cmd.exe" -ArgumentList "/c set PYTHONIOENCODING=utf-8 && .\venv\Scripts\love_engine.exe --config love_engine_config.yaml --port 6667 > love_engine.log 2>&1" -WorkingDirectory "D:\github\i_love_love_ai_ultra_final\love_ai" -WindowStyle Minimized

Write-Host "Starting love_crawler on port 6668..."
Start-Process -FilePath "cmd.exe" -ArgumentList "/c set PYTHONIOENCODING=utf-8 && .\venv\Scripts\uvicorn.exe love_crawler.deploy.docker.server:app --port 6668 > love_crawler.log 2>&1" -WorkingDirectory "D:\github\i_love_love_ai_ultra_final\love_ai" -WindowStyle Minimized

Write-Host "Waiting 5 seconds for love_engine to boot..."
Start-Sleep -Seconds 5

Write-Host "Starting love_smith on port 6665..."
Start-Process -FilePath "cmd.exe" -ArgumentList "/c set PYTHONIOENCODING=utf-8 && .\venv\Scripts\love_smith-proxy.exe --port 6665 --backend vllm --backend-url http://127.0.0.1:6667 --model all_high --budget-mode manual --budget-tokens 16384 > love_smith.log 2>&1" -WorkingDirectory "D:\github\i_love_love_ai_ultra_final\love_ai" -WindowStyle Minimized

Write-Host "Starting Auth Gateway on port 6666..."
Start-Process -FilePath "cmd.exe" -ArgumentList "/c set PYTHONIOENCODING=utf-8 && .\venv\Scripts\uvicorn.exe gateway:app --port 6666 > gateway.log 2>&1" -WorkingDirectory "D:\github\i_love_love_ai_ultra_final\love_ai" -WindowStyle Minimized

Write-Host "All services started! (Logs are in *.log)"
