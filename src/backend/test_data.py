import database as db
import sqlite3 as sql
import json
import random
import security
from datetime import datetime, timedelta

# --- MOCK DATA POOLS ---
FIRST_NAMES_MALE = ["Carlos", "Luis", "Miguel", "Alejandro", "Jose"]
FIRST_NAMES_FEMALE = ["Ana", "Maria", "Sofia", "Valeria", "Laura"]
SURNAMES = ["Perez", "Gomez", "Rodriguez", "Zerpa", "Mendoza", "Gonzalez", "Silva"]
BLOOD_TYPES = ['A+', 'A-', 'B+', 'O+', 'O-']
OCCUPATIONS = ["Engineer", "Teacher", "Student", "Lawyer", "Accountant", "Artist"]
MARITAL_STATUS = ["Single", "Married", "Divorced", "Widowed"]
MOTIVES = ["Fever and headache", "Routine checkup", "Stomach pain", "High blood pressure check", "Chest pain"]
DIAGNOSTICS = ["Viral infection", "Healthy", "Gastritis", "Hypertension", "Muscle strain"]

def random_date(start_year=1950, end_year=2005):
    """Generates a random date in YYYY-MM-DD format."""
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + timedelta(days=random_number_of_days)
    return random_date.strftime("%Y-%m-%d")

def generate_doctors(cursor):
    print("Seeding doctors...")
    doctors = [
        ("Dr. Gregory House", "house@hospital.com", "1234"),
        ("Dr. Juan Reyes", "juan@hospital.com", "admin")
    ]
    for doc in doctors:
        try:
            sec_pass = security.hash_password(doc[2])
            cursor.execute("INSERT INTO doctors (name, user, password) VALUES (?, ?, ?)", (doc[0], doc[1], sec_pass))
        except sql.IntegrityError:
            pass 

def generate_patients_and_queries(cursor, num_patients=10):
    print(f"Seeding {num_patients} patients...")
    for _ in range(num_patients):
        doc_id = f"V-{random.randint(10000000, 30000000)}"
        
        doctor_id = random.choice([1, 2]) 
        
        try:
            cursor.execute('''
                INSERT INTO patients (
                    document_id, doctor_id, names, surnames, gender, birthdate, 
                    address, phone
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                doc_id, doctor_id, "Nombre", "Apellido", "male", "1990-01-01", 
                "Caracas, Venezuela", "0414-0000000"
            ))
            # Generate 1 to 3 queries for this patient
            num_queries = random.randint(1, 3)
            for _ in range(num_queries):
                phys_exam = {
                    "general_impression": "Stable",
                    "abdomen": "Soft, painless",
                    "head": "Normocephalic"
                }
                
                cursor.execute('''
                    INSERT INTO queries (
                       patient_document_id, date, motive, current_illness,
                       weight, height, blood_pressure, heart_rate, respiratory_rate,
                       temperature, physical_examination, diagnostic, treatment
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    doc_id, random_date(2025, 2026), random.choice(MOTIVES), 
                    "Patient reports symptoms starting 2 days ago.",
                    round(random.uniform(50.0, 90.0), 1), round(random.uniform(1.50, 1.90), 2), 
                    f"{random.randint(110, 130)}/{random.randint(70, 85)}", random.randint(60, 100), 
                    random.randint(12, 20), round(random.uniform(36.5, 38.5), 1), 
                    json.dumps(phys_exam), random.choice(DIAGNOSTICS), "Rest and hydration."
                ))
                
        except sql.IntegrityError:
            continue # Skip if random ID duplicates (rare)

def run_seed():
    print("--- Starting Database Seeding ---")
    try:
        # Assumes database.py creates the tables if they don't exist
        db.create_tables() 
        
        conexion = db.connect()
        cursor = conexion.cursor()
        
        generate_doctors(cursor)
        generate_patients_and_queries(cursor, num_patients=15)
        
        conexion.commit()
        conexion.close()
        print("--- Seeding Completed Successfully! ---")
        
    except Exception as e:
        print(f"Error during seeding: {e}")

if __name__ == "__main__":
    run_seed()