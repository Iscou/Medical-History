import eel 
import sqlite3 as sql
import database as db # We import the database.py to use it 
import json
from datetime import datetime

# We initialize the folder of the frontend
# eel.init('src/frontend')

# function to register a doctor
# This line below allows than the js execute this function
@eel.expose 
def sign_in_doctor(user, password):
    print(f"Intento de registro del nuevo doctor: {user}")

    # validation of whether the username or password is null
    if not user or not password:
        return {"status": "error", "msg": "El usuario y la contraseña son obligatorios"}
    
    try: 
        conexion = db.connect()
        cursor = conexion.cursor()

        # Data insertion
        cursor.execute("INSERT INTO doctors (user, password) VALUES (?,?)", (user, password))

        # We seal the insertion
        conexion.commit()

        # We request to SQLite the id than has just assigned this doctor to him
        new_id = cursor.lastrowid

        conexion.close()

        return {
            "status":"success",
            "msg":"Doctor registrado exitosamente",
            "doctor_id": new_id
        }
    
    except sql.IntegrityError:
        # Validation for doctors trying to register with an existing name
        return {
            "status": "error", 
            "msg": f"El nombre de usuario '{user}' ya está registrado. Elige otro."
        }
    except Exception as e:
        # Any type of unexpected error on the part of the OS
        return {
            "status": "fatal", 
            "msg": f"Error interno del servidor al registrar: {str(e)}"
        }
    
# function to login a doctor 
@eel.expose
def verify_doctor_login (user, password):
    print(f"Try of login for {user}")

    try:
        # We open the conexion using database.py 
        conexion = db.connect()
        cursor = conexion.cursor()

        # We fetch the medic
        cursor.execute("SELECT * FROM doctors WHERE user = ? AND password = ?", (user, password))
        doctor = cursor.fetchone()
        conexion.close()


        if doctor: 
            # doctor[0] is the autoincremental id of the db
            return {
                "status" : "success",
                "msg": " Successfully login",
                "doctor_id" : doctor[0]
            }
        else:
            return{
                "status":"error",
                "msg": "Invalid user or password "
            }
    except Exception as e:
        # If something is not working as it should, then we notify the frontend without the program closing
        return {
            "status": "fatal",
            "msg": f"Server error: {str(e)}"
        }
    
# Setup of date
def setup_intern_date(date):
    try:
        valid_date = datetime.strptime(date, "%Y-%m-%d").date()
        return str(valid_date)
    except ValueError:
        raise ValueError(f"Formato de fecha inválido: {date}. Use YYYY-MM-DD.")  

#@DiegoACastroQ you most save the file in a folder like "src/backend/uploads/"
# because send the file it's not optimal since you have to send the .py file to 
# be saved instead of saving it directly with the JS.
@eel.expose
def upload_attached_exams(query_id, exam_name, file_path, upload_date):
    print(f"Uploading exam: {exam_name} for query ID: {query_id}")

    try:
        # We format the date in the desired scheme
        formatted_date = setup_intern_date(upload_date)

        # We open the connection with the db
        connection = db.connect()
        cursor = connection.cursor()

        # Save of the attachment
        cursor.execute('''
            INSERT INTO attached_exams(
                query_id, exam_name, file_path, upload_date           
            ) VALUES (?, ?, ?, ?)
        ''', (query_id, exam_name, file_path, formatted_date))

        # We seal the box. Only one table is updated here.
        connection.commit()
        connection.close()

        return {
            "status": "success", 
            "msg": f"Attached file {exam_name} saved successfully." 
        }
        
    except sql.IntegrityError:
        # Integrity error here usually means the query_id doesn't exist
        return {
            "status": "error", 
            "msg": f"Database constraint failed. Ensure the query ID '{query_id}' exists."
        }
    except ValueError as ve:
        return {"status": "error", "msg": str(ve)}
    except Exception as e:
        return {"status": "fatal", "msg": f"Server error: {str(e)}"}

        
