# MediHistorial 

MediHistorial is a lightweight, secure, and offline-first desktop application designed for clinical management. It streamlines the creation and tracking of electronic medical records, evolutionary queries, and patient histories without relying on external cloud databases, ensuring maximum privacy for medical data.

Developed by **Francisco Zerpa**.

##  Features

* **Secure Authentication:** Doctor registration and login system secured with bcrypt password hashing and an OTP (One-Time Password) email verification flow.
* **Patient Management:** Create, search, and manage comprehensive patient profiles, including personal data, medical background, and habits.
* **Clinical Histories & Evolutionary Queries:** Track patient progress over time with chronological evolutionary queries.
* **File Management:** Attach auxiliary exams (PDFs, JPGs, PNGs) directly to a patient's specific consultation.
* **Printable Records:** Automatically generate clean, printable medical reports directly from the interface.
* **Offline Execution:** Runs entirely locally using SQLite, compiled as a standalone Windows executable.

##  Tech Stack

* **Backend:** Python, FastAPI, Uvicorn, SQLite3.
* **Frontend:** HTML5, CSS3, Vanilla JavaScript.
* **Desktop Wrapper:** Pywebview.
* **Security:** Bcrypt, Python-dotenv.
* **Compilation:** PyInstaller.

##  Project Structure

```text
medical_history/
├── src/
│   ├── backend/
│   │   ├── api_routes.py    # API endpoints and core logic
│   │   ├── database.py      # SQLite connection and schema
│   │   ├── main.py          # Entry point and Pywebview setup
│   │   ├── security.py      # Password hashing functions
│   │   └── test_data.py     # Database seeding script
│   └── frontend/
│       ├── css/
│       ├── images/
│       ├── js/
│       └── index.html       # Main UI 
├── uploads/                 # Local storage for patient exams
├── .env                     # Environment variables (Ignored in Git)
├── .gitignore
├── requirements.txt         # Project dependencies
└── README.md
```

##  Development Setup

### Prerequisites
* Python 3.8+ installed on your system.

### 1. Clone the repository
```bash
git clone [https://github.com/yourusername/medical_history.git](https://github.com/yourusername/medical_history.git)
cd medical_history
```

### 2. Create and activate a virtual environment
Windows (PowerShell):

```PowerShell
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install dependencies

```PowerShell
pip install -r requirements.txt
```

### 4. Environment Variables

Create a .env file in the root directory and add your SMTP credentials for the OTP email system:

```PowerShell
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_16_char_app_password
```

### 5. Initialize the Database (Optional Seeding)
To create the tables and populate the database with mock data for testing purposes:

```PowerShell
python src/backend/test_data.py
```

### 6. Run the application

```PowerShell
python src/backend/main.py
```

##  Building the Executable
To compile the application into a standalone Windows executable (.exe) that includes all web assets and the hidden .env file, ensure your virtual environment is active and run:

```PowerShell
python -m PyInstaller --onedir --windowed --icon="src/frontend/images/icon.ico" --add-data "src/frontend;frontend" --add-data "uploads;uploads" --add-data ".env;." --paths src/backend src/backend/main.py --name MediHistorial
```

The compiled application will be available in the dist/MediHistorial folder.