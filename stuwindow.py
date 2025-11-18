# import sys
# from PyQt5.QtWidgets import (
#     QApplication, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox
# )
# from PyQt5.QtGui import QPixmap, QPainter, QFont
# from PyQt5.QtCore import Qt
# from PIL import Image
# import mysql.connector
# import os


# class RegisterStudent(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Register Student")

#         screen = QApplication.primaryScreen()
#         screen.setFixedSize(800, 500)
#         self.resize(self.screen_width, self.screen_height)

#         # Background setup
#         self.original_bg = "Bg.jpg"
#         self.resized_bg = "resized_Bg.jpg"
#         self.resizeBackground()

#         self.bg = QPixmap(self.resized_bg)
#         self.initUI()

#     def resizeBackground(self):
#         if not os.path.exists(self.resized_bg):
#             img = Image.open(self.original_bg)
#             img = img.resize((self.screen_width, self.screen_height))
#             img.save(self.resized_bg)

#     def paintEvent(self, event):
#         painter = QPainter(self)
#         painter.drawPixmap(self.rect(), self.bg)

#     def initUI(self):
#         self.setFont(QFont("Arial", 10))

#         # Labels and positions
#         labels = [
#             "REGISTRATION DATE (DD-MM-YYYY)", "DATE OF BIRTH (DD-MM-YYYY)", "MOTHER’S NAME",
#             "FATHER/GUARDIAN’S NAME", "PERMANENT ADDRESS", "PARENT’S CONTACT NUMBER",
#             "STUDENT NAME", "SEX", "BLOOD GROUP", "EMERGENCY CONTACT PERSON", "EMERGENCY CONTACT NUMBER"
#         ]

#         self.fields = []
#         positions = [(80, 100), (80, 160), (80, 220), (600, 220), (80, 280),
#                      (80, 340), (80, 400), (600, 100), (600, 160), (600, 280), (600, 340)]

#         # Input field styling
#         field_style = """
#             QLineEdit {
#                 border: 2px solid white;
#                 border-radius: 15px;
#                 padding: 5px 10px;
#                 background-color: white;
#             }
#         """

#         for idx, (label, pos) in enumerate(zip(labels, positions)):
#             lbl = QLabel(label, self)
#             lbl.move(pos[0], pos[1])
#             lbl.setStyleSheet("color: black; font-weight: bold; background: transparent;")
#             lbl.setFont(QFont("Arial", 10, QFont.Bold))

#             # Use ComboBox for Sex and Blood Group
#             if label == "SEX":
#                 field = QComboBox(self)
#                 field.addItems(["Male", "Female", "Other"])
#             elif label == "BLOOD GROUP":
#                 field = QComboBox(self)
#                 field.addItems(["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
#             else:
#                 field = QLineEdit(self)
#                 field.setStyleSheet(field_style)

#             field.setGeometry(pos[0], pos[1] + 25, 300, 35)
#             self.fields.append(field)

#         # Submit Button
#         self.submit_btn = QPushButton("SUBMIT", self)
#         self.submit_btn.setGeometry(600, 400, 100, 40)
#         self.submit_btn.clicked.connect(self.submitForm)
#         self.submit_btn.setStyleSheet("""
#             QPushButton {
#                 background-color: white;
#                 font-weight: bold;
#                 border-radius: 10px;
#                 border: 2px solid black;
#             }
#         """)

#         # Return to Main Menu Button
#         self.return_btn = QPushButton("RETURN TO MAIN MENU", self)
#         self.return_btn.setGeometry(720, 400, 180, 40)
#         self.return_btn.clicked.connect(self.close)
#         self.return_btn.setStyleSheet("""
#             QPushButton {
#                 background-color: white;
#                 font-weight: bold;
#                 border-radius: 10px;
#                 border: 2px solid black;
#             }
#         """)

#     def submitForm(self):
#         data = []
#         for field in self.fields:
#             if isinstance(field, QComboBox):
#                 data.append(field.currentText())
#             else:
#                 data.append(field.text())

#         # Check if any field is empty
#         if any(not val.strip() for val in data):
#             QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
#             return

#         try:
#             conn = mysql.connector.connect(
#                 host="localhost",
#                 user="root",         
#                 password="deens",    
#                 database="pharmalogix"  
#             )
#             cursor = conn.cursor()

#             query = """
#                 INSERT INTO students (
#                     registration_date, dob, mother_name, father_name, address,
#                     parent_contact, student_name, sex, blood_group,
#                     emergency_contact_person, emergency_contact_number
#                 ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#             """

#             cursor.execute(query, tuple(data))
#             conn.commit()
#             cursor.close()
#             conn.close()

#             QMessageBox.information(self, "Success", "Student registered successfully!")
#             for field in self.fields:
#                 if isinstance(field, QLineEdit):
#                     field.clear()

#         except Exception as e:
#             QMessageBox.critical(self, "Database Error", f"Error: {e}")


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = RegisterStudent()
#     window.showFullScreen()
#     sys.exit(app.exec_())

import os
import subprocess
import mysql.connector
from mysql.connector import Error
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QGridLayout, QDateEdit, QMessageBox,
    QScrollArea, QHBoxLayout
)
from PyQt5.QtGui import QFont, QPalette, QBrush, QPixmap
from PyQt5.QtCore import Qt, QDate

