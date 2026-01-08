# TODO for Remote File Access Tool (Client-Server)

- [x] Create requirements.txt with dependencies (Pillow for image preview, PyInstaller for building .exe)
- [x] Create server.py: Lightweight socket server for home computer (low RAM, non-interfering)
- [x] Modify main.py: Client GUI that connects to server for remote file operations
- [x] Implement client-server communication using TCP sockets
- [x] Add basic error handling and connection management
- [x] Test server-client locally
- [x] Build client as .exe using PyInstaller (requires Windows environment)
- [x] Create one-click auto-install for host setup
  - [x] auto-install.bat - Batch script for quick installation
  - [x] silent-install.py - Python installer script (compilable to .exe)
  - [x] build-installer.bat - Build script for single-file .exe
- [x] Add PartyKit relay support for remote access without port forwarding
  - [x] partykit-relay.js - WebSocket relay server for PartyKit
  - [x] partykit.json - PartyKit configuration
  - [x] PARTYKIT_GUIDE.md - Detailed deployment instructions
  - [x] Update silent-install.py with PartyKit relay support
  - [x] Update README with PartyKit setup instructions

