# ui/login_page.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFrame
)
from PySide6.QtCore import Signal, Qt
from logic.auth import validate_credentials

class LoginPage(QWidget):
    login_success = Signal(str)

    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f2f5;
                font-family: 'Segoe UI', sans-serif;
            }
            QFrame#card {
                background-color: white;
                border-radius: 12px;
                padding: 30px;
                max-width: 400px;
            }
            QLabel#title {
                font-size: 24px;
                font-weight: bold;
                color: #1877f2;
            }
            QLabel#error {
                color: #d93025;
                font-size: 13px;
            }
            QLineEdit {
                padding: 12px;
                font-size: 14px;
                border-radius: 8px;
                border: 1px solid #ccc;
            }
            QPushButton {
                background-color: #1877f2;
                color: white;
                font-size: 15px;
                padding: 10px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #165ecb;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)

        title = QLabel("Khaasha Inventory")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Login")
        self.status_label = QLabel("")
        self.status_label.setObjectName("error")
        self.status_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.status_label)

        main_layout.addWidget(card)

        self.login_button.clicked.connect(self.handle_login)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        role = validate_credentials(username, password)
        if role:
            self.login_success.emit(role)
        else:
            self.status_label.setText("❌ Invalid username or password")
