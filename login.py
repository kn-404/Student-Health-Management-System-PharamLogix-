import sys
import os
import subprocess
import mysql.connector
from mysql.connector import errorcode
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QUrl
from PyQt5.QtGui import QFont, QPixmap, QPainter, QDesktopServices
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QStackedWidget
)

# === Paths to assets ===
LOGO_PATH = r"C:\Users\Student\Downloads\L.png"


# ---------- Database Setup ----------
def initialize_database():
    """Ensures that the MySQL database and required tables exist."""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="deens"
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS pharmalogix")
        cursor.execute("USE pharmalogix")

        # Create login table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS login (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Insert default admin user if table empty
        cursor.execute("SELECT COUNT(*) FROM login")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO login (username, password) VALUES ('admin', 'admin')")
            print("✅ Default admin user created (username: admin, password: admin)")

        conn.commit()
        conn.close()
        print("✅ Database and tables ready.")
    except mysql.connector.Error as err:
        print(f"❌ Database setup failed: {err}")
        sys.exit(1)


def get_db_connection():
    """Return a connection to the pharmalogix database."""
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="deens",
        database="pharmalogix"
    )


# ---------- Animated Button ----------
class AnimatedButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.clicked.connect(self._pulse_effect)

    def _pulse_effect(self):
        start = self.geometry()
        bump = start.adjusted(-3, -2, 3, 2)
        anim = QPropertyAnimation(self, b"geometry", self)
        anim.setDuration(120)
        anim.setStartValue(start)
        anim.setEndValue(bump)
        anim.setEasingCurve(QEasingCurve.OutBack)
        anim.finished.connect(lambda: self._restore(start))
        anim.start()

    def _restore(self, start):
        anim = QPropertyAnimation(self, b"geometry", self)
        anim.setDuration(120)
        anim.setStartValue(self.geometry())
        anim.setEndValue(start)
        anim.setEasingCurve(QEasingCurve.InBack)
        anim.start()


# ---------- Base Page ----------
class PageWithLogo(QWidget):
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


# ---------- Login Page ----------
class LoginPage(PageWithLogo):
    def __init__(self, on_login, go_to_signup):
        super().__init__()
        self._on_login = on_login
        self._go_to_signup = go_to_signup
        self._build_ui()

    def _build_ui(self):
        self._add_logo()

        title = QLabel("Login", self)
        title.setFont(QFont("Arial", 32, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        self.username_field = QLineEdit(self)
        self.username_field.setPlaceholderText("Username")
        self.username_field.setFont(QFont("Arial", 18))
        self.username_field.setFixedSize(400, 50)

        self.password_field = QLineEdit(self)
        self.password_field.setPlaceholderText("Password")
        self.password_field.setEchoMode(QLineEdit.Password)
        self.password_field.setFont(QFont("Arial", 18))
        self.password_field.setFixedSize(400, 50)

        forgot = QPushButton("Forgot Password?", self)
        forgot.setFont(QFont("Arial", 12))
        forgot.setFlat(True)
        forgot.clicked.connect(self.open_forgot_link)

        login_btn = AnimatedButton("Login", self)
        login_btn.setFont(QFont("Arial", 14))
        login_btn.setObjectName("login-btn")
        login_btn.clicked.connect(self._handle_login)

        signup_btn = AnimatedButton("Sign Up", self)
        signup_btn.setFont(QFont("Arial", 14))
        signup_btn.clicked.connect(self._go_to_signup)

        self.setStyleSheet("""
            QWidget { background: transparent; }
            QLineEdit {
                background: white; border: 2px solid gray;
                border-radius: 25px; padding-left: 20px; font-size: 18px;
            }
            QLineEdit:focus { border-color: #555; }
            QPushButton {
                background: transparent; border: none; color: black;
            }
            QPushButton#login-btn {
                background-color: #27ae60; border: 2px solid white;
                border-radius: 25px; padding: 8px 25px; color: white;
            }
            QPushButton#login-btn:pressed {
                background-color: #1e8449;
            }
        """)

        form = QVBoxLayout()
        form.setAlignment(Qt.AlignCenter)
        form.addWidget(title)
        form.addSpacing(40)
        form.addWidget(self.username_field, alignment=Qt.AlignCenter)
        form.addSpacing(20)
        form.addWidget(self.password_field, alignment=Qt.AlignCenter)
        form.addSpacing(10)
        form.addWidget(forgot, alignment=Qt.AlignCenter)
        form.addSpacing(15)
        form.addWidget(login_btn, alignment=Qt.AlignCenter)

        top = QHBoxLayout()
        top.addStretch()
        top.addWidget(signup_btn)
        top.setContentsMargins(0, 0, 20, 0)

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addStretch()
        layout.addLayout(form)
        layout.addStretch()

    def _handle_login(self):
        user = self.username_field.text().strip()
        pwd = self.password_field.text().strip()

        if not user or not pwd:
            QMessageBox.warning(self, "Input Error", "Username and password cannot be empty.")
            return

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM login WHERE username=%s AND password=%s", (user, pwd))
            row = cur.fetchone()
            conn.close()

            if row:
                # ✅ Launch main_menu.py using the same Python executable and absolute path
                try:
                    main_menu_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main_menu.py")
                    launch_kwargs = {}
                    # On Windows, suppress the console window so no cmd pops up
                    if os.name == 'nt':
                        # CREATE_NO_WINDOW prevents a console window from appearing
                        launch_kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
                    subprocess.Popen([sys.executable, main_menu_path], cwd=os.path.dirname(main_menu_path), **launch_kwargs)
                except Exception as e:
                    QMessageBox.critical(self, "Launch Error", f"Failed to launch main_menu.py:\n{e}")
                else:
                    QApplication.quit()
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid username or password.")
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))

    def open_forgot_link(self):
        """Open external help page for forgotten passwords."""
        try:
            url = QUrl("https://www.wikihow.com/Remember-a-Forgotten-Password")
            QDesktopServices.openUrl(url)
        except Exception:
            QMessageBox.warning(self, "Open Link", "Unable to open the help link in your browser.")


