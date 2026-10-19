@echo off
cd /d "%~dp0"
where py >nul 2>&1
if %errorlevel%==0 (
    py -3 main.py
) else (
    python main.py
)
if errorlevel 1 (
    echo.
    echo The game could not start. Install Python 3 with Tkinter,
    echo then try: py -3 main.py
    pause
)
