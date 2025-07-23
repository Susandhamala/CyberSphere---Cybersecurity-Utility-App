import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, date
import calendar
from utils.db import get_db

def run_exam_reminder():
    reminder_window = tk.Toplevel()
    reminder_window.title("Exam Reminder")
    reminder_window.geometry("1000x650")
    reminder_window.configure(bg="#0f111a")
    
    ExamReminder(reminder_window)

class ExamReminder:
    def __init__(self, parent):
        self.parent = parent
        self.username = "protocool"
        self.db = get_db()
        self.setup_ui()
        self.load_exams()
        
    def setup_ui(self):
        main_frame = tk.Frame(self.parent, bg="#0f111a")
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(main_frame, text="Exam Reminder", font=("Consolas", 16, "bold"),
                fg="#00fff7", bg="#0f111a").pack(pady=10)
        
        button_frame = tk.Frame(main_frame, bg="#0f111a")
        button_frame.pack(fill='x', pady=10)
        
        tk.Button(button_frame, text="Add Exam", command=self.add_exam,
                 bg="#141627", fg="#00fff7", font=("Consolas", 12)).pack(side='left', padx=5)
        tk.Button(button_frame, text="Delete Exam", command=self.delete_exam,
                 bg="#141627", fg="#00fff7", font=("Consolas", 12)).pack(side='left', padx=5)
        tk.Button(button_frame, text="Refresh", command=self.load_exams,
                 bg="#141627", fg="#00fff7", font=("Consolas", 12)).pack(side='left', padx=5)
        
        tk.Label(main_frame, text="Upcoming Exams:", font=("Consolas", 12, "bold"),
                fg="#00fff7", bg="#0f111a").pack(anchor='w', pady=(20,5))
        
        # Create Treeview with countdown column
        columns = ('Subject', 'Date', 'Time', 'Location', 'Countdown', 'Notes')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        self.tree.heading('Subject', text='Subject')
        self.tree.heading('Date', text='Date')
        self.tree.heading('Time', text='Time')
        self.tree.heading('Location', text='Location')
        self.tree.heading('Countdown', text='Countdown')
        self.tree.heading('Notes', text='Notes')
        
        # Define column widths
        self.tree.column('Subject', width=150)
        self.tree.column('Date', width=100)
        self.tree.column('Time', width=80)
        self.tree.column('Location', width=120)
        self.tree.column('Countdown', width=120)
        self.tree.column('Notes', width=200)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        
        # Configure tags for coloring
        self.tree.tag_configure('urgent', background='#ff4444')    # Red for <= 5 days
        self.tree.tag_configure('warning', background='#4444ff')   # Blue for <= 7 days
        self.tree.tag_configure('normal', background='#44ff44')    # Green for <= 12 days
        self.tree.tag_configure('future', background='#1f2233')    # Default for > 12 days
        
    def calculate_countdown(self, exam_date_str):
        """Calculate days remaining and return formatted string with color tag"""
        try:
            exam_date = datetime.strptime(exam_date_str, "%Y-%m-%d").date()
            today = date.today()
            days_remaining = (exam_date - today).days
            
            if days_remaining < 0:
                return f"Passed ({abs(days_remaining)} days ago)", 'urgent'
            elif days_remaining == 0:
                return "Today!", 'urgent'
            elif days_remaining <= 5:
                return f"{days_remaining} days", 'urgent'
            elif days_remaining <= 7:
                return f"{days_remaining} days", 'warning'
            elif days_remaining <= 12:
                return f"{days_remaining} days", 'normal'
            else:
                return f"{days_remaining} days", 'future'
        except:
            return "Invalid Date", 'future'
            
    def load_exams(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        c = self.db.cursor()
        c.execute("SELECT id, subject, date, time, location, notes FROM exams WHERE username=? ORDER BY date", 
                 (self.username,))
        exams = c.fetchall()
        
        for exam_id, subject, date_str, time, location, notes in exams:
            # Calculate countdown and get color tag
            countdown_text, tag = self.calculate_countdown(date_str)
            
            self.tree.insert('', tk.END, 
                           values=(subject, date_str, time or '', location or '', countdown_text, notes or ''), 
                           tags=(tag, exam_id))
                           
    def add_exam(self):
        # Create dialog window
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add Exam")
        dialog.geometry("400x400")
        dialog.configure(bg="#0f111a")
        dialog.grab_set()  # Modal dialog
        
        # Subject
        tk.Label(dialog, text="Subject:", font=("Consolas", 12), 
                fg="#00fff7", bg="#0f111a").pack(pady=5)
        subject_entry = tk.Entry(dialog, bg="#1f2233", fg="#00fff7", font=("Consolas", 12))
        subject_entry.pack(pady=5, padx=20, fill='x')
        
        # Date
        tk.Label(dialog, text="Date (YYYY-MM-DD):", font=("Consolas", 12), 
                fg="#00fff7", bg="#0f111a").pack(pady=5)
        date_entry = tk.Entry(dialog, bg="#1f2233", fg="#00fff7", font=("Consolas", 12))
        date_entry.pack(pady=5, padx=20, fill='x')
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Time
        tk.Label(dialog, text="Time (HH:MM):", font=("Consolas", 12), 
                fg="#00fff7", bg="#0f111a").pack(pady=5)
        time_entry = tk.Entry(dialog, bg="#1f2233", fg="#00fff7", font=("Consolas", 12))
        time_entry.pack(pady=5, padx=20, fill='x')
        
        # Location
        tk.Label(dialog, text="Location:", font=("Consolas", 12), 
                fg="#00fff7", bg="#0f111a").pack(pady=5)
        location_entry = tk.Entry(dialog, bg="#1f2233", fg="#00fff7", font=("Consolas", 12))
        location_entry.pack(pady=5, padx=20, fill='x')
        
        # Notes
        tk.Label(dialog, text="Notes:", font=("Consolas", 12), 
                fg="#00fff7", bg="#0f111a").pack(pady=5)
        notes_entry = tk.Text(dialog, height=4, bg="#1f2233", fg="#00fff7", 
                             font=("Consolas", 11), wrap='word')
        notes_entry.pack(pady=5, padx=20, fill='x')
        
        # Buttons
        button_frame = tk.Frame(dialog, bg="#0f111a")
        button_frame.pack(pady=20)
        
        def save():
            subject = subject_entry.get().strip()
            date_str = date_entry.get().strip()
            time = time_entry.get().strip()
            location = location_entry.get().strip()
            notes = notes_entry.get(1.0, 'end-1c').strip()
            
            if not subject or not date_str:
                messagebox.showerror("Error", "Subject and Date are required.", parent=dialog)
                return
                
            # Validate date format
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.", parent=dialog)
                return
                
            # Validate time format if provided
            if time:
                try:
                    datetime.strptime(time, "%H:%M")
                except ValueError:
                    messagebox.showerror("Error", "Invalid time format. Use HH:MM.", parent=dialog)
                    return
            
            # Save to database
            c = self.db.cursor()
            c.execute("INSERT INTO exams (username, subject, date, time, location, notes) VALUES (?, ?, ?, ?, ?, ?)",
                     (self.username, subject, date_str, time or None, location or None, notes or None))
            self.db.commit()
            
            dialog.destroy()
            self.load_exams()
            messagebox.showinfo("Success", "Exam added successfully.", parent=self.parent)
            
        tk.Button(button_frame, text="Save", command=save,
                 bg="#141627", fg="#00fff7", font=("Consolas", 12)).pack(side='left', padx=5)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy,
                 bg="#141627", fg="#00fff7", font=("Consolas", 12)).pack(side='left', padx=5)
        
    def delete_exam(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an exam to delete.", parent=self.parent)
            return
            
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this exam?", 
                                  parent=self.parent):
            return
            
        item = self.tree.item(selected[0])
        exam_id = self.tree.item(selected[0])['tags'][1]  # tags[0] is color, tags[1] is id
        
        c = self.db.cursor()
        c.execute("DELETE FROM exams WHERE id=?", (exam_id,))
        self.db.commit()
        
        self.load_exams()
        messagebox.showinfo("Success", "Exam deleted.", parent=self.parent)