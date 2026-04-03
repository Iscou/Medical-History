import sqlite3 as sql

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
            document_id TEXT PRIMARY KEY,
            names TEXT NOT NULL,
            surnames TEXT NOT NULL, 
            gender TEXT CHECK (
                gender IN ("male", "female")
            ),
            birthdate TEXT NOT NULL,
            blood_type TEXT CHECK (
                blood_type IN ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-')
            ),
            reason_for_the_first_consultation TEXT NOT NULL,
            occupation TEXT NOT NULL,
            marital_status TEXT NOT NULL,              
                        
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
           diagnostic TEXT NOT NULL,
           treatment TEXT,

            -- The brigde between patient and his queries 
            FOREIGN KEY (patient_document_id) REFERENCES patients (document_id)                                    
        )
        '''
    )

    # We save the changes and close the conexion
    conexion.commit()
    conexion.close()

# This allows execute the function "create_tables()" if the main is executed
if __name__ == "__main__":
    create_tables()


    
