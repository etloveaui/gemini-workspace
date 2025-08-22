@echo off
setlocal

REM Quick bootstrap for Windows venv
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
  echo [Error] Python not found. Install Python 3.x and add to PATH.
  exit /b 1
)

echo Creating venv...
python -m venv venv
if %ERRORLEVEL% NEQ 0 (
  echo [Error] Failed to create venv.
  exit /b 1
)

echo Upgrading pip...
call venv\Scripts\python.exe -m pip install -U pip
if %ERRORLEVEL% NEQ 0 (
  echo [Warn] pip upgrade may have failed. Continue anyway.
)

echo Done. Venv ready: venv\Scripts\python.exe
endlocal
