@echo off
echo Building Modern EBook Reader...

go mod tidy
go build -ldflags="-s -w" -o ebookreader-modern.exe .

if %ERRORLEVEL% EQU 0 (
    echo Build completed successfully!
    echo Executable: ebookreader-modern.exe
    echo.
    echo To run: .\ebookreader-modern.exe
    echo To test: go test ./modernui -v
) else (
    echo Build failed!
    exit /b 1
)
