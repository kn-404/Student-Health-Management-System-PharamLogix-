# Student Health Management System (PharmaLogix)

SHMS is a medical record management system built in Python with MySQL for small NGOs or clinics. It provides a visually modern interface (PyQt5) for securely entering, updating, and managing medical data, and automates PDF report generation for students.

## Features

- Intuitive GUI built with PyQt5
- Secure login and student registration
- Store, view, update, and delete medical records (physical, pediatric, dental, ophthalmic, vaccination)
- Automated report generation (PDFs—reportlab)
- MySQL backend for robust data storage
- Prevents data redundancy compared to spreadsheets

## Technologies Used

- Python 3.13
- PyQt5 (user interface)
- mysql-connector-python (database interface)
- MySQL (as backend DB)
- PIL (interface background images)
- subprocess, sys, os (process/file ops)
- reportlab (PDF generation)

## How It Works

1. **Login/Register:** Users authenticate securely.
2. **Main Dashboard:** Add and search student records.
3. **Detailed Windows:** Enter and view medical info for each aspect (physical, pediatric, etc.).
4. **Automated Reports:** Generate comprehensive medical PDFs from database entries.
5. **Database:** All info stored securely in MySQL.

## Prerequisites

- Windows 10+ (x64) recommended
- Python 3.x
- MySQL installed and running (update credentials in code if needed)
- Recommended: 8GB+ RAM

## Setup and Usage

1. Clone the repo and install required Python packages: pip install pyqt5 mysql-connector-python pillow reportlab
2. Ensure MySQL is running, create the required database.
3. Run the login.py file (update credentials if needed).
4. Follow GUI instructions for login, registration, and student data entry.

## Output Example

<img width="1232" height="807" alt="image" src="https://github.com/user-attachments/assets/4d994921-ed85-4453-a1b7-42fac65af7d4" />


## Challenges

Developing the GUI was a huge pain, as Python kept throwing errors and exceptions, so most of the time went into fixing those. Aside from this, the code sometimes broke or didn't work, so logical errors also had to be addressed. Overall, it was quite fun though, and learning how to develop an application was such an interesting experience

## License

MIT © kn-404
