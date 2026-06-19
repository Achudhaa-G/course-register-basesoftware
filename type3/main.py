import sys
from PyQt6.QtWidgets import QApplication
from login_window import LoginWindow

def load_stylesheet():
    with open("styles.qss", "r") as file:
        return file.read()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet())  # Apply QSS styling
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
