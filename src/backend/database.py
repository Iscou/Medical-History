import sqlite3 as sql
import os
import sys

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
    DB_PATH = os.path.join(BASE_DIR, "medic_system.db")
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.normpath(os.path.join(BASE_DIR, "..", "..", "medic_system.db"))

def connect():
    conn = sql.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def create_tables():
    conexion = connect()
    cursor = conexion.cursor()

    # DOCTORS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT NOT NULL, 
            user TEXT UNIQUE NOT NULL, 
            password TEXT NOT NULL,
            signature_path TEXT 
        )          
    ''')
    
    # PATIENTS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            document_id TEXT PRIMARY KEY,
            doctor_id INTEGER NOT NULL,
            referred TEXT,
            names TEXT NOT NULL,
            surnames TEXT NOT NULL, 
            gender TEXT CHECK (gender IN ("male", "female")),
            birthdate TEXT NOT NULL,
            marital_status TEXT,
            address TEXT,
            phone TEXT,
            
            -- Functional Inquiry and Medical Background
            cardiovascular TEXT,
            pulmonary TEXT,
            neurological TEXT,
            urogenital TEXT,
            eyes TEXT,
            osteomuscular TEXT,
            metabolic TEXT,
            allergic TEXT,
            surgical TEXT,
            orl TEXT,
            habits TEXT,
            family_background TEXT,
            is_active INTEGER DEFAULT 1,
            
            FOREIGN KEY (doctor_id) REFERENCES doctors(id)
        )
    ''')

    # QUERIES
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS queries (
           id INTEGER PRIMARY KEY AUTOINCREMENT, 
           patient_document_id TEXT NOT NULL,
           date TEXT NOT NULL,
           motive TEXT NOT NULL, 
           current_illness TEXT NOT NULL,  

           weight REAL, height REAL, blood_pressure TEXT,      
           heart_rate INTEGER, respiratory_rate INTEGER, temperature REAL,         

           physical_examination TEXT,
           electrocardiogram TEXT,
           chest_xray TEXT,
           laboratory TEXT,

           diagnostic TEXT NOT NULL,
           treatment TEXT,

           FOREIGN KEY (patient_document_id) REFERENCES patients (document_id)                                    
        )   
    ''')

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attached_exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,             
            query_id INTEGER NOT NULL,       
            exam_name TEXT NOT NULL,
            file_path TEXT NOT NULL,       
            upload_date TEXT NOT NULL,       
            FOREIGN KEY (query_id) REFERENCES queries (id)                 
        )
    """)

    # OTP CODES (Email verification)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS otp_codes (
            email TEXT PRIMARY KEY,
            code TEXT NOT NULL,
            expires_at DATETIME NOT NULL
        )
    ''')

    conexion.commit()
    conexion.close()

if __name__ == "__main__":
    create_tables()