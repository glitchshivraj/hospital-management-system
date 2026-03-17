from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "hospital_secret_key_2024"

DATABASE = "hospital.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ─────────────────────────────
# CREATE DATABASE TABLES
# ─────────────────────────────
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS patients(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        date_of_birth TEXT,
        gender TEXT,
        phone TEXT,
        email TEXT,
        address TEXT,
        blood_group TEXT,
        emergency_contact TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS doctors(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        specialization TEXT,
        phone TEXT,
        email TEXT,
        experience_years INTEGER,
        qualification TEXT,
        availability TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS appointments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        doctor_id INTEGER,
        appointment_date TEXT,
        appointment_time TEXT,
        reason TEXT,
        notes TEXT,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


init_db()


# ─────────────────────────────
# HOME
# ─────────────────────────────
@app.route("/")
def index():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM patients")
    patients_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM doctors")
    doctors_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM appointments")
    appointments_count = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM appointments
        WHERE appointment_date >= DATE('now') AND status='Scheduled'
    """)
    upcoming_count = cur.fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        patients_count=patients_count,
        doctors_count=doctors_count,
        appointments_count=appointments_count,
        upcoming_count=upcoming_count
    )


# ─────────────────────────────
# PATIENTS
# ─────────────────────────────
@app.route("/patients")
def patients():
    conn = get_db_connection()
    patients = conn.execute(
        "SELECT * FROM patients ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return render_template("patients.html", patients=patients)


@app.route("/patients/add", methods=["GET", "POST"])
def add_patient():

    if request.method == "POST":

        data = (
            request.form["first_name"],
            request.form["last_name"],
            request.form["dob"],
            request.form["gender"],
            request.form["phone"],
            request.form["email"],
            request.form["address"],
            request.form["blood_group"],
            request.form["emergency_contact"]
        )

        conn = get_db_connection()
        conn.execute("""
        INSERT INTO patients
        (first_name,last_name,date_of_birth,gender,phone,email,address,blood_group,emergency_contact)
        VALUES (?,?,?,?,?,?,?,?,?)
        """, data)

        conn.commit()
        conn.close()

        flash("Patient added successfully", "success")
        return redirect(url_for("patients"))

    return render_template("add_patient.html")


@app.route("/patients/delete/<int:id>", methods=["POST"])
def delete_patient(id):

    conn = get_db_connection()

    conn.execute("DELETE FROM appointments WHERE patient_id=?", (id,))
    conn.execute("DELETE FROM patients WHERE id=?", (id,))

    conn.commit()
    conn.close()

    flash("Patient deleted", "info")
    return redirect(url_for("patients"))


# ─────────────────────────────
# DOCTORS
# ─────────────────────────────
@app.route("/doctors")
def doctors():
    conn = get_db_connection()
    doctors = conn.execute(
        "SELECT * FROM doctors ORDER BY created_at DESC"
    ).fetchall()
    conn.close()

    return render_template("doctors.html", doctors=doctors)


@app.route("/doctors/add", methods=["GET", "POST"])
def add_doctor():

    if request.method == "POST":

        data = (
            request.form["first_name"],
            request.form["last_name"],
            request.form["specialization"],
            request.form["phone"],
            request.form["email"],
            request.form["experience"],
            request.form["qualification"],
            request.form["availability"]
        )

        conn = get_db_connection()

        conn.execute("""
        INSERT INTO doctors
        (first_name,last_name,specialization,phone,email,experience_years,qualification,availability)
        VALUES (?,?,?,?,?,?,?,?)
        """, data)

        conn.commit()
        conn.close()

        flash("Doctor added successfully", "success")
        return redirect(url_for("doctors"))

    return render_template("add_doctor.html")


# ─────────────────────────────
# APPOINTMENTS
# ─────────────────────────────
@app.route("/appointments")
def appointments():

    conn = get_db_connection()

    appointments = conn.execute("""
        SELECT a.*,
               p.first_name AS pat_first,
               p.last_name AS pat_last,
               d.first_name AS doc_first,
               d.last_name AS doc_last,
               d.specialization
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors d ON a.doctor_id = d.id
        ORDER BY appointment_date DESC
    """).fetchall()

    conn.close()

    return render_template("appointments.html", appointments=appointments)


@app.route("/appointments/book", methods=["GET", "POST"])
def book_appointment():

    conn = get_db_connection()

    if request.method == "POST":

        data = (
            request.form["patient_id"],
            request.form["doctor_id"],
            request.form["appointment_date"],
            request.form["appointment_time"],
            request.form["reason"],
            request.form["notes"],
            "Scheduled"
        )

        conn.execute("""
        INSERT INTO appointments
        (patient_id,doctor_id,appointment_date,appointment_time,reason,notes,status)
        VALUES (?,?,?,?,?,?,?)
        """, data)

        conn.commit()

        flash("Appointment booked successfully", "success")

        return redirect(url_for("appointments"))

    patients = conn.execute(
        "SELECT id,first_name,last_name FROM patients"
    ).fetchall()

    doctors = conn.execute(
        "SELECT id,first_name,last_name,specialization FROM doctors"
    ).fetchall()

    conn.close()

    return render_template(
        "book_appointment.html",
        patients=patients,
        doctors=doctors
    )


# ─────────────────────────────
# API
# ─────────────────────────────
@app.route("/api/appointment/<int:id>/status", methods=["POST"])
def update_status(id):

    data = request.get_json()

    conn = get_db_connection()

    conn.execute(
        "UPDATE appointments SET status=? WHERE id=?",
        (data["status"], id)
    )

    conn.commit()
    conn.close()

    return jsonify({"success": True})


# ─────────────────────────────
# RUN
# ─────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)