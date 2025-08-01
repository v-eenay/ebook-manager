@echo off
REM Batch build script for Modern EBook Reader
REM This script builds the application with icon integration

echo Building Modern EBook Reader...

REM Ensure dependencies are up to date
echo Updating dependencies...
go mod tidy

REM Build the application with optimized flags and modern executable name
echo Building Go application with icon integration...
go build -ldflags="-s -w" -o ebookreader-modern.exe .

if %ERRORLEVEL% EQU 0 (
    echo Build completed successfully!
    echo Executable: ebookreader-modern.exe
    echo.
    echo Features included:
    echo   - Application icon integration
    echo   - Modern UI with zoom controls
    echo   - Keyboard shortcuts (F1 for help)
    echo   - Enhanced mouse interactions
    echo.
    echo To run the application:
    echo   .\ebookreader-modern.exe
    echo.
    echo To run with Go:
    echo   go run main.go
    echo.
    echo To run tests:
    echo   go test ./modernui -v
) else (
    echo Build failed!
    exit /b 1
)

echo Done!
