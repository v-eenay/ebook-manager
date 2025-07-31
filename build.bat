@echo off
echo Building EBook Reader...
go mod tidy
go build -o ebookreader.exe
if %ERRORLEVEL% EQU 0 (
    echo Build successful! Executable created: ebookreader.exe
    echo.
    echo To run the application:
    echo   .\ebookreader.exe
    echo.
    echo To run with Go:
    echo   go run main.go
) else (
    echo Build failed!
)
