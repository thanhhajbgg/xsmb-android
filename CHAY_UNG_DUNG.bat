@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_windows.ps1"
if errorlevel 1 (
    echo.
    echo Khong khoi dong duoc. Doc huong dan ngay phia tren.
    pause
    exit /b 1
)
exit /b 0
