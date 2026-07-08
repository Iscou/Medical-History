import sqlite3
import database
import security
from fastapi import APIRouter, HTTPException, File, Form, UploadFile
from pydantic import BaseModel
from typing import Optional, List
from fastapi.responses import FileResponse
import json
import datetime
import os
import sys 
import shutil

# Main router for API endpoints
api_router = APIRouter()

# --- DIRECTORY FOR ATTACHED EXAMS (PYINSTALLER COMPATIBLE) ---
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
    UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "..", "uploads"))

os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- DATA MODELS (PYDANTIC) ---
class LoginData(BaseModel):
    email: str
    password: str

class RegisterData(BaseModel):
    name: str 
    email: str
    password: str

class UpdateDoctorSchema(BaseModel):
    doctor_id: int
    name: str
    email: str
    password: Optional[str] = None 

class PatientListItem(BaseModel):
    document_id: str
    names: str
    surnames: str

# --- INTERNAL FUNCTIONS ---
def verify_doctor_login(email, password):
    """Checks credentials against database"""
    try:
        connection = database.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT id, user, password, name FROM doctors WHERE user = ?", (email,))
        doctor = cursor.fetchone()
        connection.close()
        
        if doctor: 
            doctor_id = doctor[0]
            hashed_password_db = doctor[2] 
            doctor_name = doctor[3]
            if security.verify_password(password, hashed_password_db):
                return {"status" : "success", "msg": " Successfully login", "doctor_id" : doctor_id, "doctor_name": doctor_name}
            
        return {"status" : "error", "msg": "Invalid credentials"}
    except Exception as e:
        return {"status" : "error", "msg": f"Server error: {str(e)}"}

def sign_in_doctor(name, email, password):
    """Registers a new doctor securely"""
    try:
        connection = database.connect()
        cursor = connection.cursor()
        secure_password = security.hash_password(password)
        cursor.execute("INSERT INTO doctors (name, user, password) VALUES (?, ?, ?)", (name, email, secure_password))
        connection.commit()
        connection.close()
        return {"status" : "success", "msg": "Doctor registered successfully"}
    except sqlite3.IntegrityError:
        return {"status" : "error", "msg": "Email already registered"}
    except Exception as e:
        return {"status" : "error", "msg": f"Registration error: {str(e)}"}

def internal_get_all_active_patients(doctor_id: int):
    """Retrieves list of active patients FOR A SPECIFIC DOCTOR"""
    try:
        conn = database.connect()
        cursor = conn.cursor()
        # Privacity: Only carry patients of the doctor that log in
        cursor.execute("SELECT document_id, names, surnames FROM patients WHERE is_active = 1 AND doctor_id = ?", (doctor_id,))
        patients = cursor.fetchall()
        conn.close()
        
        result = []
        for p in patients:
            result.append(PatientListItem(document_id=p[0], names=p[1], surnames=p[2]))
        return result
    except Exception as e:
        return []

# --- API ROUTER ENDPOINTS ---
@api_router.post("/login")
def process_login(data: LoginData):
    return verify_doctor_login(data.email, data.password)

@api_router.post("/sign_up")
def process_signup(data: RegisterData):
    return sign_in_doctor(data.name, data.email, data.password)

@api_router.post("/doctor/update")
def update_doctor_settings(data: UpdateDoctorSchema):
    try:
        conn = database.connect()
        cursor = conn.cursor()
        
        if data.password and data.password.strip():
            sec_pass = security.hash_password(data.password)
            cursor.execute("UPDATE doctors SET name = ?, user = ?, password = ? WHERE id = ?", 
                           (data.name, data.email, sec_pass, data.doctor_id))
        else:
            cursor.execute("UPDATE doctors SET name = ?, user = ? WHERE id = ?", 
                           (data.name, data.email, data.doctor_id))
            
        conn.commit()
        conn.close()
        return {"status": "success", "msg": "Perfil actualizado exitosamente."}
    except sqlite3.IntegrityError:
        return {"status": "error", "msg": "El correo ingresado ya está en uso por otra cuenta."}
    except Exception as e:
        return {"status": "error", "msg": f"Error updating doctor: {str(e)}"}