# ---------- Signup Page ----------
class SignupPage(PageWithLogo):
    def __init__(self, go_back):
        super().__init__()
        self._go_back = go_back
        self._build_ui()

    def _build_ui(self):
        self._add_logo()

        title = QLabel("SIGN UP", self)
        title.setFont(QFont("Arial", 32, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        self.username_field = QLineEdit(self)
        self.username_field.setPlaceholderText("Username")

        self.password_field = QLineEdit(self)
        self.password_field.setPlaceholderText("Password")
        self.password_field.setEchoMode(QLineEdit.Password)

        for field in (self.username_field, self.password_field):
            field.setFont(QFont("Arial", 18))
            field.setFixedSize(400, 50)

        signup_btn = AnimatedButton("Sign Up", self)
        signup_btn.setFont(QFont("Arial", 14))
        signup_btn.setObjectName("signup-btn")
        signup_btn.clicked.connect(self._handle_signup)

        back_btn = AnimatedButton("Back to Login", self)
        back_btn.setFont(QFont("Arial", 12))
        back_btn.clicked.connect(self._go_back)

        self.setStyleSheet("""
            QWidget { background: transparent; }
            QLineEdit {
                background: white; border: 2px solid gray;
                border-radius: 25px; padding-left: 20px; font-size: 18px;
            }
            QPushButton {
                background: transparent; border: none; color: black;
            }
            QPushButton#signup-btn {
                background-color: #27ae60; border: 2px solid white;
                border-radius: 25px; padding: 8px 25px; color: white;
            }
            QPushButton#signup-btn:pressed {
                background-color: #1e8449;
            }
        """)

        form = QVBoxLayout()
        form.setAlignment(Qt.AlignCenter)
        form.addWidget(title)
        form.addSpacing(40)
        form.addWidget(self.username_field, alignment=Qt.AlignCenter)
        form.addSpacing(20)
        form.addWidget(self.password_field, alignment=Qt.AlignCenter)
        form.addSpacing(30)
        form.addWidget(signup_btn, alignment=Qt.AlignCenter)
        form.addSpacing(10)
        form.addWidget(back_btn, alignment=Qt.AlignCenter)

        layout = QVBoxLayout(self)
        layout.addStretch()
        layout.addLayout(form)
        layout.addStretch()

    def _handle_signup(self):
        user = self.username_field.text().strip()
        pwd = self.password_field.text().strip()

        if not user or not pwd:
            QMessageBox.warning(self, "Input Error", "Username and password cannot be empty.")
            return

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM login WHERE username = %s", (user,))
            if cur.fetchone():
                conn.close()
                QMessageBox.warning(self, "Error", "Username already exists.")
                return

            cur.execute("INSERT INTO login (username, password) VALUES (%s, %s)", (user, pwd))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Success", "Registration successful. You can now login.")
            self._go_back()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Database Error", f"MySQL said:\n{err}")
        except Exception as e:
            QMessageBox.critical(self, "Unexpected Error", str(e))


# ---------- App Controller ----------
class App(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.setAutoFillBackground(True)
        from background_utils import set_background
        set_background(self)
        
        login = LoginPage(on_login=self.show_success, go_to_signup=lambda: self.setCurrentIndex(1))
        signup = SignupPage(go_back=lambda: self.setCurrentIndex(0))
        self.addWidget(login)
        self.addWidget(signup)
        self.setFixedSize(800, 500)
        self.setCurrentIndex(0)

    def show_success(self):
        pass  # not needed since login directly opens main_menu.py


# ---------- Run App ----------
if __name__ == "__main__":
    initialize_database()
    app = QApplication(sys.argv)
    window = App()
    window.setWindowTitle("Pharma Logix - Login & Signup")
    window.show()
    sys.exit(app.exec_())
