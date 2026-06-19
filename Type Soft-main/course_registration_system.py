import sys
import sqlite3
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
                             QMessageBox, QTabWidget, QComboBox, QDialog, QFormLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect('university.db')
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Students table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            major TEXT,
            year INTEGER
        )
        ''')
        
        # Courses table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            course_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            department TEXT NOT NULL,
            credits INTEGER NOT NULL,
            professor TEXT,
            schedule TEXT,
            capacity INTEGER NOT NULL,
            enrolled INTEGER DEFAULT 0,
            prerequisites TEXT
        )
        ''')
        
        # Registrations table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS registrations (
            registration_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            course_id TEXT NOT NULL,
            semester TEXT NOT NULL,
            registration_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (student_id),
            FOREIGN KEY (course_id) REFERENCES courses (course_id),
            UNIQUE (student_id, course_id, semester)
        )
        ''')
        
        # Admin table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            admin_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        ''')
        
        self.conn.commit()
        
        # Insert sample data if tables are empty
        self.insert_sample_data()

    def insert_sample_data(self):
        cursor = self.conn.cursor()
        
        # Check if students table is empty
        cursor.execute("SELECT COUNT(*) FROM students")
        if cursor.fetchone()[0] == 0:
            # Insert sample students
            students = [
                ('S1001', 'John Doe', 'john@university.edu', 'password123', 'Computer Science', 3),
                ('S1002', 'Jane Smith', 'jane@university.edu', 'password123', 'Mathematics', 2),
                ('S1003', 'Bob Johnson', 'bob@university.edu', 'password123', 'Physics', 4)
            ]
            cursor.executemany("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?)", students)
        
        # Check if courses table is empty
        cursor.execute("SELECT COUNT(*) FROM courses")
        if cursor.fetchone()[0] == 0:
            # Insert sample courses
            courses = [
                ('CS101', 'Introduction to Programming', 'Computer Science', 3, 'Dr. Smith', 'MWF 10:00-10:50', 30, 0, 'None'),
                ('CS201', 'Data Structures', 'Computer Science', 4, 'Dr. Johnson', 'TTH 11:00-12:15', 25, 0, 'CS101'),
                ('MATH101', 'Calculus I', 'Mathematics', 4, 'Dr. Lee', 'MWF 9:00-9:50', 35, 0, 'None'),
                ('PHYS101', 'General Physics', 'Physics', 4, 'Dr. Brown', 'TTH 1:00-2:15', 30, 0, 'None'),
                ('CS301', 'Algorithms', 'Computer Science', 4, 'Dr. Smith', 'MWF 11:00-11:50', 20, 0, 'CS201')
            ]
            cursor.executemany("INSERT INTO courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", courses)
        
        # Check if admin table is empty
        cursor.execute("SELECT COUNT(*) FROM admin")
        if cursor.fetchone()[0] == 0:
            # Insert sample admin
            cursor.execute("INSERT INTO admin VALUES ('A1001', 'Admin User', 'admin@university.edu', 'admin123')")
        
        self.conn.commit()

    def authenticate_student(self, email, password):
        cursor = self.conn.cursor()
        cursor.execute("SELECT student_id, name FROM students WHERE email=? AND password=?", (email, password))
        return cursor.fetchone()

    def authenticate_admin(self, email, password):
        cursor = self.conn.cursor()
        cursor.execute("SELECT admin_id, name FROM admin WHERE email=? AND password=?", (email, password))
        return cursor.fetchone()

    def get_student_info(self, student_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM students WHERE student_id=?", (student_id,))
        return cursor.fetchone()

    def get_all_courses(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM courses")
        return cursor.fetchall()

    def get_available_courses(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM courses WHERE enrolled < capacity")
        return cursor.fetchall()

    def get_student_courses(self, student_id, semester):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT c.course_id, c.title, c.credits, c.professor, c.schedule 
        FROM registrations r
        JOIN courses c ON r.course_id = c.course_id
        WHERE r.student_id=? AND r.semester=?
        ''', (student_id, semester))
        return cursor.fetchall()

    def register_course(self, student_id, course_id, semester):
        try:
            cursor = self.conn.cursor()
            
            # Check if course exists and has capacity
            cursor.execute("SELECT capacity, enrolled FROM courses WHERE course_id=?", (course_id,))
            result = cursor.fetchone()
            if not result:
                return False, "Course not found"
            
            capacity, enrolled = result
            if enrolled >= capacity:
                return False, "Course is full"
            
            # Check if student is already registered
            cursor.execute("SELECT 1 FROM registrations WHERE student_id=? AND course_id=? AND semester=?", 
                          (student_id, course_id, semester))
            if cursor.fetchone():
                return False, "Already registered for this course"
            
            # Check prerequisites
            cursor.execute("SELECT prerequisites FROM courses WHERE course_id=?", (course_id,))
            prereqs = cursor.fetchone()[0]
            if prereqs and prereqs != 'None':
                prereq_list = [p.strip() for p in prereqs.split(',')]
                for prereq in prereq_list:
                    cursor.execute('''
                    SELECT 1 FROM registrations 
                    WHERE student_id=? AND course_id=? AND semester < ?
                    ''', (student_id, prereq, semester))
                    if not cursor.fetchone():
                        return False, f"Prerequisite {prereq} not satisfied"
            
            # Register the course
            cursor.execute("INSERT INTO registrations (student_id, course_id, semester) VALUES (?, ?, ?)", 
                          (student_id, course_id, semester))
            cursor.execute("UPDATE courses SET enrolled = enrolled + 1 WHERE course_id=?", (course_id,))
            self.conn.commit()
            return True, "Registration successful"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, str(e)

    def drop_course(self, student_id, course_id, semester):
        try:
            cursor = self.conn.cursor()
            
            # Check if registration exists
            cursor.execute("SELECT 1 FROM registrations WHERE student_id=? AND course_id=? AND semester=?", 
                          (student_id, course_id, semester))
            if not cursor.fetchone():
                return False, "Registration not found"
            
            # Drop the course
            cursor.execute("DELETE FROM registrations WHERE student_id=? AND course_id=? AND semester=?", 
                          (student_id, course_id, semester))
            cursor.execute("UPDATE courses SET enrolled = enrolled - 1 WHERE course_id=?", (course_id,))
            self.conn.commit()
            return True, "Course dropped successfully"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, str(e)

    def add_student(self, student_id, name, email, password, major, year):
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?)", 
                          (student_id, name, email, password, major, year))
            self.conn.commit()
            return True, "Student added successfully"
        except sqlite3.IntegrityError:
            return False, "Student ID or email already exists"
        except sqlite3.Error as e:
            return False, str(e)

    def add_course(self, course_id, title, department, credits, professor, schedule, capacity, prerequisites):
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                          (course_id, title, department, credits, professor, schedule, capacity, 0, prerequisites))
            self.conn.commit()
            return True, "Course added successfully"
        except sqlite3.IntegrityError:
            return False, "Course ID already exists"
        except sqlite3.Error as e:
            return False, str(e)

    def get_all_students(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT student_id, name, email, major, year FROM students")
        return cursor.fetchall()

    def close(self):
        self.conn.close()

class LoginWindow(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setWindowTitle("University Course Registration - Login")
        self.setGeometry(100, 100, 400, 300)
        
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Title
        title = QLabel("University Course Registration")
        title.setFont(QFont('Arial', 16))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Login Form
        form_layout = QFormLayout()
        
        self.role_combo = QComboBox()
        self.role_combo.addItems(["Student", "Administrator"])
        form_layout.addRow("Role:", self.role_combo)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email")
        form_layout.addRow("Email:", self.email_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Password:", self.password_input)
        
        layout.addLayout(form_layout)
        
        # Login Button
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.attempt_login)
        layout.addWidget(login_btn)
        
        # Register Button (for students)
        register_btn = QPushButton("Register as New Student")
        register_btn.clicked.connect(self.show_registration)
        layout.addWidget(register_btn)
        
    def attempt_login(self):
        email = self.email_input.text()
        password = self.password_input.text()
        role = self.role_combo.currentText()
        
        if not email or not password:
            QMessageBox.warning(self, "Error", "Please enter both email and password")
            return
        
        if role == "Student":
            result = self.db_manager.authenticate_student(email, password)
            if result:
                student_id, name = result
                self.open_student_dashboard(student_id)
            else:
                QMessageBox.warning(self, "Error", "Invalid student credentials")
        else:  # Administrator
            result = self.db_manager.authenticate_admin(email, password)
            if result:
                admin_id, name = result
                self.open_admin_dashboard()
            else:
                QMessageBox.warning(self, "Error", "Invalid admin credentials")
    
    def show_registration(self):
        self.registration_dialog = StudentRegistrationDialog(self.db_manager)
        self.registration_dialog.exec_()
    
    def open_student_dashboard(self, student_id):
        self.student_dashboard = StudentDashboard(self.db_manager, student_id)
        self.student_dashboard.show()
        self.close()
    
    def open_admin_dashboard(self):
        self.admin_dashboard = AdminDashboard(self.db_manager)
        self.admin_dashboard.show()
        self.close()

class StudentRegistrationDialog(QDialog):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setWindowTitle("Student Registration")
        self.setGeometry(150, 150, 400, 400)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QFormLayout()
        self.setLayout(layout)
        
        self.student_id_input = QLineEdit()
        self.student_id_input.setPlaceholderText("e.g., S1004")
        layout.addRow("Student ID:", self.student_id_input)
        
        self.name_input = QLineEdit()
        layout.addRow("Full Name:", self.name_input)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("university email")
        layout.addRow("Email:", self.email_input)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addRow("Password:", self.password_input)
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        layout.addRow("Confirm Password:", self.confirm_password_input)
        
        self.major_input = QLineEdit()
        layout.addRow("Major:", self.major_input)
        
        self.year_input = QLineEdit()
        self.year_input.setPlaceholderText("e.g., 1 for Freshman")
        layout.addRow("Year:", self.year_input)
        
        register_btn = QPushButton("Register")
        register_btn.clicked.connect(self.register_student)
        layout.addRow(register_btn)
    
    def register_student(self):
        student_id = self.student_id_input.text()
        name = self.name_input.text()
        email = self.email_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        major = self.major_input.text()
        year = self.year_input.text()
        
        if not all([student_id, name, email, password, confirm_password, major, year]):
            QMessageBox.warning(self, "Error", "All fields are required")
            return
        
        if password != confirm_password:
            QMessageBox.warning(self, "Error", "Passwords do not match")
            return
        
        try:
            year = int(year)
        except ValueError:
            QMessageBox.warning(self, "Error", "Year must be a number")
            return
        
        success, message = self.db_manager.add_student(student_id, name, email, password, major, year)
        if success:
            QMessageBox.information(self, "Success", "Registration successful! You can now login.")
            self.close()
        else:
            QMessageBox.warning(self, "Error", message)

class StudentDashboard(QMainWindow):
    def __init__(self, db_manager, student_id):
        super().__init__()
        self.db_manager = db_manager
        self.student_id = student_id
        self.setWindowTitle("Student Dashboard")
        self.setGeometry(100, 100, 800, 600)
        
        self.init_ui()
        self.load_student_info()
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        self.layout = QVBoxLayout()
        central_widget.setLayout(self.layout)
        
        # Student info section
        self.student_info_label = QLabel()
        self.student_info_label.setFont(QFont('Arial', 12))
        self.layout.addWidget(self.student_info_label)
        
        # Tabs
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        # Course Registration Tab
        self.registration_tab = QWidget()
        self.tabs.addTab(self.registration_tab, "Course Registration")
        self.init_registration_tab()
        
        # My Courses Tab
        self.my_courses_tab = QWidget()
        self.tabs.addTab(self.my_courses_tab, "My Courses")
        self.init_my_courses_tab()
        
        # Logout button
        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.logout)
        self.layout.addWidget(logout_btn)
    
    def init_registration_tab(self):
        layout = QVBoxLayout()
        self.registration_tab.setLayout(layout)
        
        # Semester selection
        semester_layout = QHBoxLayout()
        semester_layout.addWidget(QLabel("Semester:"))
        
        self.semester_combo = QComboBox()
        self.semester_combo.addItems(["Fall 2023", "Spring 2024", "Summer 2024"])
        semester_layout.addWidget(self.semester_combo)
        
        refresh_btn = QPushButton("Refresh Courses")
        refresh_btn.clicked.connect(self.load_available_courses)
        semester_layout.addWidget(refresh_btn)
        
        layout.addLayout(semester_layout)
        
        # Available courses table
        self.available_courses_table = QTableWidget()
        self.available_courses_table.setColumnCount(7)
        self.available_courses_table.setHorizontalHeaderLabels(["Course ID", "Title", "Department", "Credits", "Professor", "Schedule", "Availability"])
        self.available_courses_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.available_courses_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.available_courses_table)
        
        # Register button
        register_btn = QPushButton("Register Selected Course")
        register_btn.clicked.connect(self.register_selected_course)
        layout.addWidget(register_btn)
        
        # Load initial data
        self.load_available_courses()
    
    def init_my_courses_tab(self):
        layout = QVBoxLayout()
        self.my_courses_tab.setLayout(layout)
        
        # Semester selection
        semester_layout = QHBoxLayout()
        semester_layout.addWidget(QLabel("Semester:"))
        
        self.my_courses_semester_combo = QComboBox()
        self.my_courses_semester_combo.addItems(["Fall 2023", "Spring 2024", "Summer 2024"])
        self.my_courses_semester_combo.currentTextChanged.connect(self.load_my_courses)
        semester_layout.addWidget(self.my_courses_semester_combo)
        
        layout.addLayout(semester_layout)
        
        # My courses table
        self.my_courses_table = QTableWidget()
        self.my_courses_table.setColumnCount(5)
        self.my_courses_table.setHorizontalHeaderLabels(["Course ID", "Title", "Credits", "Professor", "Schedule"])
        self.my_courses_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.my_courses_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.my_courses_table)
        
        # Drop button
        drop_btn = QPushButton("Drop Selected Course")
        drop_btn.clicked.connect(self.drop_selected_course)
        layout.addWidget(drop_btn)
        
        # Load initial data
        self.load_my_courses()
    
    def load_student_info(self):
        student_info = self.db_manager.get_student_info(self.student_id)
        if student_info:
            self.student_info_label.setText(
                f"Student ID: {student_info[0]} | Name: {student_info[1]} | "
                f"Email: {student_info[2]} | Major: {student_info[4]} | Year: {student_info[5]}"
            )
    
    def load_available_courses(self):
        courses = self.db_manager.get_available_courses()
        self.available_courses_table.setRowCount(len(courses))
        
        for row_idx, course in enumerate(courses):
            availability = f"{course[7]}/{course[6]}"  # enrolled/capacity
            for col_idx, item in enumerate([course[0], course[1], course[2], str(course[3]), course[4], course[5], availability]):
                self.available_courses_table.setItem(row_idx, col_idx, QTableWidgetItem(item))
    
    def load_my_courses(self):
        semester = self.my_courses_semester_combo.currentText()
        courses = self.db_manager.get_student_courses(self.student_id, semester)
        self.my_courses_table.setRowCount(len(courses))
        
        for row_idx, course in enumerate(courses):
            for col_idx, item in enumerate(course):
                self.my_courses_table.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))
    
    def register_selected_course(self):
        selected_row = self.available_courses_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Please select a course to register")
            return
        
        course_id = self.available_courses_table.item(selected_row, 0).text()
        semester = self.semester_combo.currentText()
        
        success, message = self.db_manager.register_course(self.student_id, course_id, semester)
        if success:
            QMessageBox.information(self, "Success", message)
            self.load_available_courses()
            self.load_my_courses()
        else:
            QMessageBox.warning(self, "Error", message)
    
    def drop_selected_course(self):
        selected_row = self.my_courses_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Please select a course to drop")
            return
        
        course_id = self.my_courses_table.item(selected_row, 0).text()
        semester = self.my_courses_semester_combo.currentText()
        
        success, message = self.db_manager.drop_course(self.student_id, course_id, semester)
        if success:
            QMessageBox.information(self, "Success", message)
            self.load_available_courses()
            self.load_my_courses()
        else:
            QMessageBox.warning(self, "Error", message)
    
    def logout(self):
        self.close()
        self.login_window = LoginWindow(self.db_manager)
        self.login_window.show()

class AdminDashboard(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setWindowTitle("Administrator Dashboard")
        self.setGeometry(100, 100, 900, 700)
        
        self.init_ui()
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        self.layout = QVBoxLayout()
        central_widget.setLayout(self.layout)
        
        # Title
        title = QLabel("Administrator Dashboard")
        title.setFont(QFont('Arial', 16))
        title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title)
        
        # Tabs
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        # Students Management Tab
        self.students_tab = QWidget()
        self.tabs.addTab(self.students_tab, "Students")
        self.init_students_tab()
        
        # Courses Management Tab
        self.courses_tab = QWidget()
        self.tabs.addTab(self.courses_tab, "Courses")
        self.init_courses_tab()
        
        # Logout button
        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.logout)
        self.layout.addWidget(logout_btn)
    
    def init_students_tab(self):
        layout = QVBoxLayout()
        self.students_tab.setLayout(layout)
        
        # Add student button
        add_student_btn = QPushButton("Add New Student")
        add_student_btn.clicked.connect(self.show_add_student_dialog)
        layout.addWidget(add_student_btn)
        
        # Students table
        self.students_table = QTableWidget()
        self.students_table.setColumnCount(5)
        self.students_table.setHorizontalHeaderLabels(["Student ID", "Name", "Email", "Major", "Year"])
        self.students_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.students_table)
        
        # Load data
        self.load_students()
    
    def init_courses_tab(self):
        layout = QVBoxLayout()
        self.courses_tab.setLayout(layout)
        
        # Add course button
        add_course_btn = QPushButton("Add New Course")
        add_course_btn.clicked.connect(self.show_add_course_dialog)
        layout.addWidget(add_course_btn)
        
        # Courses table
        self.courses_table = QTableWidget()
        self.courses_table.setColumnCount(9)
        self.courses_table.setHorizontalHeaderLabels(["Course ID", "Title", "Department", "Credits", "Professor", "Schedule", "Capacity", "Enrolled", "Prerequisites"])
        self.courses_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.courses_table)
        
        # Load data
        self.load_courses()
    
    def load_students(self):
        students = self.db_manager.get_all_students()
        self.students_table.setRowCount(len(students))
        
        for row_idx, student in enumerate(students):
            for col_idx, item in enumerate(student):
                self.students_table.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))
    
    def load_courses(self):
        courses = self.db_manager.get_all_courses()
        self.courses_table.setRowCount(len(courses))
        
        for row_idx, course in enumerate(courses):
            for col_idx, item in enumerate(course):
                self.courses_table.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))
    
    def show_add_student_dialog(self):
        dialog = AddStudentDialog(self.db_manager)
        if dialog.exec_() == QDialog.Accepted:
            self.load_students()
    
    def show_add_course_dialog(self):
        dialog = AddCourseDialog(self.db_manager)
        if dialog.exec_() == QDialog.Accepted:
            self.load_courses()
    
    def logout(self):
        self.close()
        self.login_window = LoginWindow(self.db_manager)
        self.login_window.show()

class AddStudentDialog(QDialog):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setWindowTitle("Add New Student")
        self.setGeometry(200, 200, 400, 300)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QFormLayout()
        self.setLayout(layout)
        
        self.student_id_input = QLineEdit()
        self.student_id_input.setPlaceholderText("e.g., S1004")
        layout.addRow("Student ID:", self.student_id_input)
        
        self.name_input = QLineEdit()
        layout.addRow("Full Name:", self.name_input)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("university email")
        layout.addRow("Email:", self.email_input)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addRow("Password:", self.password_input)
        
        self.major_input = QLineEdit()
        layout.addRow("Major:", self.major_input)
        
        self.year_input = QLineEdit()
        self.year_input.setPlaceholderText("e.g., 1 for Freshman")
        layout.addRow("Year:", self.year_input)
        
        buttons_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add Student")
        add_btn.clicked.connect(self.add_student)
        buttons_layout.addWidget(add_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addRow(buttons_layout)
    
    def add_student(self):
        student_id = self.student_id_input.text()
        name = self.name_input.text()
        email = self.email_input.text()
        password = self.password_input.text()
        major = self.major_input.text()
        year = self.year_input.text()
        
        if not all([student_id, name, email, password, major, year]):
            QMessageBox.warning(self, "Error", "All fields are required")
            return
        
        try:
            year = int(year)
        except ValueError:
            QMessageBox.warning(self, "Error", "Year must be a number")
            return
        
        success, message = self.db_manager.add_student(student_id, name, email, password, major, year)
        if success:
            QMessageBox.information(self, "Success", message)
            self.accept()
        else:
            QMessageBox.warning(self, "Error", message)

class AddCourseDialog(QDialog):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setWindowTitle("Add New Course")
        self.setGeometry(200, 200, 500, 400)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QFormLayout()
        self.setLayout(layout)
        
        self.course_id_input = QLineEdit()
        self.course_id_input.setPlaceholderText("e.g., CS101")
        layout.addRow("Course ID:", self.course_id_input)
        
        self.title_input = QLineEdit()
        layout.addRow("Title:", self.title_input)
        
        self.department_input = QLineEdit()
        layout.addRow("Department:", self.department_input)
        
        self.credits_input = QLineEdit()
        self.credits_input.setPlaceholderText("e.g., 3")
        layout.addRow("Credits:", self.credits_input)
        
        self.professor_input = QLineEdit()
        layout.addRow("Professor:", self.professor_input)
        
        self.schedule_input = QLineEdit()
        self.schedule_input.setPlaceholderText("e.g., MWF 10:00-10:50")
        layout.addRow("Schedule:", self.schedule_input)
        
        self.capacity_input = QLineEdit()
        self.capacity_input.setPlaceholderText("e.g., 30")
        layout.addRow("Capacity:", self.capacity_input)
        
        self.prerequisites_input = QLineEdit()
        self.prerequisites_input.setPlaceholderText("e.g., CS101,CS102 (or None)")
        layout.addRow("Prerequisites:", self.prerequisites_input)
        
        buttons_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add Course")
        add_btn.clicked.connect(self.add_course)
        buttons_layout.addWidget(add_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addRow(buttons_layout)
    
    def add_course(self):
        course_id = self.course_id_input.text()
        title = self.title_input.text()
        department = self.department_input.text()
        credits = self.credits_input.text()
        professor = self.professor_input.text()
        schedule = self.schedule_input.text()
        capacity = self.capacity_input.text()
        prerequisites = self.prerequisites_input.text() if self.prerequisites_input.text() else "None"
        
        if not all([course_id, title, department, credits, schedule, capacity]):
            QMessageBox.warning(self, "Error", "Required fields are missing")
            return
        
        try:
            credits = int(credits)
            capacity = int(capacity)
        except ValueError:
            QMessageBox.warning(self, "Error", "Credits and capacity must be numbers")
            return
        
        success, message = self.db_manager.add_course(
            course_id, title, department, credits, professor, 
            schedule, capacity, prerequisites
        )
        if success:
            QMessageBox.information(self, "Success", message)
            self.accept()
        else:
            QMessageBox.warning(self, "Error", message)

def main():
    app = QApplication(sys.argv)
    
    # Initialize database
    db_manager = DatabaseManager()
    
    # Show login window
    login_window = LoginWindow(db_manager)
    login_window.show()
    
    # Clean up on exit
    app.aboutToQuit.connect(db_manager.close)
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()