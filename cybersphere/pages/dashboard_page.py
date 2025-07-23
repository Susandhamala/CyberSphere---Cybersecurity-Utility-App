# -------------------------------------------------------------------------------
#                             CYBERSPHERE
#                     Property of Susan Dhamala
#                       All Rights Reserved
# -------------------------------------------------------------------------------
import tkinter as tk
from tkinter import messagebox
from tools.notes_manager import run_notes
from tools.network_scanner import run_scanner
from tools.password_vault import run_vault
from tools.exam_reminder import run_exam_reminder
from styles.styles import dashboard_style

class DashboardPage:
    def __init__(self, root, on_logout):
        self.root = root
        self.on_logout = on_logout

        self.frame = tk.Frame(root, bg=dashboard_style["bg_color"])
        self.frame.pack(fill="both", expand=True)

        tk.Label(self.frame, text="Welcome to CyberSphere", font=dashboard_style["title_font"],
                 bg=dashboard_style["bg_color"], fg=dashboard_style["title_fg"]).pack(pady=20)

        tools = [
            ("📝 Notes Manager", run_notes),
            ("🌐 Network Scanner", run_scanner),
            ("🔐 Password Vault", run_vault),
            ("📅 Exam Reminder", run_exam_reminder),
            ("🚪 Logout", self.logout)
        ]

        for text, cmd in tools:
            tk.Button(self.frame, text=text, font=dashboard_style["button_font"],
                      bg=dashboard_style["button_bg"], fg=dashboard_style["button_fg"],
                      width=30, pady=5, command=cmd).pack(pady=8)

    def logout(self):
        confirm = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if confirm:
            for widget in self.root.winfo_children():
                widget.destroy()
            self.on_logout(self.root)
