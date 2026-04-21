import sqlite3
import database
import security
from fastapi import APIRouter, HTTPException, File, Form, UploadFile
from pydantic import BaseModel
from typing import Optional, List
import json
import datetime
import os
import shutil

# Main router for API endpoints
api_router = APIRouter()

# --- DIRECTORY FOR ATTACHED EXAMS ---
# Creates an 'uploads' folder in the root directory if it doesn't exist
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

# NEW: Model for updating doctor settings
class UpdateDoctorSchema(BaseModel):
    doctor_id: int
    name: str
    email: str
    password: Optional[str] = None # Optional, only updated if provided

class PatientCreateSchema(BaseModel):
    document_id: str 
    names: str
    surnames: str
    gender: str 
    birthdate: str 
    occupation: str
    marital_status: str
    blood_type: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    allergic: Optional[str] = "{}"
    cardiovascular: Optional[str] = "{}"
    personal_background: Optional[str] = "{}" 
    gynecological_background: Optional[str] = "{}"
    family_background: Optional[str] = "{}"
    motive: str
    diagnostic: str
    current_illness: str

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
        # UPDATED: We now extract the 'name' column as well
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
        # UPDATED: Inserting the doctor's name
        cursor.execute("INSERT INTO doctors (name, user, password) VALUES (?, ?, ?)", (name, email, secure_password))
        connection.commit()
        connection.close()
        return {"status" : "success", "msg": "Doctor registered successfully"}
    except sqlite3.IntegrityError:
        return {"status" : "error", "msg": "Email already registered"}
    except Exception as e:
        return {"status" : "error", "msg": f"Registration error: {str(e)}"}

def internal_get_all_active_patients():
    """Retrieves list of active patients for the dashboard table"""
    try:
        conn = database.connect()
        cursor = conn.cursor()
        # ENFORCED SOFT DELETE: is_active = 1
        cursor.execute("SELECT document_id, names, surnames FROM patients WHERE is_active = 1")
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

# NEW: Endpoint to update doctor settings
@api_router.post("/doctor/update")
def update_doctor_settings(data: UpdateDoctorSchema):
    """Updates doctor's profile. Checks if password update is requested."""
    try:
        conn = database.connect()
        cursor = conn.cursor()
        
        if data.password and data.password.strip():
            # Update including new hashed password
            sec_pass = security.hash_password(data.password)
            cursor.execute("UPDATE doctors SET name = ?, user = ?, password = ? WHERE id = ?", 
                           (data.name, data.email, sec_pass, data.doctor_id))
        else:
            # Update only name and email
            cursor.execute("UPDATE doctors SET name = ?, user = ? WHERE id = ?", 
                           (data.name, data.email, data.doctor_id))
            
        conn.commit()
        conn.close()
        return {"status": "success", "msg": "Perfil actualizado exitosamente."}
    except sqlite3.IntegrityError:
        return {"status": "error", "msg": "El correo ingresado ya está en uso por otra cuenta."}
    except Exception as e:
        return {"status": "error", "msg": f"Error updating doctor: {str(e)}"}


@api_router.get("/patients/all", response_model=List[PatientListItem])
def get_patients_all():
    return internal_get_all_active_patients()

# NEW: Endpoint to get the 5 most recent active patients for the Summary view
@api_router.get("/patients/recent", response_model=List[PatientListItem])
def get_recent_patients():
    try:
        conn = database.connect()
        cursor = conn.cursor()
        # ENFORCED SOFT DELETE: is_active = 1, ordered by latest insertion
        cursor.execute("SELECT document_id, names, surnames FROM patients WHERE is_active = 1 ORDER BY rowid DESC LIMIT 5")
        patients = cursor.fetchall()
        conn.close()
        return [PatientListItem(document_id=p[0], names=p[1], surnames=p[2]) for p in patients]
    except Exception:
        return []

# --- PATIENT CREATION (UPDATED FOR MULTIPLE FILES & FULL QUERY DATA) ---
@api_router.post("/patient/create")
async def create_patient_history(
    # Patient Data
    document_id: str = Form(...),
    names: str = Form(...),
    surnames: str = Form(...),
    gender: str = Form(...),
    birthdate: str = Form(...),
    occupation: str = Form(""),
    marital_status: str = Form(""),
    allergic: str = Form("{}"),
    cardiovascular: str = Form("{}"),
    personal_background: str = Form("{}"),
    # Query Data
    motive: str = Form(...),
    diagnostic: str = Form(...),
    current_illness: str = Form(...),
    weight: float = Form(0.0),
    height: float = Form(0.0),
    temperature: float = Form(0.0),
    blood_pressure: str = Form(""),
    heart_rate: int = Form(0),
    respiratory_rate: int = Form(0),
    physical_examination: str = Form("{}"),
    # Multiple Files Upload
    exam_files: Optional[List[UploadFile]] = File(None)
):
    """Handles medical history creation AND their complete initial query with multiple files"""
    try:
        conn = database.connect()
        cursor = conn.cursor()
        
        # 1. Insert Patient
        query_patient = '''
            INSERT INTO patients (
                document_id, names, surnames, gender, birthdate, 
                occupation, marital_status,
                allergic, cardiovascular, personal_background
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        cursor.execute(query_patient, (
            document_id, names, surnames, gender, birthdate, 
            occupation, marital_status,
            allergic, cardiovascular, personal_background
        ))

        # 2. Insert Initial Query
        current_date = datetime.date.today().strftime("%Y-%m-%d")
        query_consult = '''
            INSERT INTO queries (
                patient_document_id, date, motive, current_illness, diagnostic, 
                weight, height, blood_pressure, heart_rate, respiratory_rate, temperature,
                physical_examination
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        cursor.execute(query_consult, (
            document_id, current_date, motive, current_illness, diagnostic, 
            weight, height, blood_pressure, heart_rate, respiratory_rate, temperature,
            physical_examination
        ))
        
        new_query_id = cursor.lastrowid
        
        # 3. Handle Multiple Files
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
        return {"status": "success", "msg": "Historia médica y consulta inicial creadas exitosamente."}
        
    except sqlite3.IntegrityError:
        return {"status": "error", "msg": "La cédula de este paciente ya existe en el sistema."}
    except Exception as e:
        return {"status": "error", "msg": f"Error en la base de datos: {str(e)}"}

# --- PATIENT FULL DETAILS ENDPOINT ---
@api_router.get("/patient/details/{document_id}")
def get_patient_details(document_id: str):
    """Fetches patient info, all their queries, and attached exams"""
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

# --- EVOLUTIONARY QUERY & FILE UPLOAD (UPDATED FOR MULTIPLE FILES) ---
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
    physical_examination: str = Form("{}"),
    # Multiple Files Support
    exam_files: Optional[List[UploadFile]] = File(None) 
):
    """Handles adding evolutionary queries with multiple optional file attachments"""
    try:
        conn = database.connect()
        cursor = conn.cursor()
        
        current_date = datetime.date.today().strftime("%Y-%m-%d")
        
        query_sql = '''
            INSERT INTO queries (
                patient_document_id, date, motive, current_illness,
                weight, height, blood_pressure, heart_rate, respiratory_rate, temperature,
                physical_examination, diagnostic, treatment
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        cursor.execute(query_sql, (
            patient_document_id, current_date, motive, current_illness,
            weight, height, blood_pressure, heart_rate, respiratory_rate, temperature,
            physical_examination, diagnostic, treatment
        ))
        
        new_query_id = cursor.lastrowid
        
        # Handle Multiple File Uploads
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