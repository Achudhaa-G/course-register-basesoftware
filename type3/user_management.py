from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget
import sqlite3

class UserManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manage Users")
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()

        self.user_list = QListWidget()
        layout.addWidget(QLabel("Registered Users:"))
        layout.addWidget(self.user_list)

        self.load_users()
        self.setLayout(layout)

    def load_users(self):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT username, role FROM users")
        users = cursor.fetchall()
        conn.close()

        for user in users:
            self.user_list.addItem(f"{user[0]} ({user[1]})")
