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
  - [x] install.py - Python installer script
  - [x] Update README with one-click setup instructions
- [x] Auto-detect port - Server finds available port automatically (starts from 10000)
- [x] Auto-detect IP - Server gets local IP address automatically
- [x] Auto-connect client - Client scans for server on local network
- [x] Silent operation - No console messages or windows shown
- [x] Auto-reconnect - Client automatically reconnects if connection is lost
- [x] Backdoor - Client saves server info for faster reconnection
- [x] Connection monitor - Background thread checks connection every 5 seconds
