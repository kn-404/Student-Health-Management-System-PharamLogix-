import os
import sys
import subprocess
import mysql.connector
from mysql.connector import Error
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QGridLayout, QDateEdit, QMessageBox,
    QScrollArea, QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QDate


class OpthalmicInfo(QWidget):
    def __init__(self, search_name=None, parent=None):
        super().__init__()
        self.parent_window = parent  # ✅ store reference
        self.search_name = search_name
        self.setWindowTitle("PharmaLogix - Ophthalmic Details")
        self.resize(800, 700)
        

        self.db_name = "pharmalogix"

        from background_utils import set_background
        set_background(self)
        
        self.fields = [
            "UHID", "STUDENT NAME", "HEAD POSTURE", "CORNEAL",
            "COVER TEST", "EXTERNAL OCULAR MOVEMENT", "CONVERGENCE",
            "EYE COMPLAINTS", "DOCTOR NAME", "DATE OF CHECKUP"
        ]
        self.inputs = {}
        

        self.create_table_if_not_exists()
        self.init_ui()
    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # # ---------- HEADER BAR ----------
        header_bar = QHBoxLayout()

       

        top_layout = QHBoxLayout()
        title_label = QLabel("STUDENT OPTHALMIC DETAILS")
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

        # centered heading
        # title = QLabel("STUDENT OPHTHALMIC DETAILS")
        # title.setFont(QFont("Arial", 18, QFont.Bold))
        # title.setAlignment(Qt.AlignCenter)

        # fill space on right side so title stays centered
        right_spacer = QLabel()
        right_spacer.setFixedWidth(40)

        header_bar.addStretch()
        header_bar.addWidget(title_label)
        header_bar.addStretch()
        header_bar.addWidget(right_spacer)

        main_layout.addLayout(header_bar)
        main_layout.addSpacing(10)

        # ---------- SCROLL AREA ----------
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # ---------- FORM ----------
        form_layout = QGridLayout()
        form_layout.setVerticalSpacing(10)
        form_layout.setHorizontalSpacing(25)

        for i, field in enumerate(self.fields):
            label = QLabel(field)
            label.setFont(QFont("Arial", 11))
            if field == "DATE OF CHECKUP":
                input_widget = QDateEdit()
                input_widget.setCalendarPopup(True)
                input_widget.setDate(QDate.currentDate())
            else:
                input_widget = QLineEdit()
                input_widget.setPlaceholderText(f"Enter {field.lower()}...")

            input_widget.setStyleSheet("""
                QLineEdit, QDateEdit {
                    background: white;
                    border-radius: 8px;
                    padding: 5px;
                    font-size: 12px;
                }
                QLabel {
                    font-weight: bold;
                    background: rgba(255,255,255,0.8);
                    border-radius: 5px;
                    padding: 4px;
                }
            """)
            if field == "STUDENT NAME" and self.search_name:
                input_widget.setText(self.search_name)
                input_widget.setReadOnly(True)
            form_layout.addWidget(label, i, 0)
            form_layout.addWidget(input_widget, i, 1)
            self.inputs[field] = input_widget

        scroll_layout.addLayout(form_layout)

        # ---------- TABLE ----------
        table_label = QLabel("VISION DETAILS")
        table_label.setFont(QFont("Arial", 14, QFont.Bold))
        table_label.setAlignment(Qt.AlignCenter)
        scroll_layout.addWidget(table_label)

        self.vision_table = QTableWidget()
        self.vision_table.setRowCount(9)
        self.vision_table.setColumnCount(3)
        self.vision_table.setHorizontalHeaderLabels(["VISION", "LEFT EYE", "RIGHT EYE"])

        # equal width columns + colored header
        self.vision_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.vision_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #a5c9ff;
                color: black;
                font-weight: bold;
                font-size: 13px;
                border: 1px solid lightgray;
                padding: 4px;
            }
        """)

        # allow internal scrolling when needed and hide the vertical header
        self.vision_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.vision_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.vision_table.verticalHeader().setVisible(False)

        vision_labels = [
            "UNAIDED", "AIDED", "DRY REFRACTION", "CYCLOPLEGIC REFRACTION",
            "GLASSES", "ANT. SEGMENT", "FUNDUS", "COLOR VISION", "I/O"
        ]
        for i, label in enumerate(vision_labels):
            vision_item = QTableWidgetItem(label)
            vision_item.setFlags(Qt.ItemIsEnabled)
            self.vision_table.setItem(i, 0, vision_item)
            self.vision_table.setItem(i, 1, QTableWidgetItem(""))
            self.vision_table.setItem(i, 2, QTableWidgetItem(""))

        # Try to size the table so multiple rows are visible (prevents outer scroll area showing only one row)
        try:
            default_row_h = self.vision_table.verticalHeader().defaultSectionSize()
            header_h = self.vision_table.horizontalHeader().height()
            total_h = header_h + default_row_h * self.vision_table.rowCount() + 4
            # set a reasonable maximum so it doesn't grow beyond the window
            max_h = 300
            self.vision_table.setFixedHeight(min(total_h, max_h))
        except Exception:
            pass

        scroll_layout.addWidget(self.vision_table)

        # ---------- SUBMIT BUTTON ----------
        submit_btn = QPushButton("SUBMIT")
        submit_btn.setStyleSheet("""
            QPushButton {
                background: white;
                border-radius: 8px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover { background: lightgray; }
        """)
        submit_btn.clicked.connect(self.submit_form)
        scroll_layout.addWidget(submit_btn, alignment=Qt.AlignCenter)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

    # ---------- Navigation ----------
    def go_to_main_menu(self):
        if self.parent_window:
            self.parent_window.show()  # ✅ show previous window again
        self.close()

    # ---------- Database ----------
    def get_connection(self):
        try:
            return mysql.connector.connect(
                host="localhost", user="root", password="deens", database=self.db_name
            )
        except Error:
            QMessageBox.critical(self, "Error", "Database connection failed.")
            return None

    def create_table_if_not_exists(self):
        conn = self.get_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS opthalmic_details (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    UHID VARCHAR(250),
                    STUDENT_NAME VARCHAR(250),
                    HEAD_POSTURE VARCHAR(250),
                    CORNEAL VARCHAR(250),
                    COVER_TEST VARCHAR(250),
                    EXTERNAL_OCULAR_MOVEMENT VARCHAR(250),
                    CONVERGENCE VARCHAR(250),
                    EYE_COMPLAINTS VARCHAR(250),
                    DOCTOR_NAME VARCHAR(250),
                    DATE_OF_CHECKUP DATE
                )
            """)
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def submit_form(self):
        data = {}
        for key, widget in self.inputs.items():
            if isinstance(widget, QDateEdit):
                data[key] = widget.date().toString("yyyy-MM-dd")
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
            query = f"INSERT INTO opthalmic_details ({columns}) VALUES ({placeholders})"
            cursor.execute(query, list(data.values()))
            conn.commit()
            QMessageBox.information(self, "Success", "Record saved successfully!")
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OpthalmicInfo()
    window.show()
    sys.exit(app.exec_())
