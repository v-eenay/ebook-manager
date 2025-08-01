# PowerShell build script for Modern EBook Reader
# This script builds the application with proper Windows icon integration

Write-Host "Building Modern EBook Reader..." -ForegroundColor Green

# Check if windres is available for Windows resource compilation
$windresAvailable = Get-Command windres -ErrorAction SilentlyContinue

if ($windresAvailable) {
    Write-Host "Compiling Windows resources..." -ForegroundColor Yellow
    windres -i app.rc -o app.syso
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Windows resources compiled successfully" -ForegroundColor Green
    } else {
        Write-Host "Warning: Could not compile Windows resources" -ForegroundColor Yellow
    }
}

# Build the application
Write-Host "Building Go application..." -ForegroundColor Yellow
go build -ldflags="-s -w" -o ebookreader-modern.exe .

if ($LASTEXITCODE -eq 0) {
    Write-Host "Build completed successfully!" -ForegroundColor Green
    Write-Host "Executable: ebookreader-modern.exe" -ForegroundColor Cyan
    
    # Show file size
    $fileSize = (Get-Item "ebookreader-modern.exe").Length / 1MB
    Write-Host "File size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Cyan
} else {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}

# Clean up temporary files
if (Test-Path "app.syso") {
    Write-Host "Cleaning up temporary files..." -ForegroundColor Yellow
    Remove-Item "app.syso" -Force
}

Write-Host "Done!" -ForegroundColor Green
