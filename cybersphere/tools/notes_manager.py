# -------------------------------------------------------------------------------
#                             CYBERSPHERE
#                     Property of Susan Dhamala
#                       All Rights Reserved
# -------------------------------------------------------------------------------
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import os
import shutil
from utils.db import get_db

def run_notes():
    notes_window = tk.Toplevel()
    notes_window.title("Notes Manager")
    notes_window.geometry("1000x700")
    notes_window.configure(bg="#0f111a")
    
    NotesManager(notes_window)

class NotesManager:
    def __init__(self, parent):
        self.parent = parent
        self.username = "protocool"
        self.db = get_db()
        self.setup_ui()
        self.load_subjects()

    def setup_ui(self):
        self.frame = tk.Frame(self.parent, bg="#0f111a")
        self.frame.pack(fill='both', expand=True, padx=10, pady=10)

        topbar = tk.Frame(self.frame, bg="#0f111a")
        topbar.pack(fill="x", pady=5)
        
        tk.Label(topbar, text="Subjects:", font=("Consolas", 12, "bold"), 
                fg="#00fff7", bg="#0f111a").pack(side="left", padx=5)

        self.subject_var = tk.StringVar()
        self.subject_combo = ttk.Combobox(topbar, textvariable=self.subject_var, 
                                         state='readonly', width=20)
        self.subject_combo.pack(side="left", padx=5)
        self.subject_combo.bind("<<ComboboxSelected>>", lambda e: self.reload_notes())

        tk.Button(topbar, text="+ Add Subject", command=self.add_subject,
                 bg="#141627", fg="#00fff7", font=("Consolas", 10)).pack(side="left", padx=5)

        body_frame = tk.Frame(self.frame, bg="#0f111a")
        body_frame.pack(fill="both", expand=True, pady=10)

        left_frame = tk.Frame(body_frame, bg="#0f111a", width=250)
        left_frame.pack(side="left", fill="y", padx=(0, 10))
        left_frame.pack_propagate(False)

        tk.Label(left_frame, text="Notes", font=("Consolas", 12, "bold"),
                fg="#00fff7", bg="#0f111a").pack(pady=5)
        
        self.notes_list = tk.Listbox(left_frame, bg="#1f2233", fg="#00fff7",
                                    font=("Consolas", 10), selectbackground="#141627")
        self.notes_list.pack(fill="both", expand=True)
        self.notes_list.bind("<<ListboxSelect>>", self.load_note)

        tk.Button(left_frame, text="+ Add Note", command=self.add_note,
                 bg="#141627", fg="#00fff7", font=("Consolas", 10)).pack(pady=5)
        tk.Button(left_frame, text="Delete Note", command=self.delete_note,
                 bg="#141627", fg="#00fff7", font=("Consolas", 10)).pack(pady=5)

        right_frame = tk.Frame(body_frame, bg="#0f111a")
        right_frame.pack(side="left", fill="both", expand=True)

        tk.Label(right_frame, text="Title:", font=("Consolas", 12, "bold"),
                fg="#00fff7", bg="#0f111a").pack(anchor="w")
        self.title_entry = tk.Entry(right_frame, bg="#1f2233", fg="#00fff7",
                                   font=("Consolas", 12), insertbackground="#00fff7")
        self.title_entry.pack(fill="x", pady=5)

        tk.Label(right_frame, text="Body:", font=("Consolas", 12, "bold"),
                fg="#00fff7", bg="#0f111a").pack(anchor="w")
        self.body_text = tk.Text(right_frame, wrap="word", bg="#1f2233", fg="#00fff7",
                                font=("Consolas", 11), insertbackground="#00fff7")
        self.body_text.pack(fill="both", expand=True, pady=5)

        tk.Button(right_frame, text="Attach File", command=self.attach_file,
                 bg="#141627", fg="#00fff7", font=("Consolas", 10)).pack(pady=3)
        tk.Button(right_frame, text="Save Note", command=self.save_note,
                 bg="#141627", fg="#00fff7", font=("Consolas", 12)).pack(pady=10)

        self.current_note = None

    def load_subjects(self):
        c = self.db.cursor()
        c.execute("SELECT name FROM subjects WHERE username=?", (self.username,))
        subjects = [row[0] for row in c.fetchall()]
        self.subject_combo['values'] = subjects
        if subjects:
            self.subject_var.set(subjects[0])
            self.reload_notes()
        else:
            self.subject_var.set('')

    def add_subject(self):
        name = simpledialog.askstring("Add Subject", "Enter subject name:", parent=self.parent)
        if name:
            c = self.db.cursor()
            try:
                c.execute("INSERT INTO subjects (username, name) VALUES (?, ?)", 
                         (self.username, name.strip()))
                self.db.commit()
                self.load_subjects()
                messagebox.showinfo("Success", "Subject added.", parent=self.parent)
            except Exception as e:
                messagebox.showerror("Error", "Subject could not be added.", parent=self.parent)

    def reload_notes(self):
        self.notes_list.delete(0, 'end')
        self.current_note = None
        subject = self.subject_var.get()
        if not subject:
            return
        c = self.db.cursor()
        c.execute("SELECT id, title FROM notes WHERE username=? AND subject=?", 
                 (self.username, subject))
        self.notes = c.fetchall()
        for _, title in self.notes:
            self.notes_list.insert('end', title)
        self.title_entry.delete(0, 'end')
        self.body_text.delete(1.0, 'end')

    def add_note(self):
        subject = self.subject_var.get()
        if not subject:
            messagebox.showwarning("No Subject", "Please add or select a subject first.", 
                                 parent=self.parent)
            return
        title = simpledialog.askstring("Note Title", "Enter note title:", parent=self.parent)
        if not title:
            return
        c = self.db.cursor()
        c.execute("INSERT INTO notes (username, subject, title, body) VALUES (?, ?, ?, ?)",
                  (self.username, subject, title.strip(), ""))
        self.db.commit()
        self.reload_notes()

    def load_note(self, _):
        sel = self.notes_list.curselection()
        if not sel:
            return
        index = sel[0]
        nid, title = self.notes[index]
        c = self.db.cursor()
        c.execute("SELECT title, body FROM notes WHERE id=?", (nid,))
        row = c.fetchone()
        self.current_note = nid
        self.title_entry.delete(0, 'end')
        self.title_entry.insert(0, row[0])
        self.body_text.delete(1.0, 'end')
        self.body_text.insert('end', row[1])

    def save_note(self):
        if not self.current_note:
            messagebox.showwarning("No Note", "No note selected.", parent=self.parent)
            return
        title = self.title_entry.get().strip()
        body = self.body_text.get(1.0, 'end-1c')
        c = self.db.cursor()
        c.execute("UPDATE notes SET title=?, body=? WHERE id=?", (title, body, self.current_note))
        self.db.commit()
        messagebox.showinfo("Success", "Note saved.", parent=self.parent)
        self.reload_notes()

    def delete_note(self):
        sel = self.notes_list.curselection()
        if not sel:
            return
        if not messagebox.askyesno("Delete Note", "Are you sure you want to delete this note?", 
                                  parent=self.parent):
            return
        index = sel[0]
        nid, _ = self.notes[index]
        c = self.db.cursor()
        c.execute("DELETE FROM notes WHERE id=?", (nid,))
        self.db.commit()
        self.reload_notes()

    def attach_file(self):
        path = filedialog.askopenfilename(parent=self.parent)
        if not path:
            return
        dest_dir = os.path.join("data", "files", self.username)
        os.makedirs(dest_dir, exist_ok=True)
        filename = os.path.basename(path)
        dest = os.path.join(dest_dir, filename)
        if not os.path.exists(dest):
            shutil.copy(path, dest)
        ext = filename.split('.')[-1].lower()
        markdown = ""
        if ext in ["png", "jpg", "jpeg", "gif", "bmp"]:
            markdown = f"![{filename}]({dest.replace(os.sep, '/')})"
        else:
            markdown = f"[{filename}]({dest.replace(os.sep, '/')})"
        self.body_text.insert('insert', markdown + "\n")
        messagebox.showinfo("Attached", f"File {filename} attached in note.", parent=self.parent)