# 
@api_router.get("/patients/all/{doctor_id}", response_model=List[PatientListItem])
def get_patients_all(doctor_id: int):
    return internal_get_all_active_patients(doctor_id)

@api_router.get("/patients/recent/{doctor_id}", response_model=List[PatientListItem])
def get_recent_patients(doctor_id: int):
    try:
        conn = database.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT document_id, names, surnames FROM patients WHERE is_active = 1 AND doctor_id = ? ORDER BY rowid DESC LIMIT 5", (doctor_id,))
        patients = cursor.fetchall()
        conn.close()
        return [PatientListItem(document_id=p[0], names=p[1], surnames=p[2]) for p in patients]
    except Exception:
        return []

# --- PATIENT CREATION  ---
@api_router.post("/patient/create")
async def create_patient_history(
    doctor_id: int = Form(...),
    document_id: str = Form(...),
    referred: str = Form("No"),
    names: str = Form(...),
    surnames: str = Form(...),
    gender: str = Form(...),
    birthdate: str = Form(...),
    marital_status: str = Form(""),
    address: str = Form(""),
    phone: str = Form(""),
    # background
    cardiovascular: str = Form(""),
    pulmonary: str = Form(""),
    neurological: str = Form(""),
    urogenital: str = Form(""),
    eyes: str = Form(""),
    osteomuscular: str = Form(""),
    metabolic: str = Form(""),
    allergic: str = Form(""),
    surgical: str = Form(""),
    orl: str = Form(""),
    habits: str = Form(""),
    family_background: str = Form(""),
    # Initial query
    motive: str = Form(...),
    current_illness: str = Form(...),
    diagnostic: str = Form(...),
    treatment: str = Form(""),
    weight: float = Form(0.0),
    height: float = Form(0.0),
    temperature: float = Form(0.0),
    blood_pressure: str = Form(""),
    heart_rate: int = Form(0),
    respiratory_rate: int = Form(0),
    physical_examination: str = Form(""),
    electrocardiogram: str = Form(""),
    chest_xray: str = Form(""),
    laboratory: str = Form(""),
    # Files
    exam_files: Optional[List[UploadFile]] = File(None)
):
    try:
        conn = database.connect()
        cursor = conn.cursor()
        
        # Insert patient
        query_patient = '''
            INSERT INTO patients (
                document_id, doctor_id, referred, names, surnames, gender, birthdate, 
                marital_status, address, phone,
                cardiovascular, pulmonary, neurological, urogenital, eyes, 
                osteomuscular, metabolic, allergic, surgical, orl, habits, family_background
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        cursor.execute(query_patient, (
            document_id, doctor_id, referred, names, surnames, gender, birthdate, 
            marital_status, address, phone,
            cardiovascular, pulmonary, neurological, urogenital, eyes, 
            osteomuscular, metabolic, allergic, surgical, orl, habits, family_background
        ))

        # Insert inital query
        current_date = datetime.date.today().strftime("%Y-%m-%d")
        query_consult = '''
            INSERT INTO queries (
                patient_document_id, date, motive, current_illness, diagnostic, treatment,
                weight, height, blood_pressure, heart_rate, respiratory_rate, temperature,
                physical_examination, electrocardiogram, chest_xray, laboratory
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        cursor.execute(query_consult, (
            document_id, current_date, motive, current_illness, diagnostic, treatment,
            weight, height, blood_pressure, heart_rate, respiratory_rate, temperature,
            physical_examination, electrocardiogram, chest_xray, laboratory
        ))
        
        new_query_id = cursor.lastrowid
        
        # File manager
        if exam_files:
            for file in exam_files:
                if file and file.filename:
                    safe_filename = f"{document_id}_{current_date}_{file.filename}"
                    file_path = os.path.join(UPLOAD_DIR, safe_filename)
                    
                    with open(file_path, "wb") as buffer:
                        shutil.copyfileobj(file.file, buffer)
                        
                    exam_sql = '''
                        INSERT INTO attached_exams (query_id, exam_name, file_path, upload_date)
                        VALUES (?, ?, ?, ?)
                    '''
                    cursor.execute(exam_sql, (new_query_id, file.filename, file_path, current_date))

        conn.commit()
        conn.close()
        return {"status": "success", "msg": "Historia médica creada exitosamente."}
        
    except sqlite3.IntegrityError:
        return {"status": "error", "msg": "La cédula de este paciente ya existe en el sistema."}
    except Exception as e:
        return {"status": "error", "msg": f"Error en la base de datos: {str(e)}"}

@api_router.get("/patient/details/{document_id}")
def get_patient_details(document_id: str):
    try:
        conn = database.connect()
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM patients WHERE document_id = ?", (document_id,))
        patient = cursor.fetchone()
        if not patient:
            return {"status": "error", "msg": "Patient not found"}
            
        cursor.execute("SELECT * FROM queries WHERE patient_document_id = ? ORDER BY date DESC, id DESC", (document_id,))
        queries = cursor.fetchall()
        
        cursor.execute("""
            SELECT ae.* FROM attached_exams ae
            JOIN queries q ON ae.query_id = q.id
            WHERE q.patient_document_id = ?
        """, (document_id,))
        exams = cursor.fetchall()
        
        conn.close()
        
        return {
            "status": "success",
            "patient": dict(patient),
            "queries": [dict(q) for q in queries],
            "exams": [dict(e) for e in exams]
        }
    except Exception as e:
        return {"status": "error", "msg": str(e)}

# --- EVOLUTIONARY QUERY & FILE UPLOAD ---
@api_router.post("/query/create")
async def add_evolutionary_query(
    patient_document_id: str = Form(...),
    motive: str = Form(...),
    current_illness: str = Form(...),
    diagnostic: str = Form(...),
    treatment: str = Form(""),
    weight: float = Form(0.0),
    height: float = Form(0.0),
    temperature: float = Form(0.0),
    blood_pressure: str = Form(""),
    heart_rate: int = Form(0),
    respiratory_rate: int = Form(0),
    physical_examination: str = Form(""),
    electrocardiogram: str = Form(""),
    chest_xray: str = Form(""),
    laboratory: str = Form(""),
    exam_files: Optional[List[UploadFile]] = File(None) 
):
    try:
        conn = database.connect()
        cursor = conn.cursor()
        
        current_date = datetime.date.today().strftime("%Y-%m-%d")
        
        query_sql = '''
            INSERT INTO queries (
                patient_document_id, date, motive, current_illness,
                weight, height, blood_pressure, heart_rate, respiratory_rate, temperature,
                physical_examination, electrocardiogram, chest_xray, laboratory, diagnostic, treatment
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        cursor.execute(query_sql, (
            patient_document_id, current_date, motive, current_illness,
            weight, height, blood_pressure, heart_rate, respiratory_rate, temperature,
            physical_examination, electrocardiogram, chest_xray, laboratory, diagnostic, treatment
        ))
        
        new_query_id = cursor.lastrowid
        
        if exam_files:
            for file in exam_files:
                if file and file.filename:
                    safe_filename = f"{patient_document_id}_{current_date}_{file.filename}"
                    file_path = os.path.join(UPLOAD_DIR, safe_filename)
                    
                    with open(file_path, "wb") as buffer:
                        shutil.copyfileobj(file.file, buffer)
                        
                    exam_sql = '''
                        INSERT INTO attached_exams (query_id, exam_name, file_path, upload_date)
                        VALUES (?, ?, ?, ?)
                    '''
                    cursor.execute(exam_sql, (new_query_id, file.filename, file_path, current_date))
        
        conn.commit()
        conn.close()
        return {"status": "success", "msg": "Consulta evolutiva guardada exitosamente."}
        
    except sqlite3.Error as e:
        return {"status": "error", "msg": f"Database error creating query: {str(e)}"}
    
# --- Download of adjunted files ---
@api_router.get("/exam/download/{exam_id}")
def download_exam(exam_id: int):
    try:
        conn = database.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT file_path, exam_name FROM attached_exams WHERE id = ?", (exam_id,))
        exam = cursor.fetchone()
        conn.close()

        if exam and os.path.exists(exam[0]):
            return FileResponse(path=exam[0], filename=exam[1])
        return {"status": "error", "msg": "El archivo no existe en el disco."}
    except Exception as e:
        return {"status": "error", "msg": str(e)}