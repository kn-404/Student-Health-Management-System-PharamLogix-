import os
import subprocess
import sys
import mysql.connector
from mysql.connector import Error

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QRadioButton,
    QLineEdit, QPushButton, QGridLayout, QMessageBox,
    QVBoxLayout, QHBoxLayout, QButtonGroup, QDateEdit
)
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QFont
from PyQt5.QtCore import Qt, QDate


class VaccinationForm(QWidget):
    def __init__(self, search_name=None, parent=None):
        super().__init__()
        self.parent_window = parent  # ✅ store reference
        self.search_name = search_name
        self.setWindowTitle("PharmaLogix")
        self.setFixedSize(800, 500)

        from background_utils import set_background
        set_background(self)
        self.set_app_font()

        self.vaccines = [
            "DPT", "HEPATITIS B", "BCG", "PENTAVALE NT",
            "ROTAVIRUS", "MEASLES RUBELLA", "ORAL POLIO",
            "PCV PNEUMONIA", "JE - JAPANESE ENCEPHALITIS"
        ]

        self.radio_buttons = {}
        self.init_ui()


    def set_app_font(self):
        font = QFont("Arial", 12)
        font.setBold(True)
        QApplication.setFont(font)

    def go_to_main_menu(self):
        if self.parent_window:
            self.parent_window.show()  # ✅ show previous window again
        self.close()
    def init_ui(self):
        layout = QGridLayout()
        self.setAutoFillBackground(True)

        main_layout = QVBoxLayout(self)

        # --- Title and Back Button ---
        top_layout = QHBoxLayout()
       
        title_label = QLabel("STUDENT VACCINATION DETAILS")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        # title_label.setFixedWidth(600)
       
        # layout.addStretch()
    
        return_btn = QPushButton("BACK")
        btn_style = """
            QPushButton {
                background: white;
                border-radius: 8px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: lightgray;
            }
        """
        return_btn.setStyleSheet(btn_style)
        return_btn.setFixedWidth(100)
        # return_btn.setAlignment(Qt.AlignRight)
        return_btn.clicked.connect(self.go_to_main_menu)
      
       
        top_layout.addWidget(title_label, 2, Qt.AlignCenter)
        top_layout.addWidget(return_btn,0, Qt.AlignRight)
        main_layout.addLayout(top_layout)
        main_layout.addLayout(layout)

        # # Add large title label at the top
        # title_label = QLabel("VACCINATION HISTORY")
        # title_font = QFont("Arial", 24, QFont.Bold)
        # title_label.setFont(title_font)
        # title_label.setAlignment(Qt.AlignCenter)
        # title_label.setStyleSheet("background-color: white; padding: 4px; border-radius: 5px;")
        # layout.addWidget(title_label, 0, 0, 1, 3)  # Span 3 columns

        row = 1  # Start other widgets from row 1
        uhid_label = QLabel("UHID")
        uhid_label.setStyleSheet("background-color: white; padding: 4px; border-radius: 5px;")
        self.uhid_input = QLineEdit()
        layout.addWidget(uhid_label, row, 0)
        layout.addWidget(self.uhid_input, row, 1, 1, 2)
        row += 1
        student_label = QLabel("STUDENT NAME")
        student_label.setStyleSheet("background-color: white; padding: 4px; border-radius: 5px;")
        self.student_input = QLineEdit()
        if self.search_name:
            self.student_input.setText(self.search_name)
            self.student_input.setReadOnly(True)
        layout.addWidget(student_label, row, 0)
        layout.addWidget(self.student_input, row, 1, 1, 2)
        row += 1
        for vaccine in self.vaccines:
            label = QLabel(vaccine)
            label.setStyleSheet("background-color: white; padding: 4px; border-radius: 5px;")

            yes_button = QRadioButton("YES")
            no_button = QRadioButton("NO")

            # Default to NO
            no_button.setChecked(True)

            # Group YES/NO per vaccine
            button_group = QButtonGroup(self)
            button_group.addButton(yes_button)
            button_group.addButton(no_button)

            layout.addWidget(label, row, 0)
            layout.addWidget(yes_button, row, 1)
            layout.addWidget(no_button, row, 2)
            self.radio_buttons[vaccine] = (yes_button, no_button)
            row += 1

        # Doctor name input
        
        doctor_label = QLabel("DOCTOR NAME")
        doctor_label.setStyleSheet("background-color: white; padding: 4px; border-radius: 5px;")
        self.doctor_input = QLineEdit()
        layout.addWidget(doctor_label, row, 0)
        layout.addWidget(self.doctor_input, row, 1, 1, 2)
        row += 1

        # Calendar-based date picker
        date_label = QLabel("DATE OF CHECKUP")
        date_label.setStyleSheet("background-color: white; padding: 4px; border-radius: 5px;")
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("dd-MM-yyyy")
        self.date_input.setDate(QDate.currentDate())  # Set current date as default
        layout.addWidget(date_label, row, 0)
        layout.addWidget(self.date_input, row, 1, 1, 2)
        row += 1

        # Buttons
        submit_btn = QPushButton("SUBMIT")
        return_btn = QPushButton("RETURN TO SEARCH")
        add_btn = QPushButton("ADD CATEGORY")
        submit_btn.setFixedSize(250, 35)
        return_btn.setFixedSize(250, 35)
        add_btn.setFixedSize(250, 35)

        submit_btn.clicked.connect(self.submit_form)
        return_btn.clicked.connect(self.go_to_main_menu)
        layout.addWidget(submit_btn, row, 1)
        # layout.addWidget(return_btn, row, 1)
        # layout.addWidget(add_btn, row, 2)

        # use main_layout as the window's layout (contains header + grid)
        self.setLayout(main_layout)

    def connect_to_database(self):
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
            conn = self.connect_to_database()
            if not conn:
                print("No database connection exists")
                return
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS vaccination_details (
                        UHID VARCHAR(250),
                        STUDENT_NAME VARCHAR(250),
                        DPT VARCHAR(5), 
                        HEPATITIS_B VARCHAR(5), 
                        BCG VARCHAR(5),
                        PENTAVALE_NT VARCHAR(5),
                        ROTAVIRUS VARCHAR(5), 
                        MEASLES_RUBELLA VARCHAR(5), 
                        ORAL_POLIO VARCHAR(5),
                        PCV_PNEUMONIA VARCHAR(5), 
                        JE_JAPANESE_ENCEPHALITIS VARCHAR(5),
                        DOCTOR_NAME VARCHAR(250),
                        DATE_OF_CHECKUP DATE
                    )
                """)
                conn.commit()
                print("Table created or already exists")
            except Error as e:
                print("Database error")
                # QMessageBox.critical(self, "Database Error", f"Table creation failed:\n{e}")
            finally:
                cursor.close()
                conn.close()    
        
        # return mysql.connector.connect(
        #     host="localhost",
        #     user="root",      
        #     password="deens",  
        #     database="pharmalogix"   
        # )

    def submit_form(self):
        try:
            data = {
                "UHID": self.uhid_input.text().strip(),
                "STUDENT_NAME": self.student_input.text().strip(),
                "doctor_name": self.doctor_input.text().strip(),
                "date_of_checkup": self.date_input.date().toString("yyyy-MM-dd")
            }

            for vaccine, (yes, no) in self.radio_buttons.items():
                key = vaccine.lower().replace(" ", "_").replace("-", "").replace("__", "_")
                if yes.isChecked():
                    value = "YES"
                elif no.isChecked():
                    value = "NO"
                else:
                    QMessageBox.warning(self, "Input Error", f"Please select YES or NO for '{vaccine}'.")
                    return
                data[key] = value
            self.create_table_if_not_exists()
            db = self.connect_to_database()
           
            cursor = db.cursor()

            columns = ', '.join(data.keys())
            values = ', '.join(['%s'] * len(data))
            sql = f"INSERT INTO vaccination_details ({columns}) VALUES ({values})"

            cursor.execute(sql, list(data.values()))
            db.commit()

            QMessageBox.information(self, "Success", "Vaccination record submitted successfully!")

            cursor.close()
            db.close()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to submit data:\n{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = VaccinationForm()
    form.show()
    sys.exit(app.exec_())
