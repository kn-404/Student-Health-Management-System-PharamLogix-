import sys
import os
import mysql.connector
from mysql.connector import Error
import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton,
    QMessageBox, QHBoxLayout, QFileDialog
)
from PyQt5.QtGui import QFont, QPalette, QBrush, QPixmap
from PyQt5.QtCore import Qt
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
except ImportError:
    print("Missing required Python package: reportlab")
    print("Install it with:")
    print(f"{sys.executable} -m pip install reportlab")
    # Exit early so the script doesn't raise ModuleNotFoundError later
    sys.exit(1)


class ReportPage(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent_window = parent
        self.setWindowTitle("Generate Student Health Report")
        # make window a bit larger so dropdown and buttons are comfortable
        self.setFixedSize(600, 150)
        
        from background_utils import set_background
        set_background(self)
        
        self.init_ui()
        self.load_students()
    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Generate Student Health Report")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        self.student_dropdown = QComboBox()
        self.student_dropdown.setPlaceholderText("Select Student")

        generate_btn = QPushButton("Generate Report")
        generate_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        generate_btn.clicked.connect(self.generate_report)

        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self.go_back)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(generate_btn)
        btn_layout.addWidget(back_btn)

        layout.addWidget(title)
        layout.addWidget(self.student_dropdown)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def go_back(self):
        if self.parent_window:
            self.parent_window.show()
        self.close()

    def connect_db(self):
        try:
            return mysql.connector.connect(
                host="localhost",
                user="root",
                password="deens",
                database="pharmalogix"
            )
        except Error as e:
            QMessageBox.critical(self, "Database Error", str(e))
            return None

    def load_students(self):
        conn = self.connect_db()
        if not conn:
            return
        # Collect distinct student names from any of the known tables (skip missing tables)
        tables = ["physical_details", "pediatric_details", "general_checkup_details", "dental_details", "opthalmic_details", "vaccination_details"]
        names_set = set()
        cursor = None
        try:
            cursor = conn.cursor()
            for table in tables:
                try:
                    cursor.execute(f"SELECT DISTINCT STUDENT_NAME FROM {table}")
                    rows = [row[0] for row in cursor.fetchall() if row and row[0]]
                    for n in rows:
                        names_set.add(n)
                except Error:
                    # table missing or other DB error for this table — skip it
                    continue
        except Error as e:
            QMessageBox.critical(self, "Database Error", str(e))
        finally:
            try:
                if cursor:
                    cursor.close()
            except Exception:
                pass
            conn.close()

        if names_set:
            names_list = sorted(names_set)
            self.student_dropdown.addItems(names_list)
        # else: leave dropdown empty; user will be prompted if they try to generate a report

    def generate_report(self):
        student_name = self.student_dropdown.currentText()
        if not student_name:
            QMessageBox.warning(self, "No Student", "Please select a student.")
            return

        conn = self.connect_db()
        if not conn:
            return

        cursor = None
        report_data = {}
        try:
            cursor = conn.cursor(dictionary=True)
            # ✅ Fetch from different tables
            tables = ["physical_details", "pediatric_details", "general_checkup_details", "dental_details", "opthalmic_details", "vaccination_details"]
            for table in tables:
                try:
                    cursor.execute(f"SELECT * FROM {table} WHERE STUDENT_NAME = %s", (student_name,))
                    result = cursor.fetchone()
                    report_data[table] = result if result else {}
                except Error:
                    # missing table or query error - skip this table
                    report_data[table] = {}
        except Error as e:
            QMessageBox.critical(self, "Database Error", str(e))
        finally:
            try:
                if cursor:
                    cursor.close()
            except Exception:
                pass
            conn.close()

        # ✅ Choose save location and create PDF
        default_name = f"{student_name.replace(' ', '_')}_Health_Report.pdf"
        default_path = os.path.join(os.getcwd(), default_name)
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Report As", default_path, "PDF Files (*.pdf)")
        if not save_path:
            # User cancelled save dialog
            return
        # ensure .pdf extension
        if not save_path.lower().endswith('.pdf'):
            save_path += '.pdf'
        pdf = SimpleDocTemplate(save_path, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph(f"<b>STUDENT HEALTH RECORD</b>", styles['Title']))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"<b>STUDENT NAME:</b> {student_name}", styles['Normal']))
        elements.append(Spacer(1, 12))

        # ✅ Physical Checkup
        physical = report_data.get("physical_details", {})
        if physical:
            elements.append(Paragraph("<b>Physical Checkup</b>", styles['Heading2']))
            # add header row
            def _fmt(v):
                if v is None:
                    return ""
                if isinstance(v, bytes):
                    try:
                        return v.decode('utf-8')
                    except Exception:
                        return str(v)
                if isinstance(v, (datetime.date, datetime.datetime)):
                    return v.isoformat()
                return str(v)

            data = [["Field", "Value"]]
            for k, v in physical.items():
                if k and k.lower() in ("id", "student_name"):
                    continue
                data.append([k.replace('_', ' ').title(), _fmt(v)])
            table = Table(data, colWidths=[200, 200])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
            elements.append(Spacer(1, 12))

        # ✅ Pediatric Details
        pediatric = report_data.get("pediatric_details", {})
        if pediatric:
            elements.append(Paragraph("<b>Pediatric Checkup</b>", styles['Heading2']))
            data = [["Field", "Value"]]
            for k, v in pediatric.items():
                if k and k.lower() in ("id", "student_name"):
                    continue
                data.append([k.replace('_', ' ').title(), _fmt(v)])
            table = Table(data, colWidths=[200, 200])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
            elements.append(Spacer(1, 12))

        # ✅ General Checkup Details
        general = report_data.get("general_checkup_details", {})
        
        if general:
            elements.append(Paragraph("<b>General Checkup</b>", styles['Heading2']))
            data = [["Field", "Value"]]
            for k, v in general.items():
                if k and k.lower() in ("id", "student_name"):
                    continue
                data.append([k.replace('_', ' ').title(), _fmt(v)])
            table = Table(data, colWidths=[200, 200])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
            elements.append(Spacer(1, 12))
        # ✅ Dental Details
        dental = report_data.get("dental_details", {})
        if dental:
            elements.append(Paragraph("<b>Dental Checkup</b>", styles['Heading2']))
            data = [["Field", "Value"]]
            for k, v in dental.items():
                if k and k.lower() in ("id", "student_name"):
                    continue
                data.append([k.replace('_', ' ').title(), _fmt(v)])
            table = Table(data, colWidths=[200, 200])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
            elements.append(Spacer(1, 12))
        # ✅ Ophthalmic Details
        opthalmic = report_data.get("opthalmic_details", {})
        
        if opthalmic:
            elements.append(Paragraph("<b>Opthalmic Checkup</b>", styles['Heading2']))
            data = [["Field", "Value"]]
            for k, v in opthalmic.items():
                if k and k.lower() in ("id", "student_name"):
                    continue
                data.append([k.replace('_', ' ').title(), _fmt(v)])
            table = Table(data, colWidths=[200, 200])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
            elements.append(Spacer(1, 12))
        # ✅ Vaccination Details
        vacc = report_data.get("vaccination_details", {})
        if vacc:
            elements.append(Paragraph("<b>Vaccination Details</b>", styles['Heading2']))
            data = [["Field", "Value"]]
            for k, v in vacc.items():
                if k and k.lower() in ("id", "student_name"):
                    continue
                data.append([k.replace('_', ' ').title(), _fmt(v)])
            table = Table(data, colWidths=[200, 200])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
            elements.append(Spacer(1, 12))
        

        try:
            pdf.build(elements)
            QMessageBox.information(self, "Success", f"Report generated:\n{save_path}")
        except Exception as e:
            QMessageBox.critical(self, "PDF Error", f"Failed to generate PDF:\n{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ReportPage()
    window.show()
    sys.exit(app.exec_())
