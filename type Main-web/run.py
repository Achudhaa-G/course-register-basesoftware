import subprocess
import webbrowser
import time
import os

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
FRONTEND_FILE = os.path.join(BASE_DIR, "frontend", "index.html")

# Start Flask backend
backend_process = subprocess.Popen(["python", os.path.join(BACKEND_DIR, "app.py")])

# Wait for backend to start
time.sleep(3)

# Open frontend in browser
webbrowser.open("file://" + FRONTEND_FILE)

try:
    backend_process.wait()
except KeyboardInterrupt:
    backend_process.terminate()
