@echo off
cd /d "%~dp0.."
set SPEEDMON_DEV=1
call venv\Scripts\activate.bat
python -m backend.poller
