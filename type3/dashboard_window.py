from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from course_management import CourseManagement
from user_management import UserManagement
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from enrollment_window import EnrollmentWindow


class DashboardWindow(QWidget):
    def __init__(self, username, role):
        super().__init__()
        self.setWindowTitle("Dashboard")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Welcome, {username}"))
        layout.addWidget(QLabel(f"Role: {role}"))

        if role == "admin":
            self.manage_users_button = QPushButton("Manage Users")
            self.manage_users_button.clicked.connect(self.open_user_management)
            layout.addWidget(self.manage_users_button)

        if role in ["admin", "staff"]:
            self.manage_courses_button = QPushButton("Manage Courses")
            self.manage_courses_button.clicked.connect(self.open_course_management)
            layout.addWidget(self.manage_courses_button)

        if role == "student":
            self.enroll_button = QPushButton("Enroll in Courses")
            self.enroll_button.clicked.connect(self.open_enrollment)
            layout.addWidget(self.enroll_button)

        self.setLayout(layout)

    def open_enrollment(self):
        self.enroll_window = EnrollmentWindow(self.user_id)
        self.enroll_window.show()

        self.setLayout(layout)

    def open_course_management(self):
        self.course_window = CourseManagement()
        self.course_window.show()

    def open_user_management(self):
        self.user_window = UserManagement()
        self.user_window.show()
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Welcome, {username}"))
        layout.addWidget(QLabel(f"Role: {role}"))

        