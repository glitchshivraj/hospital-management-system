# 🏥 MediCare — Hospital Management System

A full-featured Hospital Management System built with **Flask** and **MySQL**.

## Features
- **Patient Registry** — Register, view, edit, and delete patients with full medical details
- **Doctor Management** — Manage doctors with specialization, qualifications, and availability
- **Appointment Booking** — Book, edit, and cancel appointments with real-time status updates
- **Dashboard** — Live stats overview (total patients, doctors, appointments, upcoming today)

---

## Tech Stack
| Layer    | Technology        |
|----------|-------------------|
| Backend  | Python / Flask    |
| Database | MySQL             |
| ORM      | Flask-MySQLdb     |
| Frontend | Jinja2 + Vanilla JS |

---

## Setup Instructions

### 1. Prerequisites
- Python 3.9+
- MySQL 8.0+
- pip

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up the database
Log in to MySQL and run the schema:
```bash
mysql -u root -p < schema.sql
```
This creates the `hospital_db` database, all tables, and inserts sample data.

### 4. Configure environment variables (optional)
```bash
export MYSQL_HOST=localhost
export MYSQL_USER=root
export MYSQL_PASSWORD=your_password
export MYSQL_DB=hospital_db
```
Or edit `app.py` directly with your credentials.

### 5. Run the application
```bash
python app.py
```
Visit **http://localhost:5000** in your browser.

---

## Project Structure
```
hospital_mgmt/
├── app.py               # Flask routes & business logic
├── schema.sql           # MySQL schema + sample data
├── requirements.txt     # Python dependencies
└── templates/
    ├── base.html        # Shared layout & navigation
    ├── index.html       # Dashboard
    ├── patients.html    # Patient list
    ├── add_patient.html
    ├── edit_patient.html
    ├── view_patient.html
    ├── doctors.html     # Doctor list
    ├── add_doctor.html
    ├── edit_doctor.html
    ├── view_doctor.html
    ├── appointments.html
    ├── book_appointment.html
    └── edit_appointment.html
```

---

## API Endpoint
`POST /api/appointment/<id>/status` — Update appointment status via AJAX (used for inline status dropdown on appointments page).

---

## Sample Data
The schema includes:
- **5 doctors** across Cardiology, Neurology, Pediatrics, Orthopedics, and Dermatology
- **5 patients** with realistic Indian patient data
- **5 appointments** — some upcoming, one completed

---

## Screenshots
The UI features a dark navy sidebar, elegant typography (Playfair Display + DM Sans), and a clean medical dashboard aesthetic.
