from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
import sqlite3

class CourseManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manage Courses")
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()
        
        self.course_name_input = QLineEdit()
        self.course_name_input.setPlaceholderText("Course Name")
        layout.addWidget(QLabel("Course Name:"))
        layout.addWidget(self.course_name_input)

        self.instructor_input = QLineEdit()
        self.instructor_input.setPlaceholderText("Instructor")
        layout.addWidget(QLabel("Instructor:"))
        layout.addWidget(self.instructor_input)

        self.add_course_button = QPushButton("Add Course")
        self.add_course_button.clicked.connect(self.add_course)
        layout.addWidget(self.add_course_button)

        self.setLayout(layout)

    def add_course(self):
        course_name = self.course_name_input.text()
        instructor = self.instructor_input.text()

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO courses (name, instructor) VALUES (?, ?)", (course_name, instructor))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Success", "Course added successfully!")
