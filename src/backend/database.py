import sqlite3 as sql
import json

def connect ():
    # This function allows the access to the db
    return sql.connect("medic_system.db")

def create_tables ():

    conexion = connect()
    cursor = conexion.cursor()

    # Medic table (for the local login)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            user TEXT UNIQUE NOT NULL, 
            password TEXT NOT NULL    
        )         
    ''')
    
    # Patients table (Here we store all the essential information about the patient )
    # Here is the information base of the patient
    # The relation between doctor and patient  is 1 to N
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
                   
            -- Personal information
            document_id TEXT PRIMARY KEY,
            names TEXT NOT NULL,
            surnames TEXT NOT NULL, 
            gender TEXT CHECK (
                gender IN ("male", "female")
            ),
            birthdate TEXT NOT NULL,
            emergency_contact_name TEXT,
            emergency_contact_phone TEXT,
            blood_type TEXT CHECK (
                blood_type IN ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-')
            ),
            occupation TEXT NOT NULL,
            marital_status TEXT NOT NULL,         

            -- Medical interview
                   
                -- personal background.
                      
                -- Stores: Chronic diseases, surgeries, allergies, vaccines, habits, and medications.
                -- How is it passed?: From the API (Python), you retrieve a dictionary and use `json.dumps(dictionary)`.
                -- How is it stored?: It is saved as a single line of plain text (String).
                -- Example of 1-line formatting:
                -- '{"chronic_diseases": "None", "surgeries": "Appendectomy 2015", "allergies": {"drugs": "Penicillin", "food": "None"}, "vaccines": "COVID-19, Tetanus", "toxic_habits": {"tobacco": "No", "alcohol": "Social"}, "daily_medication": "None", "physiological_habits": {"dream":" 6 hours", } }
                   
            personal_background TEXT,

                -- family history.
                   
                -- Stores: Hereditary or risk diseases (diabetes, hypertension).
                -- How is it passed?: The same way, you use json.dumps(python_dictionary).
                -- How is it stored?: As plain text.
                -- Example of a 1-line format:
                -- '{"diabetes": "Father", "hypertension": "Paternal grandfather", "cancer": "None", "others": "None"}'
                
            family_background TEXT
                            
        )
    ''')

    # Queries Tables (Here we store the subsequent queries associated to the medical history of one patient)
    # The relation between patient and quieres is 1 to N

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS queries (
           id INTEGER PRIMARY KEY AUTOINCREMENT, -- inquiry number
           patient_document_id TEXT NOT NULL,
           date TEXT NOT NULL,
           motive TEXT NOT NULL, 
           current_illness TEXT NOT NULL,  

           -- Vital Signs & Anthropometry 
           weight REAL,              
           height REAL,              
           bmi REAL,                 
           blood_pressure TEXT,      
           heart_rate INTEGER,       
           respiratory_rate INTEGER, 
           temperature REAL,         

           -- Qualitative Physical Examination (Examen Físico Descriptivo)
           -- Almacena en JSON: impresion_general, constitucion, facies, actitud, decubito, 
           -- marcha, piel, cabeza, cuello, respiratorio, cardiovascular, abdomen, neurologico.
           -- Ejemplo: '{"general_impression": "Paciente estable", "head": "Normocéfalo", "abdomen": "Blando, depresible"}'
           physical_examination TEXT,

           diagnostic TEXT NOT NULL,
           treatment TEXT,

           -- The bridge between patient and his queries 
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

    # Attached exams to the consult 
    # The relation between  and quieres is 1 to N
    # We save the changes and close the conexion
    conexion.commit()
    conexion.close()

# This allows execute the function "create_tables()" if the main is executed
if __name__ == "__main__":
    create_tables()


    
