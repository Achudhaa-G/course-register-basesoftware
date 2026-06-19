import sqlite3

def connect_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    # Create Users Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT,
                        role TEXT)''')
    
    # Create Courses Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS courses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE,
                        instructor TEXT)''')

    conn.commit()
    conn.close()

def add_user(username, password, role):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
    conn.commit()
    conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user
def enroll_course(student_id, course_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    # Check if already enrolled
    cursor.execute("SELECT * FROM enrollments WHERE student_id = ? AND course_id = ?", (student_id, course_id))
    if cursor.fetchone():
        conn.close()
        return False  # Already enrolled

    # Enroll the student
    cursor.execute("INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)", (student_id, course_id))
    conn.commit()
    conn.close()
    return True
