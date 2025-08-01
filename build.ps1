# Build script for Modern EBook Reader
Write-Host "Building Modern EBook Reader..." -ForegroundColor Green

# Build the application
go build -ldflags="-s -w" -o ebookreader-modern.exe .

if ($LASTEXITCODE -eq 0) {
    Write-Host "Build completed successfully!" -ForegroundColor Green
    $fileSize = (Get-Item "ebookreader-modern.exe").Length / 1MB
    Write-Host "File size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Cyan
} else {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}
