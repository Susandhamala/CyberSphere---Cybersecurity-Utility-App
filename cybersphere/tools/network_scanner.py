import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import socket
import threading
import subprocess
import sys
import os

def run_scanner():
    scanner_window = tk.Toplevel()
    scanner_window.title("Network Scanner")
    scanner_window.geometry("800x600")
    scanner_window.configure(bg="#0f111a")
    
    NetworkScanner(scanner_window)

class NetworkScanner:
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = tk.Frame(self.parent, bg="#0f111a")
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(main_frame, text="Network Scanner", font=("Consolas", 16, "bold"),
                fg="#00fff7", bg="#0f111a").pack(pady=10)
        
        input_frame = tk.Frame(main_frame, bg="#0f111a")
        input_frame.pack(fill='x', pady=10)
        
        tk.Label(input_frame, text="Target IP/Range:", font=("Consolas", 12),
                fg="#00fff7", bg="#0f111a").pack(side='left')
        
        self.target_entry = tk.Entry(input_frame, width=30, bg="#1f2233", fg="#00fff7",
                                    font=("Consolas", 12), insertbackground="#00fff7")
        self.target_entry.pack(side='left', padx=10)
        self.target_entry.insert(0, "192.168.1.1")
        
        type_frame = tk.Frame(main_frame, bg="#0f111a")
        type_frame.pack(fill='x', pady=5)
        
        tk.Label(type_frame, text="Scan Type:", font=("Consolas", 12),
                fg="#00fff7", bg="#0f111a").pack(side='left')
        
        self.scan_type = tk.StringVar(value="ping")
        tk.Radiobutton(type_frame, text="Ping Scan", variable=self.scan_type, value="ping",
                      bg="#0f111a", fg="#00fff7", selectcolor="#1f2233", font=("Consolas", 10)).pack(side='left', padx=10)
        tk.Radiobutton(type_frame, text="Port Scan", variable=self.scan_type, value="port",
                      bg="#0f111a", fg="#00fff7", selectcolor="#1f2233", font=("Consolas", 10)).pack(side='left', padx=10)
        
        button_frame = tk.Frame(main_frame, bg="#0f111a")
        button_frame.pack(fill='x', pady=10)
        
        tk.Button(button_frame, text="Start Scan", command=self.start_scan,
                 bg="#141627", fg="#00fff7", font=("Consolas", 12)).pack(side='left', padx=5)
        tk.Button(button_frame, text="Stop Scan", command=self.stop_scan,
                 bg="#141627", fg="#00fff7", font=("Consolas", 12)).pack(side='left', padx=5)
        
        tk.Label(main_frame, text="Scan Results:", font=("Consolas", 12, "bold"),
                fg="#00fff7", bg="#0f111a").pack(anchor='w', pady=(20,5))
        
        self.results_text = scrolledtext.ScrolledText(main_frame, height=20, bg="#1f2233", 
                                                     fg="#00fff7", font=("Consolas", 10))
        self.results_text.pack(fill='both', expand=True)
        
        self.scanning = False
        
    def start_scan(self):
        target = self.target_entry.get().strip()
        if not target:
            messagebox.showerror("Error", "Please enter a target IP or range.", parent=self.parent)
            return
            
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"Starting {self.scan_type.get()} scan on {target}...\n\n")
        
        self.scanning = True
        scan_thread = threading.Thread(target=self.perform_scan, args=(target,))
        scan_thread.daemon = True
        scan_thread.start()
        
    def stop_scan(self):
        self.scanning = False
        self.results_text.insert(tk.END, "\nScan stopped by user.\n")
        
    def perform_scan(self, target):
        try:
            if self.scan_type.get() == "ping":
                self.ping_scan(target)
            else:
                self.port_scan(target)
        except Exception as e:
            self.results_text.insert(tk.END, f"\nError: {str(e)}\n")
            
    def ping_scan(self, target):
        self.results_text.insert(tk.END, f"Ping scanning {target}...\n")
        self.parent.update()
        
        try:
            if target == "192.168.1.1":
                base_ip = "192.168.1."
                for i in range(1, 10):
                    if not self.scanning:
                        break
                    ip = f"{base_ip}{i}"
                    try:
                        if sys.platform.startswith('win'):
                            response = subprocess.run(['ping', '-n', '1', '-w', '1000', ip], 
                                                    capture_output=True, timeout=2)
                        else:
                            response = subprocess.run(['ping', '-c', '1', '-W', '1', ip], 
                                                    capture_output=True, timeout=2)
                        
                        if response.returncode == 0:
                            self.results_text.insert(tk.END, f"Host up: {ip}\n")
                        else:
                            self.results_text.insert(tk.END, f"Host down: {ip}\n")
                            
                    except subprocess.TimeoutExpired:
                        self.results_text.insert(tk.END, f"Timeout: {ip}\n")
                    except Exception as e:
                        self.results_text.insert(tk.END, f"Error scanning {ip}: {str(e)}\n")
                        
                    self.parent.update()
                    
        except Exception as e:
            self.results_text.insert(tk.END, f"Ping scan error: {str(e)}\n")
            
    def port_scan(self, target):
        self.results_text.insert(tk.END, f"Port scanning {target}...\n")
        self.parent.update()
        
        common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995]
        
        for port in common_ports:
            if not self.scanning:
                break
                
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((target, port))
                sock.close()
                
                if result == 0:
                    service = self.get_service_name(port)
                    self.results_text.insert(tk.END, f"Open: {target}:{port} ({service})\n")
                else:
                    self.results_text.insert(tk.END, f"Closed: {target}:{port}\n")
                    
            except Exception as e:
                self.results_text.insert(tk.END, f"Error scanning port {port}: {str(e)}\n")
                
            self.parent.update()
            
    def get_service_name(self, port):
        services = {
            21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
            53: "DNS", 80: "HTTP", 110: "POP3", 143: "IMAP",
            443: "HTTPS", 993: "IMAPS", 995: "POP3S"
        }
        return services.get(port, "Unknown")