@eel.expose 
def register_new_patient_and_consult (patient, consult):
    """
    We recibe two dictionaries from Javascript:
    patient = {"document_id": "V-123", "names": "Juan", ... "personal_background": {...}}
    consult = {"date": "2026-04-04", "motive": "Fiebre", ... "physical_examination": {...}}
    """
    print(f"Registrando nuevo paciente: {patient.get('document_id')}")
    
    try:
        # We clean and validate the date using "setup_intern_date(date)"
        datebirth = setup_intern_date(patient['birthdate'])
        consult_date = setup_intern_date(consult['date'])
        
        # We package the internal dictionarios into plain text JSON format
        # We use get so that if the frontend doesn't send anything, it puts an empty dictionary by default.
        bg_personal_json = json.dumps(patient.get('personal_background', {}))
        bg_gineco_json = json.dumps(patient.get('gynecological_background', {}))
        bg_familiar_json = json.dumps(patient.get('family_background', {}))
        
        examen_phisic_json = json.dumps(consult.get('physical_examination', {}))

        # We open the connection to the db
        conexion = db.connect()
        cursor = conexion.cursor()
        
        # ---- Start of the atomic transaction ----
        # If the consultation fails, the patient is not saved, and vice versa. It's all or nothing.
        
        # Save of the patient 
        cursor.execute('''
            INSERT INTO patients (
                document_id, names, surnames, gender, birthdate, 
                emergency_contact_name, emergency_contact_phone, blood_type, 
                occupation, marital_status, personal_background, 
                gynecological_background, family_background
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            patient['document_id'], patient['names'], patient['surnames'], 
            patient['gender'], datebirth, patient.get('emergency_contact_name', ''), 
            patient.get('emergency_contact_phone', ''), patient['blood_type'], 
            patient['occupation'], patient['marital_status'], 
            bg_personal_json, bg_gineco_json, bg_familiar_json
        ))
        
        # Save his first consult
        cursor.execute('''
            INSERT INTO queries (
               patient_document_id, date, motive, current_illness,
               weight, height, blood_pressure, heart_rate, respiratory_rate,
               temperature, physical_examination, diagnostic, treatment
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            patient['document_id'], consult_date, consult['motive'], 
            consult['current_illness'], consult.get('weight'), consult.get('height'), 
            consult.get('blood_pressure'), consult.get('heart_rate'), 
            consult.get('respiratory_rate'), consult.get('temperature'), 
            examen_phisic_json, consult['diagnostic'], consult.get('treatment', '')
        ))

        # We capture the newly generated ID for the consultation
        new_query_id = cursor.lastrowid
        # We seal the box. If we get this far without errors, both tables will be updated.
        conexion.commit()
        conexion.close()
        
        return {
            "status": "success", 
            "mensaje": f"Paciente {patient['names']} y su primera consulta guardados exitosamente.",
            "query_id": new_query_id
        }
        
    except sql.IntegrityError:
        return {
            "status": "error", 
            "mensaje": f"El paciente con cédula {patient.get('document_id')} ya existe en el sistema."
        }
    except ValueError as ve:
        return {"status": "error", "mensaje": str(ve)}
    except Exception as e:
        return {"status": "fatal", "mensaje": f"Error del servidor: {str(e)}"}

@eel.expose
def update_patient_data(patient):
    """
    Receives the FULL modified patient dictionary again from Javascript and overwrites the DB row.
    """
    print(f"Updating data for patient: {patient.get('document_id')}")
    
    try:
        birthdate = setup_intern_date(patient['birthdate'])
        
        # Repackage JSONs
        bg_personal_json = json.dumps(patient.get('personal_background', {}))
        bg_gineco_json = json.dumps(patient.get('gynecological_background', {}))
        bg_familiar_json = json.dumps(patient.get('family_background', {}))
        
        conexion = db.connect()
        cursor = conexion.cursor()
        
        # The Full Overwrite approach (We update everything EXCEPT the primary key)
        cursor.execute('''
            UPDATE patients SET 
                names = ?, surnames = ?, gender = ?, birthdate = ?, 
                emergency_contact_name = ?, emergency_contact_phone = ?, blood_type = ?, 
                occupation = ?, marital_status = ?, 
                cardiovascular = ?, respiratory = ?, gastrointestinal = ?, 
                nephrourological = ?, neurological = ?, infectious_diseases = ?, 
                endocrinological = ?, traumatological = ?, allergic = ?, 
                personal_background = ?, gynecological_background = ?, family_background = ?
            WHERE document_id = ?
        ''', (
            patient['names'], patient['surnames'], patient['gender'], birthdate,
            patient.get('emergency_contact_name', ''), patient.get('emergency_contact_phone', ''), 
            patient['blood_type'], patient['occupation'], patient['marital_status'],
            patient.get('cardiovascular', ''), patient.get('respiratory', ''), 
            patient.get('gastrointestinal', ''), patient.get('nephrourological', ''), 
            patient.get('neurological', ''), patient.get('infectious_diseases', ''), 
            patient.get('endocrinological', ''), patient.get('traumatological', ''), 
            patient.get('allergic', ''),
            bg_personal_json, bg_gineco_json, bg_familiar_json,
            patient['document_id'] # The WHERE clause condition
        ))
        
        # Seal the update
        conexion.commit()
        conexion.close()
        
        return {
            "status": "success", 
            "msg": "Patient data updated successfully."
        }
        
    except ValueError as ve:
        return {"status": "error", "msg": str(ve)}
    except Exception as e:
        return {"status": "fatal", "msg": f"Server error updating patient: {str(e)}"}

