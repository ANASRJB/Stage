# FastAPI Server Startup Script
Write-Host "Starting FastAPI Server..." -ForegroundColor Green
Write-Host ""
Set-Location "C:\Users\MSI\Documents\chatbot\Stage\fast_api"
Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
Write-Host ""

Write-Host "Activating Python environment..." -ForegroundColor Blue
& "C:\Users\MSI\Documents\chatbot\venv\Scripts\Activate.ps1"
Write-Host ""

Write-Host "Starting uvicorn server on http://localhost:8000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
