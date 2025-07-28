# PowerShell script to start the development environment
Write-Host "Starting eBook Manager Development Environment..." -ForegroundColor Green
Write-Host ""

Write-Host "[1/2] Starting Vite development server..." -ForegroundColor Yellow
Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WorkingDirectory $PSScriptRoot

Write-Host "[2/2] Waiting for Vite server to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "Starting Electron application..." -ForegroundColor Yellow
$env:IS_DEV = "true"
npx electron .

Write-Host "Press any key to continue..." -ForegroundColor Cyan
[Console]::ReadKey() | Out-Null
