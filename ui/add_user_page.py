# ui/add_user_page.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout,
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt
from logic.user_operations import add_user, get_all_users, update_user, delete_user

class AddUserPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("User Management")
        self.resize(500, 350)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # Title
        title = QLabel("Manage Users")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:18px; font-weight:bold;")
        layout.addWidget(title)

        # Table
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Username", "Role", "Password"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self.load_user_to_form)
        layout.addWidget(self.table)

        # Input form
        form = QHBoxLayout()
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)  # <-- Hide password input!
        self.role_input = QLineEdit()
        self.role_input.setPlaceholderText("admin or staff")
        form.addWidget(self.username_input)
        form.addWidget(self.password_input)
        form.addWidget(self.role_input)
        layout.addLayout(form)

        # Buttons
        btns = QHBoxLayout()
        self.add_btn = QPushButton("Add")
        self.update_btn = QPushButton("Update")
        self.delete_btn = QPushButton("Delete")
        btns.addWidget(self.add_btn)
        btns.addWidget(self.update_btn)
        btns.addWidget(self.delete_btn)
        layout.addLayout(btns)

        self.add_btn.clicked.connect(self.handle_add)
        self.update_btn.clicked.connect(self.handle_update)
        self.delete_btn.clicked.connect(self.handle_delete)

        self.load_users()

    def load_users(self):
        self.table.setRowCount(0)
        for user, pwd, role in get_all_users():
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(user))
            self.table.setItem(row, 1, QTableWidgetItem(role))
            self.table.setItem(row, 2, QTableWidgetItem("*****"))  # Always show stars instead of real password

    def load_user_to_form(self):
        items = self.table.selectedItems()
        if items:
            self.username_input.setText(items[0].text())
            self.role_input.setText(items[1].text())
            # Don't autofill the password (for privacy); clear instead:
            self.password_input.clear()

    def handle_add(self):
        u = self.username_input.text().strip()
        p = self.password_input.text().strip()
        r = self.role_input.text().strip()
        if not (u and p and r in ("admin", "staff")):
            QMessageBox.warning(self, "Invalid Input", "Fill all fields (role must be admin or staff).")
            return
        ok = add_user(u, p, r)
        if ok:
            QMessageBox.information(self, "Added", "User created.")
            self.load_users()
            self.clear_inputs()
        else:
            QMessageBox.warning(self, "Duplicate", "User already exists.")

    def handle_update(self):
        u = self.username_input.text().strip()
        p = self.password_input.text().strip()
        r = self.role_input.text().strip()
        if not (u and p and r in ("admin", "staff")):
            QMessageBox.warning(self, "Invalid Input", "Fill all fields (role must be admin or staff).")
            return
        update_user(u, p, r)
        QMessageBox.information(self, "Updated", "User updated.")
        self.load_users()
        self.clear_inputs()

    def handle_delete(self):
        u = self.username_input.text().strip()
        if not u:
            return
        delete_user(u)
        QMessageBox.information(self, "Deleted", "User deleted.")
        self.load_users()
        self.clear_inputs()

    def clear_inputs(self):
        self.username_input.clear()
        self.password_input.clear()
        self.role_input.clear()
