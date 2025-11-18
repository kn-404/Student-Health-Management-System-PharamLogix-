import sys
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QPainter, QPixmap, QFont, QIcon, QDesktopServices
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QStackedWidget, QMessageBox, 
)

# Paths to assets — update as needed
LOGO_PATH = r"C:\Python\Project\PROJECT\L.png"
ICON_MAG = r"C:\Users\Student\Downloads\magnifier.png"


# ---------- Base Page ----------
class PageWithLogo(QWidget):
    """Base class for pages with a background and logo."""
    def __init__(self):
        super().__init__()
        from background_utils import set_background
        set_background(self)

    def _add_logo(self):
        logo = QLabel(self)
        pix = QPixmap(LOGO_PATH)
        if not pix.isNull():
            pix = pix.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo.setPixmap(pix)
            logo.setFixedSize(pix.size())
            logo.move(20, 20)


# ---------- Main Dashboard ----------
class MainDashboard(PageWithLogo):
    def __init__(self, open_student_dashboard):
        super().__init__()
        self.open_student_dashboard = open_student_dashboard
        self._build_ui()

    def _build_ui(self):
        self.setFixedSize(800, 500)
        self._add_logo()

        logout = QPushButton("LOGOUT", self)
        logout.setFont(QFont("Arial", 12))
        logout.clicked.connect(self.logout)

        search = QLineEdit(self)
        search.setPlaceholderText("Enter Student Name")
        search.setFont(QFont("Arial", 18))
        search.setFixedSize(600, 50)
        search.addAction(QIcon(ICON_MAG), QLineEdit.LeadingPosition)
        search.setStyleSheet("""
            QLineEdit {
                background: white;
                border: 2px solid gray;
                border-radius: 25px;
                padding-left: 40px;
                font-size: 18px;
                color: black;
            }
            QLineEdit:focus { border-color: #555; }
        """)
        search.returnPressed.connect(lambda: self._search_student(search.text()))

    # organization label removed per request

        btn1 = QPushButton("Register New Student", self)
        btn2 = QPushButton("About Us", self)
        for btn in (btn1, btn2):
            btn.setFont(QFont("Arial", 18))
            btn.setFixedSize(300, 50)
            btn.setStyleSheet("""
                QPushButton {
                    background: white;
                    border: 2px solid black;
                    border-radius: 25px;
                    color: black;
                    font-size: 18px;
                    padding: 0 12px;
                }
                QPushButton:pressed {
                    background: #dddddd;
                    border-style: inset;
                }
            """)
        btn1.clicked.connect(self.open_student_regitration)
        btn2.clicked.connect(self.open_youtube)
        top = QHBoxLayout()
        top.addStretch()
        top.addWidget(logout)
        top.setContentsMargins(20, 20, 20, 0)

        title = QLabel("Pharma Logix", self)
        title.setFont(QFont("Arial", 32, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        center = QVBoxLayout()
        center.setAlignment(Qt.AlignCenter)
        center.addWidget(title)
        center.addSpacing(10)
        center.addWidget(search, alignment=Qt.AlignCenter)
        center.addSpacing(30)
        center.addWidget(btn1, alignment=Qt.AlignCenter)
        center.addSpacing(15)
        center.addWidget(btn2, alignment=Qt.AlignCenter)

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addStretch()
        layout.addLayout(center)
        layout.addStretch()

    def open_youtube(self):
        # Open the organisation's About page in the default browser
        url = QUrl("https://empactngo.my.canva.site")
        QDesktopServices.openUrl(url)

    def _search_student(self, name):
        if not name.strip():
            QMessageBox.warning(self, "Input Error", "Please enter a student name.")
        else:
            self.open_student_dashboard(name)
    def logout(self):
        if self.parent_window:
            self.parent_window.show()  # ✅ show the main menu again
        self.close()

    def open_student_regitration(self):
        """Opens stuwindow.py (Student Registration page)."""
        import subprocess, os, sys
        base_dir = os.path.dirname(os.path.abspath(__file__))
        stuwindow_path = os.path.join(base_dir, "stuwindow.py")
        if os.path.exists(stuwindow_path):
            subprocess.Popen([sys.executable, stuwindow_path])
            self.close()
        else:
            QMessageBox.warning(self, "File Missing", f"Could not find:\n{stuwindow_path}")

# ---------- Student Dashboard ----------
class StudentDashboard(PageWithLogo):
    def __init__(self, student_name, go_back):
        super().__init__()
        self.student_name = student_name
        self.go_back = go_back
        self._build_ui()
    
    def _build_ui(self):
        import os, sys, subprocess

        self.setFixedSize(800, 500)
        self._add_logo()

        back = QPushButton("BACK", self)
        back.setFont(QFont("Arial", 12))
        back.clicked.connect(self.go_back)

        # organization label removed per request

        student_label = QLabel(f"{self.student_name}", self)
        student_label.setFont(QFont("Arial", 18, QFont.Bold))
        student_label.setAlignment(Qt.AlignCenter)

        # === Buttons ===
        btn1 = QPushButton("View Medical History 🧬", self)
        btn2 = QPushButton("Add Medical Checkup Details 🩺", self)
        btn3 = QPushButton("Generate Report 📄", self)

        for btn in (btn1, btn2, btn3):
            btn.setFont(QFont("Arial", 18))
            btn.setFixedSize(300, 50)
            btn.setStyleSheet("""
                QPushButton {
                    background: white;
                    border: none;
                    border-radius: 25px;
                    font-size: 18px;
                    padding: 8px 16px;
                }
                QPushButton:pressed { background: #dddddd; }
            """)

        # --- Button connections ---
        btn2.clicked.connect(self.open_medical_checkup_history)
        btn1.clicked.connect(self.open_medical_history)
        btn3.clicked.connect(self.generate_report)

        top = QHBoxLayout()
        top.addStretch()
        top.addWidget(back)
        top.setContentsMargins(20, 20, 20, 0)

        title = QLabel("Pharma Logix", self)
        title.setFont(QFont("Arial", 32, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        center = QVBoxLayout()
        center.setAlignment(Qt.AlignCenter)
        center.addWidget(title)
        center.addSpacing(15)
        center.addWidget(student_label)
        center.addSpacing(25)

        # Two buttons in one row
        row = QHBoxLayout()
        row.addWidget(btn1)
        row.addSpacing(30)
        row.addWidget(btn2)

        center.addLayout(row)
        center.addSpacing(20)
        center.addWidget(btn3, alignment=Qt.AlignCenter)

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addStretch()
        layout.addLayout(center)
        layout.addStretch()

    # === Open Medical Checkup History Function ===
    def open_medical_checkup_history(self):
        """Opens stuhis.py (Medical Check-Up page)."""
        from stuphydet import MainMenu  # local import to avoid circular imports
        self.studet_window = MainMenu(student_name=self.student_name, parent=self)  # ✅ pass self as parent
        self.hide()  # ✅ hide current main menu
        self.studet_window.show()
        
    def open_medical_history(self):
        """Opens stuhis.py (Medical Check-Up page)."""
        from stuhis import MainMenu  # local import to avoid circular imports
        self.stuhis_window = MainMenu(student_name=self.student_name, parent=self)  # ✅ pass self as parent
        self.hide()  # ✅ hide current main menu
        self.stuhis_window.show()
    def generate_report(self):
        """Opens generate_report.py (Generate Report page)."""
        from generate_report import ReportPage  # local import to avoid circular imports
        self.report_window = ReportPage(parent=self)  # ✅ pass self as parent
        self.hide()  # ✅ hide current main menu
        self.report_window.show()

# ---------- App Controller ----------
class App(QStackedWidget):
    def __init__(self, initial_page):
        super().__init__()
        self.student_name = initial_page
        self.setFixedSize(800, 500)

        self.student_dashboard = StudentDashboard(self.student_name, go_back=self.show_main_dashboard)
        self.main_dashboard = MainDashboard(open_student_dashboard=self.show_student_dashboard)
        if initial_page != "Main":
            self.addWidget(self.student_dashboard)
        else:        
            self.addWidget(self.main_dashboard)

    def show_student_dashboard(self, student_name):
        student_page = StudentDashboard(student_name, go_back=self.show_main_dashboard)
        self.addWidget(student_page)
        self.setCurrentWidget(student_page)

    def show_main_dashboard(self):
        self.setCurrentWidget(self.main_dashboard)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = App(sys.argv[1] if len(sys.argv) > 1 else "Main")
    window.setWindowTitle("Pharma Logix - Main Menu")
    window.show()
    sys.exit(app.exec_())