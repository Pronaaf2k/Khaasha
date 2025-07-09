# ui/dashboard_page.py

from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout,
    QComboBox, QLineEdit, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox
)
from PySide6.QtCore import Signal, Qt
import pandas as pd

from logic.log_operations import (
    log_bought, log_used, get_today_inventory_with_leftover, get_today_totals,
    clear_inventory, clear_daily_logs   # <-- add these
)
from logic.product_operations import get_all_products
from ui.log_viewer_page import LogViewerPage
from ui.add_product_page import AddProductPage
from ui.add_user_page import AddUserPage

class DashboardPage(QWidget):
    logout_requested = Signal()

    def __init__(self, role):
        super().__init__()
        self.role = role
        self.viewer = None
        self.add_product_page = None
        self.add_user_page = None

        self.setStyleSheet("""
            QWidget {
                background-color: #f0f2f5;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel#header {
                font-size: 22px;
                font-weight: 600;
            }
            QLineEdit, QComboBox {
                padding: 10px;
                font-size: 14px;
                border-radius: 6px;
                border: 1px solid #ccc;
            }
            QPushButton {
                background-color: #1877f2;
                color: white;
                font-size: 14px;
                padding: 10px 16px;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #165ecb;
            }
        """)

        main_layout = QVBoxLayout(self)

        # Header
        self.header = QLabel(f"Welcome, {role.capitalize()}")
        self.header.setObjectName("header")
        self.header.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(self.header)

        # Summary
        self.summary = QLabel()
        main_layout.addWidget(self.summary)

        # Product selector & amount
        self.product_select = QComboBox()
        main_layout.addWidget(self.product_select)
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter amount in kg")
        main_layout.addWidget(self.amount_input)

        # Button row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        # Always-visible buttons
        self.buy_btn     = QPushButton("Log Bought")
        self.use_btn     = QPushButton("Log Used")
        self.history_btn = QPushButton("View History")
        self.logout_btn  = QPushButton("Logout")

        self.buy_btn.clicked.connect(lambda: self.log(True))
        self.use_btn.clicked.connect(lambda: self.log(False))
        self.history_btn.clicked.connect(self.show_history)
        self.logout_btn.clicked.connect(self.logout_requested.emit)

        for btn in (self.buy_btn, self.use_btn, self.history_btn, self.logout_btn):
            btn_row.addWidget(btn)

        # Add Product: visible to Admins & Staff
        self.add_product_btn = QPushButton("Add Product")
        self.add_product_btn.clicked.connect(self.show_add_product)
        btn_row.addWidget(self.add_product_btn)

        # Admin-only buttons
        if self.role == "admin":
            self.clear_inv_btn = QPushButton("Clear Inventory")
            btn_row.addWidget(self.clear_inv_btn)
            self.clear_inv_btn.clicked.connect(self.handle_clear_inventory)
            self.export_btn      = QPushButton("Export to Excel")
            self.add_user_btn    = QPushButton("Add User")

            self.export_btn.clicked.connect(self.export_to_excel)
            self.add_user_btn.clicked.connect(self.show_add_user)

            btn_row.addWidget(self.export_btn)
            btn_row.addWidget(self.add_user_btn)

        main_layout.addLayout(btn_row)

        # Inventory table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Product", "Bought", "Used", "Leftover From Past", "Remaining Today"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        main_layout.addWidget(self.table)

        # Initialize data
        self.load_products()
        self.refresh()

    def load_products(self):
        """Populate the dropdown with all products."""
        products = get_all_products()
        self.product_select.clear()
        self.product_select.addItems(products)

    def refresh(self):
        """Refresh the summary and table with today's data."""
        total_bought, total_used = get_today_totals()
        self.summary.setText(f"Today: Bought {total_bought:.1f} kg | Used {total_used:.1f} kg")

        rows = get_today_inventory_with_leftover()
        self.table.setRowCount(len(rows))
        for i, (product, bought, used, leftover, remaining) in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(product))
            self.table.setItem(i, 1, QTableWidgetItem(f"{bought:.1f}"))
            self.table.setItem(i, 2, QTableWidgetItem(f"{used:.1f}"))
            self.table.setItem(i, 3, QTableWidgetItem(f"{leftover:.1f}"))
            self.table.setItem(i, 4, QTableWidgetItem(f"{remaining:.1f}"))
        self.table.resizeColumnsToContents()

    def log(self, is_buy: bool):
        """Log bought or used amount for the selected product."""
        product = self.product_select.currentText()
        try:
            amt = float(self.amount_input.text())
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid number.")
            return

        if is_buy:
            log_bought(product, amt)
        else:
            log_used(product, amt)
        self.amount_input.clear()
        self.refresh()

    def show_history(self):
        """Open the full history log viewer."""
        if not self.viewer:
            self.viewer = LogViewerPage()
        self.viewer.show()

    def export_to_excel(self):
        """Export today's table to an Excel file (admin only)."""
        rows = get_today_inventory_with_leftover()
        data = [
            {
                "Product": product,
                "Bought": bought,
                "Used": used,
                "Leftover From Past": leftover,
                "Remaining Today": remaining
            }
            for product, bought, used, leftover, remaining in rows
        ]
        df = pd.DataFrame(data)
        path, _ = QFileDialog.getSaveFileName(self, "Save Excel File", "", "Excel Files (*.xlsx)")
        if path:
            df.to_excel(path, index=False)
            QMessageBox.information(self, "Exported", f"Saved to {path}")

    def show_add_product(self):
        """Open the Add Product dialog."""
        if not self.add_product_page:
            self.add_product_page = AddProductPage()
            self.add_product_page.product_added.connect(self.load_products)
        self.add_product_page.show()

    def show_add_user(self):
        """Open the Add User dialog (admin only)."""
        if not self.add_user_page:
            self.add_user_page = AddUserPage()
        self.add_user_page.show()

    def handle_clear_inventory(self):
        """Clear today's inventory and logs (admin only)."""
        reply = QMessageBox.question(
            self, "Confirm Clear",
            "Are you sure you want to clear today's inventory and logs?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            clear_inventory()
            clear_daily_logs()
            self.refresh()
            QMessageBox.information(self, "Cleared", "Today's inventory and logs have been cleared.")
