@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>&1
if not errorlevel 1 (
    py -3 -m venv .venv
) else (
    where python >nul 2>&1
    if errorlevel 1 (
        echo Python is needed once on this Windows computer to build the EXE.
        echo Install Python 3 from python.org, select Add python.exe to PATH, then retry.
        pause
        exit /b 1
    )
    python -m venv .venv
)
if errorlevel 1 goto failed

echo Installing the EXE builder...
".venv\Scripts\python.exe" -m pip install --upgrade "pyinstaller>=6,<7"
if errorlevel 1 goto failed

echo Running game tests...
".venv\Scripts\python.exe" -m unittest discover -s tests -v
if errorlevel 1 goto failed

echo Building SpaceFractions.exe...
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --onefile --windowed --name SpaceFractions main.py
if errorlevel 1 goto failed

if not exist "dist\SpaceFractions.exe" goto failed
echo.
echo SUCCESS: %CD%\dist\SpaceFractions.exe
echo Copy only this EXE to another Windows PC and double-click it to play.
explorer "dist"
pause
exit /b 0

:failed
echo.
echo The build failed. Read the error above and try again.
pause
exit /b 1
