@echo off
REM FileOrganizer Windows Dependency Installer
echo ========================================
echo  File Organizer Pro - Dependency Setup
echo ========================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found in PATH.
    echo Please install Python 3.11+ from https://www.python.org/downloads/
    echo And ensure you check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo Python found.

REM Check if tkinter is available (should be included with Python on Windows)
python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo Warning: tkinter module not found.
    echo On Windows, tkinter is usually included with Python installation.
    echo If you installed Python without tkinter, you may need to reinstall Python
    echo and ensure "tcl/tk and IDLE" option is checked.
    echo.
)

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

if errorlevel 1 (
    echo Warning: Failed to upgrade pip. Continuing...
)

REM Install dependencies from requirements.txt
echo Installing dependencies from requirements.txt...
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo Error: Failed to install dependencies.
    pause
    exit /b 1
)

echo Successfully installed all dependencies.
echo.
echo You can now run the GUI with:
echo   python file_organizer_gui.py
echo.
echo Or build the executable with:
echo   python build_exe.py
echo.
pause