@echo off
setlocal

cd /d "%~dp0"
title Lightsky AI pro by Krivi

where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher was not found.
  echo Install Python 3.11+ from https://www.python.org/downloads/windows/
  echo Make sure the "py" launcher option is enabled.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Creating private Python environment for Lightsky AI...
  py -m venv .venv
  if errorlevel 1 (
    echo Failed to create the Python environment.
    pause
    exit /b 1
  )
)

call ".venv\Scripts\activate.bat"

if not exist ".venv\.lightsky_deps_installed" (
  echo Installing Lightsky AI dependencies. This can take a few minutes on first launch.
  python -m pip install --upgrade pip
  if errorlevel 1 (
    echo Failed to update pip.
    pause
    exit /b 1
  )
  python -m pip install -r requirements.txt
  if errorlevel 1 (
    echo Failed to install dependencies.
    pause
    exit /b 1
  )
  echo installed > ".venv\.lightsky_deps_installed"
)

start "" "http://127.0.0.1:8501/?startup=done"
python -m streamlit run streamlit_app.py --server.headless false --server.port 8501

pause
