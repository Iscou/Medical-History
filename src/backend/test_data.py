import database as db
import sqlite3 as sql
import json
import random
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
        ("DrHouse", "1234"),
        ("DrJuan", "admin"),
        ("DraPerez", "password")
    ]
    for doc in doctors:
        try:
            cursor.execute("INSERT INTO doctors (user, password) VALUES (?, ?)", doc)
        except sql.IntegrityError:
            pass # Ignore if they already exist

def generate_patients_and_queries(cursor, num_patients=10):
    print(f"Seeding {num_patients} patients and their queries...")
    
    for _ in range(num_patients):
        # Generate Patient Data
        gender = random.choice(["male", "female"])
        name = random.choice(FIRST_NAMES_FEMALE) if gender == "female" else random.choice(FIRST_NAMES_MALE)
        surname = random.choice(SURNAMES)
        doc_id = f"V-{random.randint(10000000, 30000000)}"
        
        # Build JSON Backgrounds
        personal_bg = {
            "chronic_diseases": random.choice(["None", "Asthma", "Diabetes"]),
            "surgeries": random.choice(["None", "Appendectomy 2015", "Tonsillectomy"]),
            "habits": {"tobacco": random.choice(["Yes", "No"]), "alcohol": "Social"}
        }
        
        family_bg = {
            "diabetes": random.choice(["None", "Mother", "Father"]),
            "hypertension": random.choice(["None", "Grandfather"])
        }
        
        gynecological_bg = {}
        if gender == "female":
            gynecological_bg = {
                "menarche_age": random.randint(11, 15),
                "pregnancies": random.randint(0, 3),
                "contraceptive": random.choice(["Pills", "IUD", "None"])
            }
            
        # Insert Patient
        try:
            cursor.execute('''
                INSERT INTO patients (
                    document_id, names, surnames, gender, birthdate, 
                    emergency_contact_name, emergency_contact_phone, blood_type, 
                    occupation, marital_status, cardiovascular, respiratory, 
                    personal_background, gynecological_background, family_background
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                doc_id, name, surname, gender, random_date(),
                "Emergency Contact", f"0414-{random.randint(1000000, 9999999)}",
                random.choice(BLOOD_TYPES), random.choice(OCCUPATIONS), random.choice(MARITAL_STATUS),
                random.choice(["Normal", "Slight arrhythmia", ""]), random.choice(["Clear", "Wheezing", ""]),
                json.dumps(personal_bg), json.dumps(gynecological_bg), json.dumps(family_bg)
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