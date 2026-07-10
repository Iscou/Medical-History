import threading
import uvicorn
import webview
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import api_routes # Import the custom routing and SQLite logic
import os
import sys 
import ctypes
import database 
import multiprocessing 

# --- WINDOWS TASKBAR FIX ---
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
app.include_router(api_routes.api_router)

# --- DYNAMIC PATHS (PYINSTALLER COMPATIBLE) ---
if getattr(sys, 'frozen', False):
    BUNDLE_DIR = sys._MEIPASS
    FRONTEND_DIR = os.path.join(BUNDLE_DIR, "frontend")
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    FRONTEND_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "frontend"))

# --- FrontEnd ---
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


# --- STARTUP ENGINE (DESKTOP) ---
def start_server():
    """Runs FastAPI in a background thread without blocking the program"""
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")

if __name__ == "__main__":
    multiprocessing.freeze_support() 
    
    try:
        database.create_tables()
    except Exception as e:
        print(f"Critical Error: Could not initialize database: {e}")
        exit(1) 

    api_thread = threading.Thread(target=start_server, daemon=True)
    api_thread.start()

    ICON_PATH = os.path.join(FRONTEND_DIR, "images", "icon.ico")

    webview.create_window(
        title="MediHistorial - Clinical System", 
        url="http://127.0.0.1:8000",
        width=1024, 
        height=768,
        resizable=True 
    )
    
    # Start the GUI loop (private_mode=False forces localstorage persistence)
    webview.start(icon=ICON_PATH, private_mode=False)