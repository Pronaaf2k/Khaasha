# ui/add_product_page.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout,
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Signal, Qt
from logic.product_operations import (
    add_product, get_all_products_full, update_product, delete_product
)

class AddProductPage(QWidget):
    product_added = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manage Products")
        self.resize(500, 350)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # Title
        title = QLabel("Product Management")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:18px; font-weight:bold;")
        layout.addWidget(title)

        # Table
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["ID", "Product Name"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self.load_product_to_form)
        layout.addWidget(self.table)

        # Input form
        form = QHBoxLayout()
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("ID (autofilled)")
        self.id_input.setReadOnly(True)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Product Name")
        form.addWidget(self.id_input)
        form.addWidget(self.name_input)
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

        self.load_products()

    def load_products(self):
        self.table.setRowCount(0)
        for prod_id, name in get_all_products_full():
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(prod_id)))
            self.table.setItem(row, 1, QTableWidgetItem(name))

    def load_product_to_form(self):
        items = self.table.selectedItems()
        if items:
            self.id_input.setText(items[0].text())
            self.name_input.setText(items[1].text())

    def handle_add(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Invalid Input", "Product name cannot be empty.")
            return
        ok = add_product(name)
        if ok:
            QMessageBox.information(self, "Added", "Product added.")
            self.load_products()
            self.product_added.emit()
        else:
            QMessageBox.warning(self, "Duplicate", "Product already exists.")

    def handle_update(self):
        pid = self.id_input.text().strip()
        name = self.name_input.text().strip()
        if not (pid and name):
            QMessageBox.warning(self, "Invalid Input", "Select a product and edit name.")
            return
        update_product(int(pid), name)
        QMessageBox.information(self, "Updated", "Product updated.")
        self.load_products()
        self.product_added.emit()

    def handle_delete(self):
        pid = self.id_input.text().strip()
        if not pid:
            return
        delete_product(int(pid))
        QMessageBox.information(self, "Deleted", "Product deleted.")
        self.load_products()
        self.product_added.emit()
        self.id_input.clear()
        self.name_input.clear()
