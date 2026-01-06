import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog
import os
import shutil
from PIL import Image, ImageTk
import subprocess
import platform
import socket
import json

class FileManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NeverScam Remote File Manager")
        self.root.geometry("1000x700")
        self.current_dir = "~"
        self.theme = "light"
        self.clipboard = None
        self.sock = None
        self.server_host = "localhost"  # Change to home IP
        self.server_port = 12345
        self.connect_to_server()
        self.create_menu()

    def connect_to_server(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.server_host, self.server_port))
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect to server: {e}")
            self.sock = None

    def send_command(self, command):
        if not self.sock:
            return None
        try:
            data = json.dumps(command).encode('utf-8')
            self.sock.sendall(data)
            response_data = self.sock.recv(4096)
            return json.loads(response_data.decode('utf-8'))
        except Exception as e:
            messagebox.showerror("Error", f"Communication error: {e}")
            return None
        self.create_ui()
        self.populate_tree()
        self.apply_theme()
        self.bind_shortcuts()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New File", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="New Folder", command=self.new_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Upload", command=self.upload_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Copy", command=self.copy_item, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste_item, accelerator="Ctrl+V")
        edit_menu.add_command(label="Delete", command=self.delete_item, accelerator="Del")
        edit_menu.add_command(label="Rename", command=self.rename_item)

        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Theme", command=self.toggle_theme)
        view_menu.add_command(label="Refresh", command=self.refresh)

    def create_ui(self):
        self.paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)

        # Left panel: treeview for directories
        self.tree_frame = tk.Frame(self.paned)
        self.paned.add(self.tree_frame)
        self.tree = ttk.Treeview(self.tree_frame)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.heading("#0", text="Directories")
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Right panel
        self.right_frame = tk.Frame(self.paned)
        self.paned.add(self.right_frame)

        # Search entry
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self.right_frame, textvariable=self.search_var)
        self.search_entry.pack(fill=tk.X)
        self.search_entry.bind("<KeyRelease>", self.on_search)

        # File list
        self.list_frame = tk.Frame(self.right_frame)
        self.list_frame.pack(fill=tk.BOTH, expand=True)
        self.file_list = tk.Listbox(self.list_frame)
        self.file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.file_scroll = tk.Scrollbar(self.list_frame)
        self.file_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_list.config(yscrollcommand=self.file_scroll.set)
        self.file_scroll.config(command=self.file_list.yview)
        self.file_list.bind("<Double-1>", self.on_list_double_click)
        self.file_list.bind("<Button-3>", self.on_right_click)

        # Bottom: editor and image
        self.bottom_frame = tk.Frame(self.right_frame)
        self.bottom_frame.pack(fill=tk.BOTH, expand=True)
        self.text_editor = scrolledtext.ScrolledText(self.bottom_frame, wrap=tk.WORD)
        self.text_editor.pack(fill=tk.BOTH, expand=True)
        self.image_label = tk.Label(self.bottom_frame)
        self.image_label.pack_forget()

    def populate_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.insert_tree("", self.current_dir)

    def insert_tree(self, parent, path):
        try:
            name = os.path.basename(path) or path
            node = self.tree.insert(parent, "end", text=name, values=(path,))
            response = self.send_command({"cmd": "LIST_DIRS", "path": path})
            if response and "items" in response:
                for item in sorted(response["items"]):
                    item_path = os.path.join(path, item)
                    self.insert_tree(node, item_path)
        except Exception as e:
            pass

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if selected:
            path = self.tree.item(selected[0], "values")[0]
            self.current_dir = path
            self.populate_list()

    def populate_list(self):
        self.file_list.delete(0, tk.END)
        response = self.send_command({"cmd": "LIST_DIR", "path": self.current_dir})
        if response and "items" in response:
            for item in sorted(response["items"]):
                self.file_list.insert(tk.END, item)
        elif response and "error" in response:
            messagebox.showerror("Error", response["error"])

    def on_list_double_click(self, event):
        selection = self.file_list.curselection()
        if selection:
            item = self.file_list.get(selection[0])
            path = os.path.join(self.current_dir, item)
            if os.path.isfile(path):
                self.open_file_path(path)
            elif os.path.isdir(path):
                self.current_dir = path
                self.populate_tree()
                self.populate_list()

    def open_file_path(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.text_editor.delete(1.0, tk.END)
            self.text_editor.insert(tk.END, content)
            self.image_label.pack_forget()
            self.text_editor.pack(fill=tk.BOTH, expand=True)
        except UnicodeDecodeError:
            try:
                img = Image.open(path)
                img.thumbnail((400, 400))
                self.photo = ImageTk.PhotoImage(img)
                self.image_label.config(image=self.photo)
                self.text_editor.pack_forget()
                self.image_label.pack(fill=tk.BOTH, expand=True)
            except Exception as e:
                messagebox.showerror("Error", f"Cannot open file: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open file: {e}")

    def open_file(self):
        path = filedialog.askopenfilename(initialdir=self.current_dir)
        if path:
            self.open_file_path(path)

    def save_file(self):
        path = filedialog.asksaveasfilename(initialdir=self.current_dir)
        if path:
            content = self.text_editor.get(1.0, tk.END)
            response = self.send_command({"cmd": "WRITE_FILE", "path": path, "content": content})
            if response and "status" in response:
                messagebox.showinfo("Success", "File saved successfully")
            elif response and "error" in response:
                messagebox.showerror("Error", response["error"])
            else:
                messagebox.showerror("Error", "Failed to save file")

    def new_file(self):
        name = simpledialog.askstring("New File", "Enter file name:")
        if name:
            path = os.path.join(self.current_dir, name)
            response = self.send_command({"cmd": "WRITE_FILE", "path": path, "content": ""})
            if response and "status" in response:
                self.populate_list()
            elif response and "error" in response:
                messagebox.showerror("Error", response["error"])
            else:
                messagebox.showerror("Error", "Failed to create file")

    def new_folder(self):
        name = simpledialog.askstring("New Folder", "Enter folder name:")
        if name:
            path = os.path.join(self.current_dir, name)
            response = self.send_command({"cmd": "MKDIR", "path": path})
            if response and "status" in response:
                self.populate_tree()
                self.populate_list()
            elif response and "error" in response:
                messagebox.showerror("Error", response["error"])
            else:
                messagebox.showerror("Error", "Failed to create folder")

    def delete_item(self):
        selection = self.file_list.curselection()
        if selection:
            item = self.file_list.get(selection[0])
            path = os.path.join(self.current_dir, item)
            if messagebox.askyesno("Delete", f"Delete {item}?"):
                response = self.send_command({"cmd": "DELETE", "path": path})
                if response and "status" in response:
                    self.populate_tree()
                    self.populate_list()
                elif response and "error" in response:
                    messagebox.showerror("Error", response["error"])
                else:
                    messagebox.showerror("Error", "Failed to delete")

    def rename_item(self):
        selection = self.file_list.curselection()
        if selection:
            old_name = self.file_list.get(selection[0])
            new_name = simpledialog.askstring("Rename", "Enter new name:", initialvalue=old_name)
            if new_name and new_name != old_name:
                old_path = os.path.join(self.current_dir, old_name)
                new_path = os.path.join(self.current_dir, new_name)
                response = self.send_command({"cmd": "RENAME", "path": old_path, "new_path": new_path})
                if response and "status" in response:
                    self.populate_tree()
                    self.populate_list()
                elif response and "error" in response:
                    messagebox.showerror("Error", response["error"])
                else:
                    messagebox.showerror("Error", "Failed to rename")

    def copy_item(self):
        selection = self.file_list.curselection()
        if selection:
            item = self.file_list.get(selection[0])
            self.clipboard = os.path.join(self.current_dir, item)

    def paste_item(self):
        if self.clipboard:
            base_name = os.path.basename(self.clipboard)
            dest = os.path.join(self.current_dir, base_name)
            response = self.send_command({"cmd": "COPY", "path": self.clipboard, "dest": dest})
            if response and "status" in response:
                self.populate_tree()
                self.populate_list()
            elif response and "error" in response:
                messagebox.showerror("Error", response["error"])
            else:
                messagebox.showerror("Error", "Failed to paste")

    def upload_file(self):
        local_path = filedialog.askopenfilename(title="Select file to upload")
        if local_path:
            try:
                with open(local_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                base_name = os.path.basename(local_path)
                remote_path = os.path.join(self.current_dir, base_name)
                response = self.send_command({"cmd": "WRITE_FILE", "path": remote_path, "content": content})
                if response and "status" in response:
                    self.populate_list()
                    messagebox.showinfo("Success", "Uploaded successfully")
                elif response and "error" in response:
                    messagebox.showerror("Error", response["error"])
                else:
                    messagebox.showerror("Error", "Upload failed")
            except UnicodeDecodeError:
                messagebox.showerror("Error", "Cannot upload binary files")
            except Exception as e:
                messagebox.showerror("Error", f"Upload failed: {e}")

    def on_search(self, event):
        query = self.search_var.get().lower()
        self.file_list.delete(0, tk.END)
        try:
            for item in sorted(os.listdir(self.current_dir)):
                if query in item.lower():
                    self.file_list.insert(tk.END, item)
        except PermissionError:
            pass

    def show_properties(self):
        selection = self.file_list.curselection()
        if selection:
            item = self.file_list.get(selection[0])
            path = os.path.join(self.current_dir, item)
            response = self.send_command({"cmd": "STAT", "path": path})
            if response and "size" in response:
                size = response["size"]
                mtime = response["mtime"]
                from datetime import datetime
                mod_time = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                info = f"Name: {item}\nSize: {size} bytes\nModified: {mod_time}"
                messagebox.showinfo("Properties", info)
            elif response and "error" in response:
                messagebox.showerror("Error", response["error"])
            else:
                messagebox.showerror("Error", "Failed to get properties")

    def open_with_default(self):
        messagebox.showinfo("Info", "Open with default app is not available for remote files")

    def on_right_click(self, event):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Open", command=lambda: self.on_list_double_click(event))
        menu.add_command(label="Open with Default App", command=self.open_with_default)
        menu.add_command(label="Properties", command=self.show_properties)
        menu.add_command(label="Delete", command=self.delete_item)
        menu.add_command(label="Rename", command=self.rename_item)
        menu.add_command(label="Copy", command=self.copy_item)
        menu.add_command(label="Paste", command=self.paste_item)
        menu.post(event.x_root, event.y_root)

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        self.apply_theme()

    def apply_theme(self):
        if self.theme == "light":
            self.root.config(bg="white")
            self.text_editor.config(bg="white", fg="black")
            self.file_list.config(bg="white", fg="black")
        else:
            self.root.config(bg="gray20")
            self.text_editor.config(bg="gray20", fg="white")
            self.file_list.config(bg="gray20", fg="white")

    def refresh(self):
        self.populate_tree()
        self.populate_list()

    def bind_shortcuts(self):
        self.root.bind("<Control-n>", lambda e: self.new_file())
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-c>", lambda e: self.copy_item())
        self.root.bind("<Control-v>", lambda e: self.paste_item())
        self.root.bind("<Delete>", lambda e: self.delete_item())
        self.root.focus_set()

if __name__ == "__main__":
    root = tk.Tk()
    app = FileManagerApp(root)
    root.mainloop()
