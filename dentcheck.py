import os
import subprocess
import mysql.connector
from mysql.connector import Error
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QGridLayout, QDateEdit, QMessageBox,
    QScrollArea, QHBoxLayout, QComboBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QDate

class dentalinfo(QWidget):
    def __init__(self, search_name=None, parent=None):
        super().__init__()
        self.parent_window = parent  # ✅ store reference
        self.search_name = search_name
        self.setWindowTitle("PharmaLogix")
        self.setFixedSize(800, 500)  # Window size

        # Form fields
        self.dentaldetails = [
            "UHID", "STUDENT NAME", "ORAL HYGIENE STATUS", "CLINICAL FINDINGS",
            "CARIES STATUS", "CARIES RISK PROFILE", "TREATMENT ADVICE",
            "DIETARY MODIFICATION", "NOTES", "DOCTOR NAME", "DATE OF CHECKUP"
        ]

        self.inputs = {}
        self.init_ui()
        self.create_table_if_not_exists()

    def init_ui(self):
        self.setAutoFillBackground(True)
        from background_utils import set_background
        set_background(self)

        main_layout = QVBoxLayout(self)

        # --- Title and Back Button ---
        top_layout = QHBoxLayout()
        title_label = QLabel("STUDENT DENTAL DETAILS")
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

        # --- Scroll Area with Form ---
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background: transparent; border: none;")

        inner_widget = QWidget()
        inner_layout = QVBoxLayout(inner_widget)
        grid_layout = QGridLayout()
        grid_layout.setVerticalSpacing(15)
        grid_layout.setHorizontalSpacing(20)

        field_style = """
            QLineEdit, QDateEdit, QComboBox {
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

        for row, detail in enumerate(self.dentaldetails):
            label = QLabel(detail)
            label.setFont(QFont("Arial", 11, QFont.Bold))
            label.setStyleSheet(field_style)
            

            # Dropdowns for specific fields
            if detail == "ORAL HYGIENE STATUS":
                input_field = QComboBox()
                input_field.addItems(["Select Option","GOOD", "FAIR", "POOR"])
            elif detail == "CARIES STATUS":
                input_field = QComboBox()
                input_field.addItems(["Select Option","MILD", "MODERATE", "SEVERE"])
            elif detail == "CARIES RISK PROFILE":
                input_field = QComboBox()
                input_field.addItems(["Select Option","LOW", "MEDIUM", "HIGH"])
            elif detail == "DATE OF CHECKUP":
                input_field = QDateEdit()
                input_field.setCalendarPopup(True)
                input_field.setDate(QDate.currentDate())
            else:
                input_field = QLineEdit()

            input_field.setStyleSheet(field_style)
            if detail == "STUDENT NAME" and self.search_name:
                input_field.setText(self.search_name)
                input_field.setReadOnly(True)
            grid_layout.addWidget(label, row, 0)
            grid_layout.addWidget(input_field, row, 1)
            self.inputs[detail] = input_field

        inner_layout.addLayout(grid_layout)
        scroll_area.setWidget(inner_widget)
        main_layout.addWidget(scroll_area)

        # --- Submit Button ---
        submit_btn = QPushButton("SUBMIT")
        submit_btn.setStyleSheet(btn_style)
        submit_btn.clicked.connect(self.submit_form)
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        bottom_layout.addWidget(submit_btn)
        bottom_layout.addStretch()
        main_layout.addLayout(bottom_layout)

    def resizeEvent(self, event):
        from background_utils import set_background
        set_background(self)
        super().resizeEvent(event)

    def go_to_main_menu(self):
        if self.parent_window:
            self.parent_window.show()  # ✅ show previous window again
        self.close()

    def submit_form(self):
        data = {}
        for key, widget in self.inputs.items():
            if isinstance(widget, QDateEdit):
                data[key] = widget.date().toString("yyyy-MM-dd")
            elif isinstance(widget, QComboBox):
                data[key] = widget.currentText()
            else:
                data[key] = widget.text().strip()

        if not data["UHID"] or not data["STUDENT NAME"]:
            QMessageBox.warning(self, "Missing Info", "Please fill UHID and Student Name.")
            return

        conn = self.get_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            columns = ', '.join([f"`{col.replace(' ', '_')}`" for col in data.keys()])
            placeholders = ', '.join(['%s'] * len(data))
            query = f"INSERT INTO dental_details ({columns}) VALUES ({placeholders})"
            cursor.execute(query, list(data.values()))
            conn.commit()
            QMessageBox.information(self, "Success", "Record saved successfully!")

            # Clear fields
            for widget in self.inputs.values():
                if isinstance(widget, QLineEdit):
                    widget.clear()
                elif isinstance(widget, QDateEdit):
                    widget.setDate(QDate.currentDate())
                elif isinstance(widget, QComboBox):
                    widget.setCurrentIndex(0)
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
            print("Database error:", e)
            return None

    def create_table_if_not_exists(self):
        conn = self.get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dental_details (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    UHID VARCHAR(250),
                    STUDENT_NAME VARCHAR(250),
                    ORAL_HYGIENE_STATUS VARCHAR(250),
                    CLINICAL_FINDINGS VARCHAR(250),
                    CARIES_STATUS VARCHAR(250),
                    CARIES_RISK_PROFILE VARCHAR(250),
                    TREATMENT_ADVICE VARCHAR(250),
                    DIETARY_MODIFICATION VARCHAR(250),
                    NOTES VARCHAR(250),
                    DOCTOR_NAME VARCHAR(250),
                    DATE_OF_CHECKUP DATE
                )
            """)
            conn.commit()
            print("Table created or already exists")
        except Error as e:
            print("Database error:", e)
        finally:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    print("hello")
    app = QApplication(sys.argv)
    form = dentalinfo()
    form.show()
    sys.exit(app.exec_())
