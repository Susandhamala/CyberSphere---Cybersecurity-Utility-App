-------------------------------------------------------------------------------
                            CYBERSPHERE
                    Property of Susan Dhamala
                      All Rights Reserved
-------------------------------------------------------------------------------
import sqlite3
import os

def get_db():
    os.makedirs("data", exist_ok=True)
    db_path = os.path.join("data", "cybersphere.db")
    conn = sqlite3.connect(db_path)
    create_tables(conn)
    return conn

def create_tables(conn):
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password_hash TEXT NOT NULL)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS subjects
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT NOT NULL,
                  name TEXT NOT NULL)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS notes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT NOT NULL,
                  subject TEXT NOT NULL,
                  title TEXT NOT NULL,
                  body TEXT,
                  created TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS passwords
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT NOT NULL,
                  service TEXT NOT NULL,
                  account TEXT NOT NULL,
                  password TEXT NOT NULL,
                  created TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS exams
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT NOT NULL,
                  subject TEXT NOT NULL,
                  date TEXT NOT NULL,
                  time TEXT,
                  location TEXT,
                  notes TEXT,
                  created TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
