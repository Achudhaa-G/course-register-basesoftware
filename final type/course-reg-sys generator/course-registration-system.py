import os
import zipfile

project_root = "course-registration-system"
zip_filename = "course-registration-system.zip"

# Project file structure and contents
file_structure = {
    "backend": {
        "run.py": '''from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
''',
        "app/__init__.py": '''from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///courses.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
''',
        "app/routes.py": '''from flask import Blueprint, jsonify

main = Blueprint('main', __name__)

@main.route("/courses")
def get_courses():
    return jsonify({"courses": ["Math", "Science", "History"]})
'''
    },
    "frontend": {
        "package.json": '''{
  "name": "frontend",
  "version": "0.0.1",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.3.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.0.0"
  }
}''',
        "vite.config.js": '''import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/courses': 'http://localhost:5000',
      '/auth': 'http://localhost:5000',
      '/admin': 'http://localhost:5000'
    }
  }
})''',
        "index.html": '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Course Registration</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>''',
        "src/main.jsx": '''import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import App from "./App";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <Router>
      <App />
    </Router>
  </React.StrictMode>
);''',
        "src/App.jsx": '''import React from "react";

function App() {
  return (
    <div>
      <h1>Course Registration System</h1>
    </div>
  );
}

export default App;''',
        "src/index.css": '''body {
  margin: 0;
  font-family: sans-serif;
  background: #f5f5f5;
}'''
    },
    "run.py": '''import subprocess
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
'''
    }


# Function to create directories and write files
def create_project(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_project(path, content)
        else:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

# Create the project directory
os.makedirs(project_root, exist_ok=True)
create_project(project_root, file_structure)

# Create ZIP archive
with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
    for root, _, files in os.walk(project_root):
        for file in files:
            filepath = os.path.join(root, file)
            arcname = os.path.relpath(filepath, os.path.dirname(project_root))
            zipf.write(filepath, arcname)

print(f" Project generated and zipped as: {zip_filename}")