class student_registration(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PharmaLogix")
        self.setFixedSize(800, 500)  # Window size

        from background_utils import set_background
        set_background(self)

        # Form fields
        self.student_details = [
    
            "REGISTRATION DATE", "DATE OF BIRTH", "MOTHER NAME",
            "FATHER NAME", "PERMANENT ADDRESS", "PARENT CONTACT NUMBER",
            "STUDENT NAME", "SEX", "BLOOD GROUP", "EMERGENCY CONTACT PERSON", "EMERGENCY CONTACT NUMBER"
        ]
        

        self.inputs = {}
        self.init_ui()

        # Initialize DB
        self.create_table_if_not_exists()

    def init_ui(self):
        self.setAutoFillBackground(True)
        # self.update_background()

        main_layout = QVBoxLayout(self)

        # Top layout for title and back button
        top_layout = QHBoxLayout()
        title_label = QLabel("STUDENT DETAILS")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(title_label)
        top_layout.addStretch()

        return_btn = QPushButton("BACK")
        btn_style = """
            QPushButton {
                background: white;
                border-radius: 10px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: lightgray;
            }
        """
        return_btn.setStyleSheet(btn_style)
        return_btn.clicked.connect(self.go_to_main_menu)
        top_layout.addWidget(return_btn)

        main_layout.addLayout(top_layout)

        # Scrollable form
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background: transparent; border: none;")
        inner_widget = QWidget()
        inner_layout = QVBoxLayout(inner_widget)
        grid_layout = QGridLayout()
        grid_layout.setVerticalSpacing(15)
        grid_layout.setHorizontalSpacing(20)

        field_style = """
            QLineEdit, QDateEdit {
                background: white;
                border-radius: 10px;
                padding: 5px;
                font-size: 12px;
            }
            QLabel {
                background: rgba(255,255,255,0.8);
                border-radius: 10px;
                padding: 5px;
            }
        """

        for row, detail in enumerate(self.student_details):
            label = QLabel(detail)
            label.setFont(QFont("Arial", 11, QFont.Bold))
            label.setStyleSheet(field_style)
            if detail == "REGISTRATION DATE" or detail == "DATE OF BIRTH":
                input_field = QDateEdit()
                input_field.setCalendarPopup(True)
                input_field.setDate(QDate.currentDate())
            else:
                input_field = QLineEdit()
            input_field.setStyleSheet(field_style)
            grid_layout.addWidget(label, row, 0)
            grid_layout.addWidget(input_field, row, 1)
            self.inputs[detail] = input_field

        inner_layout.addLayout(grid_layout)
        scroll_area.setWidget(inner_widget)
        main_layout.addWidget(scroll_area)

        # Submit button at bottom
        submit_btn = QPushButton("SUBMIT")
        submit_btn.setStyleSheet(btn_style)
        submit_btn.clicked.connect(self.submit_form)  
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        bottom_layout.addWidget(submit_btn)
        bottom_layout.addStretch()
        main_layout.addLayout(bottom_layout)



    def go_to_main_menu(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        menu_path = os.path.join(base_dir, "main_menu.py")
        subprocess.Popen([sys.executable, menu_path])
        self.close()
        
    def submit_form(self):
        data = {}
        for key, widget in self.inputs.items():
            if isinstance(widget, QDateEdit):
                data[key] = widget.date().toString("yyyy-MM-dd")
            else:
                data[key] = widget.text().strip()

        # Basic validation
        

        conn = self.get_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            columns = ', '.join([f"`{col.replace(' ', '_')}`" for col in data.keys()])
            placeholders = ', '.join(['%s'] * len(data))
            query = f"INSERT INTO student_details ({columns}) VALUES ({placeholders})"
            cursor.execute(query, list(data.values()))
            conn.commit()
            QMessageBox.information(self, "Success", "Record saved successfully!")
            # clear fields
            for widget in self.inputs.values():
                if isinstance(widget, QLineEdit):
                    widget.clear()
                elif isinstance(widget, QDateEdit):
                    widget.setDate(QDate.currentDate())
        except Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to insert data:\n{e}")
        finally:
            cursor.close()
            conn.close()

    def get_connection(self):
            try:
                conn = mysql.connector.connect(
                    host="localhost",
                    user="root",        
                    password="deens",        
                    database="pharmalogix"
                )
                print("Database connected")
                return conn
            except Error as e:
                print("Database error")
                return None

    def create_table_if_not_exists(self):
            conn = self.get_connection()
            if not conn:
                return
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS student_details (    
            REGISTRATION_DATE date,
            DATE_OF_BIRTH date,
            MOTHER_NAME varchar(255),
            FATHER_NAME varchar(255),
            PERMANENT_ADDRESS varchar(400),
            PARENT_CONTACT_NUMBER varchar(100),
            STUDENT_NAME varchar(255),
            SEX varchar(5),
            BLOOD_GROUP varchar(5),
            EMERGENCY_CONTACT_PERSON varchar(255),
            EMERGENCY_CONTACT_NUMBER varchar(100))
        
                    
                """)
                conn.commit()
                print("Table created or already exists")
            except Error as e:
                print("Database error")
                # QMessageBox.critical(self, "Database Error", f"Table creation failed:\n{e}")
            finally:
                cursor.close()
                conn.close()
if __name__ == "__main__":
    print("hello")
    app = QApplication(sys.argv)
    form = student_registration()
    form.show()
    
    sys.exit(app.exec_())