@eel.expose
def add_new_consult(consult):
    """
    Adds a new evolutionary consultation to an existing patient.
    """
    print(f"Adding new consult for patient ID: {consult.get('patient_document_id')}")
    
    try:
        consult_date = setup_intern_date(consult['date'])
        examen_phisic_json = json.dumps(consult.get('physical_examination', {}))
        
        conexion = db.connect()
        cursor = conexion.cursor()
        
        cursor.execute('''
            INSERT INTO queries (
               patient_document_id, date, motive, current_illness,
               weight, height, blood_pressure, heart_rate, respiratory_rate,
               temperature, physical_examination, diagnostic, treatment
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            consult['patient_document_id'], consult_date, consult['motive'], 
            consult['current_illness'], consult.get('weight'), consult.get('height'), 
            consult.get('blood_pressure'), consult.get('heart_rate'), 
            consult.get('respiratory_rate'), consult.get('temperature'), 
            examen_phisic_json, consult['diagnostic'], consult.get('treatment', '')
        ))
        
        # We capture the newly generated ID for the consultation
        new_query_id = cursor.lastrowid
        conexion.commit()
        conexion.close()
        
        return {
            "status": "success", 
            "msg": "New medical consult added successfully.",
            "query_id": new_query_id
        }
        
    except Exception as e:
        return {"status": "fatal", "msg": f"Server error adding consult: {str(e)}"}

@eel.expose
def get_full_patient_history(document_id):
    """
    Fetches the patient's profile and ALL their past consultations.
    Returns a unified dictionary to the frontend.
    """
    print(f"Fetching full history for: {document_id}")
    
    try:
        conexion = db.connect()
        # This tells SQLite to return dictionaries instead of plain tuples
        conexion.row_factory = sql.Row 
        cursor = conexion.cursor()
        
        # Fetch the patient profile (Portada)
        cursor.execute("SELECT * FROM patients WHERE document_id = ?", (document_id,))
        patient_row = cursor.fetchone()
        
        if not patient_row:
            conexion.close()
            return {"status": "error", "msg": "Paciente no encontrado."}
            
        # Convert the sqlite3.Row to a standard Python dictionary
        patient_data = dict(patient_row)
        
        # Let's decode the JSON strings back into Python dictionaries 
        # so JS receives real objects, not stringified text.
        patient_data['personal_background'] = json.loads(patient_data['personal_background'] or '{}')
        patient_data['gynecological_background'] = json.loads(patient_data['gynecological_background'] or '{}')
        patient_data['family_background'] = json.loads(patient_data['family_background'] or '{}')
        
        # Fetch all consultations for this patient ordered by date (newest first)
        cursor.execute("SELECT * FROM queries WHERE patient_document_id = ? ORDER BY date DESC", (document_id,))
        queries_rows = cursor.fetchall()
        
        # Convert all query rows to a list of dictionaries
        consultations_list = []
        for row in queries_rows:
            consult_dict = dict(row)
            # Decode the physical examination JSON
            consult_dict['physical_examination'] = json.loads(consult_dict['physical_examination'] or '{}')
            consultations_list.append(consult_dict)
            
        conexion.close()
        
        # We package everything neatly for the frontend
        return {
            "status": "success",
            "patient": patient_data,
            "consultations": consultations_list
        }
        
    except Exception as e:
        return {"status": "fatal", "msg": f"Error en la base de datos buscando el paciente: {str(e)}"}
    
@eel.expose
def search_patients(search_term):
    """
    Searches for patients by document_id, names, or surnames.
    Returns a brief list of matches for the frontend search bar.
    """
    print(f"Searching for patient with term: {search_term}")
    
    # If the search bar is empty, return an empty list safely
    if not search_term or str(search_term).strip() == "":
        return {"status": "success", "results": []}
        
    try:
        conexion = db.connect()
        conexion.row_factory = sql.Row 
        cursor = conexion.cursor()
        
        # We add the "%" wildcards so it matches partial text
        # E.g., searching "Perez" matches "Juan Perez" or "Perez Gomez"
        wildcard_term = f"%{search_term}%"
        
        # We only fetch the essential data to make the search fast
        cursor.execute('''
            SELECT document_id, names, surnames, gender, birthdate 
            FROM patients 
            WHERE is_active = 1 AND (document_id LIKE ? OR names LIKE ? OR surnames LIKE ?)
            ORDER BY names ASC
            LIMIT 20
        ''', (wildcard_term, wildcard_term, wildcard_term))
        
        results_rows = cursor.fetchall()
        
        # Convert the rows to a list of dictionaries
        patients_list = [dict(row) for row in results_rows]
        
        conexion.close()
        
        return {
            "status": "success",
            "results": patients_list
        }
        
    except Exception as e:
        return {"status": "fatal", "msg": f"Server error during search: {str(e)}"}
    
@eel.expose
def archive_patient(document_id):
    """
    Performs a 'Soft Delete' on a patient. 
    It doesn't erase the data, just marks it as inactive (archived) for legal compliance.
    """
    print(f"Archiving (Soft Deleting) patient: {document_id}")
    
    try:
        conexion = db.connect()
        cursor = conexion.cursor()
        
        # We UPDATE instead of DELETE. 
        cursor.execute('''
            UPDATE patients 
            SET is_active = 0 
            WHERE document_id = ?
        ''', (document_id,))
        
        # We verify if a row was actually changed
        if cursor.rowcount == 0:
            conexion.close()
            return {"status": "error", "msg": "Patient not found."}
            
        conexion.commit()
        conexion.close()
        
        return {
            "status": "success", 
            "msg": "Patient successfully archived. Their medical history is preserved but hidden."
        }
        
    except Exception as e:
        return {"status": "fatal", "msg": f"Server error archiving patient: {str(e)}"}
# eel.start('index.html', size=(1024, 768))