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
DIAGNOSTICS = ["Viral infection", "Healthy", "Gastritis", "Controlled Hypertension", "Sprain"]

def random_date(start_year=1950, end_year=2005):
    """Generates a random date in YYYY-MM-DD format."""
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return (start_date + timedelta(days=random_number_of_days)).strftime("%Y-%m-%d")

def generate_doctors(cursor):
    """Injects default mock doctors."""
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
    """Injects random patients securely linked only to mock doctors."""
    print(f"Seeding {num_patients} patients...")
    
    # FETCH EXACT IDs FOR THE MOCK DOCTORS TO PREVENT ID COLLISIONS
    cursor.execute("SELECT id FROM doctors WHERE user IN ('house@hospital.com', 'juan@hospital.com')")
    valid_doctor_ids = [row[0] for row in cursor.fetchall()]
    
    if not valid_doctor_ids:
        print("Mock doctors not found. Skipping patient seeding.")
        return

    for _ in range(num_patients):
        doc_id = f"V-{random.randint(10000000, 30000000)}"
        doctor_id = random.choice(valid_doctor_ids) 
        gender = random.choice(["male", "female"])
        name = random.choice(FIRST_NAMES_MALE) if gender == "male" else random.choice(FIRST_NAMES_FEMALE)
        
        try:
            # Insertion with ALL fields from the database
            cursor.execute('''
                INSERT INTO patients (
                    document_id, doctor_id, referred, names, surnames, gender, birthdate, 
                    marital_status, address, phone, cardiovascular, pulmonary, neurological, 
                    urogenital, eyes, osteomuscular, metabolic, allergic, surgical, orl, 
                    habits, family_background
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                doc_id, doctor_id, "No", name, random.choice(SURNAMES), gender, random_date(), 
                "Single", "Caracas, Distrito Capital", "0414-1234567",
                "Normal", "Symmetrical thorax", "Conscious patient",
                "Menarche at 12" if gender == "female" else "Normal",
                "Isocoric pupils", "Preserved strength", "Denies diabetes", "Penicillin",
                "Appendectomy (2015)", "Normal", "Social smoking", "Hypertensive father"
            ))
            
            # Generate querys for the patients
            num_queries = random.randint(1, 3)
            for _ in range(num_queries):
                cursor.execute('''
                    INSERT INTO queries (
                       patient_document_id, date, motive, current_illness,
                       weight, height, blood_pressure, heart_rate, respiratory_rate,
                       temperature, physical_examination, electrocardiogram, chest_xray, 
                       laboratory, diagnostic, treatment
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    doc_id, random_date(2025, 2026), "Routine checkup", 
                    "Patient attends for general checkup without acute symptoms.",
                    round(random.uniform(50.0, 90.0), 2), round(random.uniform(1.50, 1.90), 2), 
                    f"{random.randint(110, 130)}/{random.randint(70, 85)}", random.randint(60, 100), 
                    random.randint(12, 20), round(random.uniform(36.5, 37.5), 1), 
                    "[BMI: 22.5 (Normal) | QTc: 400 ms]\nPatient in apparent good general condition.",
                    "Normal sinus rhythm", "Clear lungs", "Glucose 90 mg/dL",
                    random.choice(DIAGNOSTICS), "Maintain a healthy lifestyle."
                ))
                
        except sql.IntegrityError:
            continue

def run_seed():
    print("--- Starting Database Seeding ---")
    try:
        db.create_tables() 
        conn = db.connect()
        cursor = conn.cursor()
        generate_doctors(cursor)
        generate_patients_and_queries(cursor, num_patients=15)
        conn.commit()
        conn.close()
        print("--- Seeding Completed Successfully! ---")
    except Exception as e:
        print(f"Error during seeding: {e}")

if __name__ == "__main__":
    run_seed()