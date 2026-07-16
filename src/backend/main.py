import threading
import uvicorn
import webview
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import api_routes 
import os
import sys 
import ctypes
import database 
import multiprocessing 

try:
    myappid = 'com.franciscozerpa.medihistorial.1.0' 
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception as e:
    pass

app = FastAPI()

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

app.include_router(api_routes.api_router)

if getattr(sys, 'frozen', False):
    BUNDLE_DIR = sys._MEIPASS
    FRONTEND_DIR = os.path.join(BUNDLE_DIR, "frontend")
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    FRONTEND_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "frontend"))

app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

def start_server():
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")

# --- CUSTOM WINDOW CONTROLS API ---
class WindowAPI:
    def __init__(self):
        self.window = None

    def set_window(self, window):
        self.window = window

    def minimize(self):
        if self.window: self.window.minimize()

    def toggle_maximize(self):
        if self.window:
            if self.window.fullscreen:
                self.window.restore()
            else:
                self.window.toggle_fullscreen()

    def close(self):
        if self.window: self.window.destroy()

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
    
    # Initialize JS to Python API
    window_api = WindowAPI()

    window = webview.create_window(
        title="MediHistorial", 
        url="http://127.0.0.1:8000",
        width=1200, 
        height=800,
        resizable=True,
        frameless=True, # THIS REMOVES THE WINDOWS BORDER
        js_api=window_api
    )
    
    window_api.set_window(window)
    webview.start(icon=ICON_PATH, private_mode=False)