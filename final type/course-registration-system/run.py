import subprocess
import os
import threading
import time
import webbrowser

BACKEND_PATH = os.path.join(os.getcwd(), "backend")
FRONTEND_PATH = os.path.join(os.getcwd(), "frontend")

def run_backend():
    subprocess.run(["python", "run.py"], cwd=BACKEND_PATH)

def run_frontend():
    subprocess.run(["npm", "run", "dev"], cwd=FRONTEND_PATH, shell=True)

if __name__ == "__main__":
    threading.Thread(target=run_backend).start()
    time.sleep(2)
    threading.Thread(target=run_frontend).start()
    time.sleep(3)
    webbrowser.open("http://localhost:5173")
