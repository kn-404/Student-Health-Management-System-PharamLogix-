import sys
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
from main_menu import StudentDashboard  # Adjust class name as needed
from main_menu import MainDashboard  # Adjust class name as needed
from main_menu import App  # Adjust class name as needed
# === Secondary Page Template ===
class DetailPage(QWidget):
    def __init__(self, title_text, student_name=None):
        super().__init__()
        
        self.setWindowTitle(title_text)
        self.setGeometry(200, 200, 400, 300)

        main_layout = QVBoxLayout(self)

        # === Top bar with "Back to Main Menu" button ===
        top_bar = QHBoxLayout()
        top_bar.addStretch()

        back_btn = QPushButton("Back to Main Menu")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: black;
                font-weight: bold;
                border-radius: 10px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        back_btn.clicked.connect(self.go_to_main_menu)
        top_bar.addWidget(back_btn)
        main_layout.addLayout(top_bar)

        # === Page content ===
        title = QLabel(title_text)
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Bold))
        main_layout.addWidget(title)

        if student_name:
            name_label = QLabel(f"Student: {student_name}")
            name_label.setAlignment(Qt.AlignCenter)
            name_label.setFont(QFont("Arial", 12))
            main_layout.addWidget(name_label)

    def go_to_main_menu(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        menu_path = os.path.join(base_dir, "main_menu.py")
        if os.path.exists(menu_path):
            subprocess.Popen([sys.executable, menu_path])
        self.close()


# === Main Menu Window ===
class MainMenu(QWidget):
    def __init__(self, student_name=None, parent=None):
        super().__init__()
        self.parent_window = parent  # ✅ store reference
        self.student_name = student_name
        self.setWindowTitle("Medical Check-Up")
        self.setFixedSize(727, 411)

        from background_utils import set_background
        set_background(self)

        # Transparent Overlay Container
        self.container = QWidget(self)
        self.container.setGeometry(0, 0, 727, 411)
        self.container.setStyleSheet("background: transparent;")

        self.create_ui()

    def create_ui(self):
        layout = QVBoxLayout(self.container)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(15)

        # === Top-right Back to Main Menu button ===
        top_bar = QHBoxLayout()
        top_bar.addStretch()

        back_btn = QPushButton("Back to Main Menu")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: black;
                font-weight: bold;
                border-radius: 10px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        back_btn.clicked.connect(self.go_to_main_menu)
        top_bar.addWidget(back_btn)
        layout.addLayout(top_bar)

        # === Title ===
        title = QLabel("MEDICAL CHECK-UP")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: black;")
        layout.addWidget(title)

        # Student name display (optional)
        if self.student_name:
            name_label = QLabel(f"Student: {self.student_name}")
            name_label.setAlignment(Qt.AlignCenter)
            name_label.setFont(QFont("Arial", 12))
            name_label.setStyleSheet("color: black;")
            layout.addWidget(name_label)

        # === Buttons ===
        button_info = {
            "PHYSICAL DETAILS": self.open_physical_details,
            "PEDIATRIC DETAILS": self.open_pediatric_checkup,
            "GENERAL CHECKUP": self.open_general_checkup,
            "DENTAL DETAILS": self.open_dental_checkup,
            "OPHTHALMIC": self.open_opthalmic_checkup,
            "VACCINATION DETAILS": self.open_vaccination_details,
        }

        for label, action in button_info.items():
            btn = QPushButton(label)
            btn.setFixedHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    color: black;
                    font-weight: bold;
                    border-radius: 20px;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """)
            btn.clicked.connect(action)
            layout.addWidget(btn)

    def go_to_main_menu(self):
        """Return to the previous (main menu) window without reopening."""
        if self.parent_window:
            self.parent_window.show()  # ✅ show the main menu again
        self.close()
        
        
    # === Button functions ===
    def open_physical_details(self):
        if self.student_name:
            
            from phydetinp import physicalinfo
            self.phydet_window = physicalinfo(search_name=self.student_name, parent=self)
            self.hide()
            self.phydet_window.show()
        

    def open_general_checkup(self):
        if self.student_name:
            from stugencheck import generalcheckupinfo
            self.gencheck_window = generalcheckupinfo(search_name=self.student_name,parent=self)
            self.hide() 
            self.gencheck_window.show()
        

    def open_pediatric_checkup(self):
        from pedcheck import pediatricinfo
        self.pedcheck_window = pediatricinfo(search_name=self.student_name,parent=self)
        self.hide()  # hide current window (don’t close)
        self.pedcheck_window.show()
        
    def open_dental_checkup(self):
        from dentcheck import dentalinfo
        self.dentcheck_window = dentalinfo(search_name=self.student_name,parent=self)
        self.hide()  # hide current window (don’t close)
        self.dentcheck_window.show()
        

    def open_opthalmic_checkup(self):
        from stuopthdet import OpthalmicInfo
        self.opthcheck_window = OpthalmicInfo(search_name=self.student_name,parent=self)
        self.hide()  # hide current window (don’t close)
        self.opthcheck_window.show()
        

    def open_vaccination_details(self):
        from vaccwindow import VaccinationForm
        self.vacc_window = VaccinationForm(search_name=self.student_name,parent=self)  
        self.hide()  # hide current window (don’t close)
        self.vacc_window.show()

    # Helper to open another script
    def launch_file(self, filename):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, filename)
        if os.path.exists(file_path):
            subprocess.Popen([sys.executable, file_path])
            self.close()
        else:
            print(f"⚠️ File not found: {file_path}")


if __name__ == "__main__":
    # Check if student name was passed from main app
    student_name = None
    if len(sys.argv) > 1:
        student_name = sys.argv[1]

    app = QApplication(sys.argv)
    window = MainMenu(student_name=student_name)
    window.show()
    sys.exit(app.exec_())
