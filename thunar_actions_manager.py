#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import zipfile
import shutil
import threading
import subprocess

class ThunarActionsManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Thunar Custom Actions Manager")
        self.root.geometry("500x300")
        
        # Configuration paths
        self.thunar_config = os.path.expanduser("~/.config/Thunar")
        self.uca_xml = os.path.join(self.thunar_config, "uca.xml")
        self.uca_d = os.path.join(self.thunar_config, "uca.d")
        
        # GUI Elements
        self.create_widgets()
        self.update_status("Ready")

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        btn_style = ttk.Style()
        btn_style.configure('TButton', padding=5)
        
        self.btn_backup = ttk.Button(main_frame, text="Backup Actions", command=self.start_backup)
        self.btn_backup.pack(pady=5, fill=tk.X)
        
        self.btn_restore = ttk.Button(main_frame, text="Restore Actions", command=self.start_restore)
        self.btn_restore.pack(pady=5, fill=tk.X)
        
        self.btn_import = ttk.Button(main_frame, text="Import Actions", command=self.start_import)
        self.btn_import.pack(pady=5, fill=tk.X)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def update_status(self, message):
        self.status_var.set(message)
        self.root.update_idletasks()

    def validate_config_exists(self):
        if not os.path.exists(self.uca_xml) and not os.path.exists(self.uca_d):
            messagebox.showerror("Error", "No Thunar custom actions found!")
            return False
        return True

    def start_backup(self):
        if not self.validate_config_exists():
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".zip",
            filetypes=[("ZIP files", "*.zip")],
            title="Save Backup As"
        )
        if path:
            threading.Thread(target=self.backup_actions, args=(path,), daemon=True).start()

    def start_restore(self):
        path = filedialog.askopenfilename(
            filetypes=[("ZIP files", "*.zip")],
            title="Select Backup File"
        )
        if path:
            threading.Thread(target=self.restore_actions, args=(path,), daemon=True).start()

    def start_import(self):
        path = filedialog.askopenfilename(
            filetypes=[("ZIP files", "*.zip")],
            title="Select Import File"
        )
        if path:
            threading.Thread(target=self.import_actions, args=(path,), daemon=True).start()

    def backup_actions(self, backup_path):
        try:
            self.update_status("Backing up custom actions...")
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Backup uca.xml
                if os.path.exists(self.uca_xml):
                    zipf.write(self.uca_xml, arcname="uca.xml")
                
                # Backup uca.d directory
                if os.path.exists(self.uca_d):
                    for root, _, files in os.walk(self.uca_d):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, self.thunar_config)
                            zipf.write(file_path, arcname=arcname)
            
            self.update_status(f"Backup complete: {backup_path}")
            messagebox.showinfo("Success", "Backup created successfully!")
            
        except Exception as e:
            self.update_status("Backup failed")
            messagebox.showerror("Error", f"Backup failed:\n{str(e)}")

    def restore_actions(self, restore_path):
        try:
            self.update_status("Restoring custom actions...")
            
            # Clear existing configuration
            if os.path.exists(self.uca_xml):
                os.remove(self.uca_xml)
            if os.path.exists(self.uca_d):
                shutil.rmtree(self.uca_d)
            
            # Extract backup
            with zipfile.ZipFile(restore_path, 'r') as zipf:
                zipf.extractall(self.thunar_config)
            
            self.update_status("Restore complete. Restarting Thunar...")
            self.restart_thunar()
            messagebox.showinfo("Success", "Custom actions restored and Thunar restarted!")
            
        except Exception as e:
            self.update_status("Restore failed")
            messagebox.showerror("Error", f"Restore failed:\n{str(e)}")

    def import_actions(self, import_path):
        try:
            self.update_status("Importing custom actions...")
            
            # Extract to temporary directory
            temp_dir = os.path.join(self.thunar_config, "temp_import")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            with zipfile.ZipFile(import_path, 'r') as zipf:
                zipf.extractall(temp_dir)
            
            # Merge XML files
            imported_xml = os.path.join(temp_dir, "uca.xml")
            if os.path.exists(imported_xml):
                if os.path.exists(self.uca_xml):
                    # Simple append (not XML-merge, but practical for most users)
                    with open(self.uca_xml, 'a') as f:
                        with open(imported_xml, 'r') as import_f:
                            f.write("\n" + import_f.read())
                else:
                    shutil.move(imported_xml, self.uca_xml)
            
            # Merge uca.d directory
            imported_uca_d = os.path.join(temp_dir, "uca.d")
            if os.path.exists(imported_uca_d):
                if not os.path.exists(self.uca_d):
                    os.makedirs(self.uca_d)
                for item in os.listdir(imported_uca_d):
                    src = os.path.join(imported_uca_d, item)
                    dst = os.path.join(self.uca_d, item)
                    if os.path.exists(dst):
                        os.remove(dst)
                    shutil.move(src, dst)
            
            shutil.rmtree(temp_dir)
            self.update_status("Import complete. Restarting Thunar...")
            self.restart_thunar()
            messagebox.showinfo("Success", "Actions imported and Thunar restarted!")
            
        except Exception as e:
            self.update_status("Import failed")
            messagebox.showerror("Error", f"Import failed:\n{str(e)}")

    def restart_thunar(self):
        # Restart Thunar to reload custom actions
        try:
            # Quit Thunar
            subprocess.run(['thunar', '-q'], check=True)
            # Start Thunar as daemon in background
            subprocess.Popen(['thunar', '--daemon'])
            self.update_status("Thunar restarted.")
        except Exception as e:
            self.update_status("Failed to restart Thunar.")
            messagebox.showwarning("Warning", f"Could not restart Thunar automatically.\nYou may need to restart it manually.\n\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ThunarActionsManager(root)
    root.mainloop()
