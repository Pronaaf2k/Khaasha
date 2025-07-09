from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel
from logic.log_operations import get_full_inventory_history

class LogViewerPage(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("📊 Inventory Log Viewer")
        layout = QVBoxLayout(self)

        self.setStyleSheet("""
            QWidget {
                background-color: #f0f2f5;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel#title {
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)

        self.title = QLabel("📊 Inventory Log Viewer")
        self.title.setObjectName("title")
        layout.addWidget(self.title)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Date", "Product", "Bought", "Used", "Leftover From Past", "Remaining Today"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        self.load_data()

    def load_data(self):
        rows = get_full_inventory_history()
        self.table.setRowCount(len(rows))
        for row_idx, (log_date, product, bought, used, leftover_past, remaining_today) in enumerate(rows):
            self.table.setItem(row_idx, 0, QTableWidgetItem(log_date))
            self.table.setItem(row_idx, 1, QTableWidgetItem(product))
            self.table.setItem(row_idx, 2, QTableWidgetItem(f"{bought:.1f}"))
            self.table.setItem(row_idx, 3, QTableWidgetItem(f"{used:.1f}"))
            self.table.setItem(row_idx, 4, QTableWidgetItem(f"{leftover_past:.1f}"))
            self.table.setItem(row_idx, 5, QTableWidgetItem("" if remaining_today is None else f"{remaining_today:.1f}"))
        self.table.resizeColumnsToContents()
