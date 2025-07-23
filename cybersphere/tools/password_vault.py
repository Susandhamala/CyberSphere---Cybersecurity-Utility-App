# -------------------------------------------------------------------------------
#                             CYBERSPHERE
#                     Property of Susan Dhamala
#                       All Rights Reserved
# -------------------------------------------------------------------------------
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import base64
from cryptography.fernet import Fernet
import os
from utils.db import get_db

def run_vault():
    vault_window = tk.Toplevel()
    vault_window.title("Password Vault")
    vault_window.geometry("800x600")
    vault_window.configure(bg="#0f111a")
    
    PasswordVault(vault_window)

class PasswordVault:
    def __init__(self, parent):
        self.parent = parent
        self.username = "protocool"
        self.db = get_db()
        self.key = self.load_or_create_key()
        self.cipher = Fernet(self.key)
        self.setup_ui()
        self.load_passwords()
        
    def load_or_create_key(self):
        key_file = os.path.join("data", "vault_key.key")
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            os.makedirs("data", exist_ok=True)
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
            
    def setup_ui(self):
        main_frame = tk.Frame(self.parent, bg="#0f111a")
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(main_frame, text="Password Vault", font=("Consolas", 16, "bold"),
                fg="#00fff7", bg="#0f111a").pack(pady=10)
        
        button_frame = tk.Frame(main_frame, bg="#0f111a")
        button_frame.pack(fill='x', pady=10)
        
        tk.Button(button_frame, text="Add Password", command=self.add_password,
                 bg="#141627", fg="#00fff7", font=("Consolas", 12)).pack(side='left', padx=5)
        tk.Button(button_frame, text="Delete Password", command=self.delete_password,
                 bg="#141627", fg="#00fff7", font=("Consolas", 12)).pack(side='left', padx=5)
        tk.Button(button_frame, text="Copy Password", command=self.copy_password,
                 bg="#141627", fg="#00fff7", font=("Consolas", 12)).pack(side='left', padx=5)
        
        tk.Label(main_frame, text="Saved Passwords:", font=("Consolas", 12, "bold"),
                fg="#00fff7", bg="#0f111a").pack(anchor='w', pady=(20,5))
        
        columns = ('Service', 'Account', 'Password')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=15)
        
        self.tree.heading('Service', text='Service')
        self.tree.heading('Account', text='Account')
        self.tree.heading('Password', text='Password')
        
        self.tree.column('Service', width=150)
        self.tree.column('Account', width=200)
        self.tree.column('Password', width=200)
        
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        
    def load_passwords(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        c = self.db.cursor()
        c.execute("SELECT id, service, account, password FROM passwords WHERE username=?", 
                 (self.username,))
        passwords = c.fetchall()
        
        for pwd_id, service, account, encrypted_pwd in passwords:
            try:
                decrypted_pwd = self.cipher.decrypt(encrypted_pwd.encode()).decode()
                self.tree.insert('', tk.END, values=(service, account, decrypted_pwd), 
                               tags=(pwd_id,))
            except:
                self.tree.insert('', tk.END, values=(service, account, "[DECRYPTION ERROR]"), 
                               tags=(pwd_id,))
                               
    def add_password(self):
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add Password")
        dialog.geometry("400x250")
        dialog.configure(bg="#0f111a")
        dialog.grab_set()
        
        tk.Label(dialog, text="Service:", font=("Consolas", 12), 
                fg="#00fff7", bg="#0f111a").pack(pady=5)
        service_entry = tk.Entry(dialog, bg="#1f2233", fg="#00fff7", font=("Consolas", 12))
        service_entry.pack(pady=5, padx=20, fill='x')
        
        tk.Label(dialog, text="Account/Username:", font=("Consolas", 12), 
                fg="#00fff7", bg="#0f111a").pack(pady=5)
        account_entry = tk.Entry(dialog, bg="#1f2233", fg="#00fff7", font=("Consolas", 12))
        account_entry.pack(pady=5, padx=20, fill='x')
        
        tk.Label(dialog, text="Password:", font=("Consolas", 12), 
                fg="#00fff7", bg="#0f111a").pack(pady=5)
        password_entry = tk.Entry(dialog, bg="#1f2233", fg="#00fff7", font=("Consolas", 12), show="*")
        password_entry.pack(pady=5, padx=20, fill='x')
        
        button_frame = tk.Frame(dialog, bg="#0f111a")
        button_frame.pack(pady=20)
        
        def save():
            service = service_entry.get().strip()
            account = account_entry.get().strip()
            password = password_entry.get()
            
            if not service or not account or not password:
                messagebox.showerror("Error", "All fields are required.", parent=dialog)
                return
                
            encrypted_pwd = self.cipher.encrypt(password.encode()).decode()
            
            c = self.db.cursor()
            c.execute("INSERT INTO passwords (username, service, account, password) VALUES (?, ?, ?, ?)",
                     (self.username, service, account, encrypted_pwd))
            self.db.commit()
            
            dialog.destroy()
            self.load_passwords()
            messagebox.showinfo("Success", "Password saved successfully.", parent=self.parent)
            
        tk.Button(button_frame, text="Save", command=save,
                 bg="#141627", fg="#00fff7", font=("Consolas", 12)).pack(side='left', padx=5)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy,
                 bg="#141627", fg="#00fff7", font=("Consolas", 12)).pack(side='left', padx=5)
        
    def delete_password(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a password to delete.", parent=self.parent)
            return
            
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this password?", 
                                  parent=self.parent):
            return
            
        item = self.tree.item(selected[0])
        pwd_id = self.tree.item(selected[0])['tags'][0]
        
        c = self.db.cursor()
        c.execute("DELETE FROM passwords WHERE id=?", (pwd_id,))
        self.db.commit()
        
        self.load_passwords()
        messagebox.showinfo("Success", "Password deleted.", parent=self.parent)
        
    def copy_password(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a password to copy.", parent=self.parent)
            return
            
        item = self.tree.item(selected[0])
        password = item['values'][2]
        
        if password == "[DECRYPTION ERROR]":
            messagebox.showerror("Error", "Cannot copy this password.", parent=self.parent)
            return
            
        self.parent.clipboard_clear()
        self.parent.clipboard_append(password)
        self.parent.update()
        messagebox.showinfo("Copied", "Password copied to clipboard.", parent=self.parent)
