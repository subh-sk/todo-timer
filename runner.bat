::[Bat To Exe Converter]
::
::YAwzoRdxOk+EWAjk
::fBw5plQjdCyDJGyX8VAjFAhBTgyDAES0A5EO4f7+086CsUYJW/IDeZzayfqHI+9z
::YAwzuBVtJxjWCl3EqQJgSA==
::ZR4luwNxJguZRRnk
::Yhs/ulQjdF+5
::cxAkpRVqdFKZSzk=
::cBs/ulQjdF+5
::ZR41oxFsdFKZSDk=
::eBoioBt6dFKZSDk=
::cRo6pxp7LAbNWATEpCI=
::egkzugNsPRvcWATEpCI=
::dAsiuh18IRvcCxnZtBJQ
::cRYluBh/LU+EWAnk
::YxY4rhs+aU+JeA==
::cxY6rQJ7JhzQF1fEqQJQ
::ZQ05rAF9IBncCkqN+0xwdVs0
::ZQ05rAF9IAHYFVzEqQJQ
::eg0/rx1wNQPfEVWB+kM9LVsJDGQ=
::fBEirQZwNQPfEVWB+kM9LVsJDGQ=
::cRolqwZ3JBvQF1fEqQJQ
::dhA7uBVwLU+EWDk=
::YQ03rBFzNR3SWATElA==
::dhAmsQZ3MwfNWATElA==
::ZQ0/vhVqMQ3MEVWAtB9wSA==
::Zg8zqx1/OA3MEVWAtB9wSA==
::dhA7pRFwIByZRRnk
::Zh4grVQjdCyDJGyX8VAjFAhBTgyDAES0A5EO4f7+086CsUYJW/IDbIDf1fqLOOVz
::YB416Ek+ZG8=
::
::
::978f952a14a936cc963da21a135fa983
@echo off
SETLOCAL

:: Set the path to the temporary folder
SET TEMP_DIR=%TEMP%\todo_timer
SET SCRIPT_PATH=%TEMP_DIR%\todo.py
SET PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe
SET PYTHON_INSTALLER=%TEMP%\python-3.11.0-amd64.exe

:: Create the temporary directory if it doesn't exist
IF NOT EXIST "%TEMP_DIR%" (
    mkdir "%TEMP_DIR%"
)

:: Check if Python 3.11 is installed
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Python 3.11 is not installed.
    echo Downloading Python 3.11 installer...
    
    :: Download Python installer
    powershell -Command "Invoke-WebRequest -Uri '%PYTHON_INSTALLER_URL%' -OutFile '%PYTHON_INSTALLER%'"
    
    echo Installing Python 3.11...
    
    :: Install Python silently
    "%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1
    
    :: Wait for a moment to ensure installation is complete
    timeout /t 5 /nobreak >nul
    
    :: Check again if Python is installed
    python --version >nul 2>&1
    IF ERRORLEVEL 1 (
        echo Python installation failed. Please install it manually from https://www.python.org/downloads/
        EXIT /B
    ) ELSE (
        echo Python 3.11 is successfully installed.
    )
) ELSE (
    echo Python 3.11 is already installed.
)

:: Check if pip is installed
python -m pip --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Pip is not installed. Installing Pip...
    python -m ensurepip --default-pip
)

:: Find the pip executable path
FOR /F "delims=" %%i IN ('where pip') DO SET PIP_PATH=%%i

:: Print the pip path found
IF DEFINED PIP_PATH (
    echo Pip found at: %PIP_PATH%
) ELSE (
    echo Pip path not found. Please check the installation.
    EXIT /B
)

:: Install necessary modules
echo Installing required modules...
"%PIP_PATH%" install tkcalendar

:: Check if todo.py exists
IF EXIST "%SCRIPT_PATH%" (
    echo todo.py already exists. Replacing the file...
    DEL /Q "%SCRIPT_PATH%"
)

:: Download the todo.py script from GitHub into the temp directory
echo Downloading todo.py from GitHub...
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/subh-sk/todo-timer/main/todo.py' -OutFile '%SCRIPT_PATH%'"

:: Run the todo.py script from the temporary folder
cd /d "%TEMP_DIR%"
python todo.py

:: Exit the batch file after todo.py finishes
exit
ENDLOCAL
