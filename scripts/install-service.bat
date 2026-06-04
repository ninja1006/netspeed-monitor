@echo off
setlocal
cd /d "%~dp0.."
set "ROOT=%CD%"
set "SERVICE=SpeedMonPoller"
set "PYTHON=%ROOT%\venv\Scripts\python.exe"
set "NSSM=%ROOT%\scripts\nssm\nssm.exe"
if not exist "%NSSM%" (
  where nssm >nul 2>&1
  if errorlevel 1 (
    echo ERROR: nssm not found. Install with: winget install NSSM.NSSM
    echo Or place nssm.exe in scripts\nssm\
    exit /b 1
  )
  set "NSSM=nssm"
)

if not exist "%PYTHON%" (
  echo ERROR: venv not found at %PYTHON%
  echo Run: py -m venv venv ^& pip install -r backend\requirements.txt
  exit /b 1
)

sc query %SERVICE% >nul 2>&1
if not errorlevel 1 (
  echo Service %SERVICE% already exists. Run uninstall-service.bat first.
  exit /b 1
)

echo Installing %SERVICE% ...
"%NSSM%" install %SERVICE% "%PYTHON%" "-m" "backend.poller"
"%NSSM%" set %SERVICE% AppDirectory "%ROOT%"
"%NSSM%" set %SERVICE% AppStdout "%ROOT%\data\poller-service.log"
"%NSSM%" set %SERVICE% AppStderr "%ROOT%\data\poller-service.log"
"%NSSM%" set %SERVICE% AppRotateFiles 1
"%NSSM%" set %SERVICE% AppRotateBytes 1048576
"%NSSM%" set %SERVICE% Start SERVICE_AUTO_START
"%NSSM%" set %SERVICE% DisplayName "Network Speed Monitor Poller"
"%NSSM%" set %SERVICE% Description "VPN-aware speed poller (3-5 min interval; no SPEEDMON_DEV)"

net start %SERVICE%
if errorlevel 1 (
  echo Service failed to start. Check data\poller-service.log
  exit /b 1
)

echo.
echo OK: %SERVICE% is running.
echo Log: %ROOT%\data\poller-service.log
echo Verify: sc query %SERVICE%
endlocal
