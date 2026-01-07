@echo off
REM NeverScam Client Build Script
REM Auto-installs dependencies silently and builds the .exe

REM Install dependencies silently
pip install -r requirements.txt --quiet --disable-pip-version-check >nul 2>&1

REM Build the .exe silently
pyinstaller --onefile --windowed --name NeverScamClient main.py --clean --noconfirm >nul 2>&1

REM Clean up build files
if exist build rmdir /s /q build >nul 2>&1
if exist NeverScamClient.spec del NeverScamClient.spec >nul 2>&1

echo Build complete. NeverScamClient.exe created.
pause
