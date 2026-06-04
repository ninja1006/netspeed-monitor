@echo off
setlocal
cd /d "%~dp0.."
set "SERVICE=SpeedMonPoller"
set "NSSM=%CD%\scripts\nssm\nssm.exe"
if not exist "%NSSM%" (
  where nssm >nul 2>&1
  if errorlevel 1 (
    echo ERROR: nssm not found.
    exit /b 1
  )
  set "NSSM=nssm"
)

sc query %SERVICE% >nul 2>&1
if errorlevel 1 (
  echo Service %SERVICE% is not installed.
  exit /b 0
)

echo Stopping %SERVICE% ...
net stop %SERVICE% 2>nul
"%NSSM%" stop %SERVICE% confirm
"%NSSM%" remove %SERVICE% confirm

sc query %SERVICE% >nul 2>&1
if errorlevel 1 (
  echo OK: %SERVICE% removed.
) else (
  echo WARN: Service may still be registered. Check: sc query %SERVICE%
  exit /b 1
)
endlocal
