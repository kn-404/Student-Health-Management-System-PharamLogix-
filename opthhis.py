import sys
import os
import subprocess
import mysql.connector
from mysql.connector import Error
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QScrollArea, QFrame, QMessageBox, QLabel, QHBoxLayout, QHeaderView
)
from PyQt5.QtGui import QFont, QPalette, QBrush, QPixmap
from PyQt5.QtCore import Qt


class OpthalmicHistory(QWidget):
    def __init__(self, search_name=None, parent=None):
        super().__init__()
        self.parent_window = parent  # ✅ store reference
        self.search_name = search_name
        self.setWindowTitle("PharmaLogix - Opthalmic History")
        self.setFixedSize(800, 500)
        self.search_name = search_name  # store search term

        from background_utils import set_background
        set_background(self)

        self.init_ui()
        self.load_data_from_db()

    def init_ui(self):

        layout = QVBoxLayout(self)

        # Top layout with title and back button
        top_layout = QHBoxLayout()
        title = QLabel("OPTHALMIC HISTORY")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(title)
        top_layout.addStretch()

        back_btn = QPushButton("BACK")
        back_btn.setStyleSheet("""
            QPushButton {
                background: white;
                border-radius: 10px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: lightgray;
            }
        """)
        back_btn.clicked.connect(self.go_back)
        top_layout.addWidget(back_btn)
        layout.addLayout(top_layout)

        # === Scroll area for data ===
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)




    # --------- MySQL Data Fetch ----------
    def load_data_from_db(self):
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",        # update if needed
                password="deens",        # update if you have a MySQL password
                database="pharmalogix"
            )
            cursor = conn.cursor()

            if self.search_name:  # search by student name
                query = "SELECT * FROM opthalmic_details WHERE student_name = %s"
                cursor.execute(query, (self.search_name,))
            else:  # fetch all records
                cursor.execute("SELECT * FROM opthalmic_details")

            data = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

            if not data:
                QMessageBox.information(self, "No Data", 
                                        "No opthalmic records found for this student.")
                return

            # === Build Record Blocks ===
            for row_idx, row_data in enumerate(data):
                record_frame = QFrame()
                record_frame.setStyleSheet("""
                    QFrame {
                        background-color: rgba(255,255,255,0.9);
                        border-radius: 10px;
                        border: 1px solid gray;
                        padding: 12px;
                        margin-bottom: 15px;
                    }
                """)
                record_layout = QVBoxLayout(record_frame)

                for col_name, value in zip(columns, row_data):
                    row_layout = QHBoxLayout()

                    # Column name
                    label_key = QLabel(f"{col_name.replace('_', ' ').upper()}:")
                    label_key.setFont(QFont("Arial", 11, QFont.Bold))
                    label_key.setFixedWidth(200)

                    # Column value
                    label_value = QLabel(str(value))
                    label_value.setFont(QFont("Arial", 11))
                    label_value.setStyleSheet("color: #222;")

                    row_layout.addWidget(label_key)
                    row_layout.addWidget(label_value)
                    row_layout.addStretch()
                    record_layout.addLayout(row_layout)

                # Add each record block to scroll layout
                self.scroll_layout.addWidget(record_frame)

            

        except Error as e:
            QMessageBox.critical(self, "Database Error", f"Error while fetching data:\n{e}")

        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    # ---------- Go to Main Menu ----------
    def go_back(self):
        if self.parent_window:
            self.parent_window.show()  # ✅ show previous window again
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Example usage: pass a name to search
    search_name = None  # set to a string like "John Doe" to filter
    window = OpthalmicHistory(search_name)
    
    window.show()
    sys.exit(app.exec_())
