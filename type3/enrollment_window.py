from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QMessageBox
import sqlite3
from database import enroll_course

class EnrollmentWindow(QWidget):
    def __init__(self, student_id):
        super().__init__()
        self.setWindowTitle("Course Enrollment")
        self.setGeometry(100, 100, 400, 300)

        self.student_id = student_id
        layout = QVBoxLayout()

        self.course_list = QListWidget()
        layout.addWidget(QLabel("Available Courses:"))
        layout.addWidget(self.course_list)

        self.enroll_button = QPushButton("Enroll in Selected Course")
        self.enroll_button.clicked.connect(self.enroll_course)
        layout.addWidget(self.enroll_button)

        self.setLayout(layout)
        self.load_courses()

    def load_courses(self):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM courses")
        courses = cursor.fetchall()
        conn.close()

        for course in courses:
            self.course_list.addItem(f"{course[0]} - {course[1]}")

    def enroll_course(self):
        selected = self.course_list.currentItem()
        if selected:
            course_id = selected.text().split(" - ")[0]
            success = enroll_course(self.student_id, course_id)
            if success:
                QMessageBox.information(self, "Success", "You have been enrolled successfully!")
            else:
                QMessageBox.warning(self, "Error", "You are already enrolled in this course.")
        else:
            QMessageBox.warning(self, "Error", "Please select a course.")
