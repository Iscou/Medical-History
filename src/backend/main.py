import threading
import uvicorn
import webview
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import api # Importas tu archivo limpio con las funciones de SQLite
import os
import sys # NEW
import ctypes
import database 
import multiprocessing # NEW: Critical for PyInstaller + Uvicorn on Windows

# --- WINDOWS TASKBAR FIX ---
# This tells Windows that this is a unique application, 
# so it doesn't group it with the generic Python icon.
try:
    myappid = 'mycompany.myproduct.subproduct.version' 
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception as e:
    print(f"Taskbar icon fix failed: {e}")

app = FastAPI()

# --- Security ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models ---
class LoginData(BaseModel):
    email: str
    password: str

class RegisterData(BaseModel):
    name: str
    email: str
    password: str

# --- ENDPOINTS (API) ---
app.include_router(api.api_router)

# --- DYNAMIC PATHS (PYINSTALLER COMPATIBLE) ---
# NEW: PyInstaller creates a temp folder and stores path in _MEIPASS
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    BUNDLE_DIR = sys._MEIPASS
    FRONTEND_DIR = os.path.join(BUNDLE_DIR, "frontend")
else:
    # Running as script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    FRONTEND_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "frontend"))

# --- FrontEnd ---
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


# --- STARTUP ENGINE (DESKTOP) ---
def start_server():
    """Runs FastAPI in a background thread without blocking the program"""
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")

if __name__ == "__main__":
    # NEW: Required by Windows when combining PyInstaller with Multiprocessing/Uvicorn
    multiprocessing.freeze_support() 
    
    # Ensure the database and tables exist before anything else
    try:
        database.create_tables()
    except Exception as e:
        print(f"Critical Error: Could not initialize database: {e}")
        exit(1) # Stop the program if the DB is not ready

    # Start the backend thread (FastAPI)
    api_thread = threading.Thread(target=start_server, daemon=True)
    api_thread.start()

    # Set up the absolute path for the window icon
    ICON_PATH = os.path.join(FRONTEND_DIR, "images", "icon.ico")

    # Create and show the native desktop window
    webview.create_window(
        title="MediHistorial - Clinical System", 
        url="http://127.0.0.1:8000",
        width=1024, 
        height=768,
        resizable=True 
    )
    
    # Start the GUI loop
    webview.start(icon=ICON_PATH)