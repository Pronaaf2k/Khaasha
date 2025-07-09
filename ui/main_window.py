# ui/main_window.py
from PySide6.QtWidgets import QMainWindow, QStackedWidget
from ui.login_page import LoginPage
from ui.dashboard_page import DashboardPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Khaasha Inventory")
        self.setGeometry(100, 100, 1200, 800)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.login_page = LoginPage()
        self.dashboard_page = None

        self.login_page.login_success.connect(self.show_dashboard)
        self.stack.addWidget(self.login_page)
        self.stack.setCurrentWidget(self.login_page)

    def show_dashboard(self, role):
        self.dashboard_page = DashboardPage(role)
        self.dashboard_page.logout_requested.connect(self.return_to_login)
        self.stack.addWidget(self.dashboard_page)
        self.stack.setCurrentWidget(self.dashboard_page)

    def return_to_login(self):
        self.stack.setCurrentWidget(self.login_page)
