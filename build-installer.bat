@echo off
REM Build silent installer exe
pip install pyinstaller --quiet --disable-pip-version-check >nul 2>&1

pyinstaller --onefile --windowed --name NeverScamInstaller silent-install.py --clean --noconfirm >nul 2>&1

if exist build rmdir /s /q build >nul 2>&1
if exist silent-install.spec del silent-install.spec >nul 2>&1

echo Build complete. NeverScamInstaller.exe created in dist folder.
pause

