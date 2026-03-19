from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
import sqlite3
import os
 
app = Flask(__name__)
app.secret_key = "ms_hospital_secret_2024"
 
DATABASE = os.environ.get("DATABASE_PATH", "hospital.db")
 
 
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
 
 
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS patients(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT, last_name TEXT,
        date_of_birth TEXT, gender TEXT,
        phone TEXT, email TEXT, address TEXT,
        blood_group TEXT, emergency_contact TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS doctors(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT, last_name TEXT,
        specialization TEXT, phone TEXT, email TEXT,
        experience_years INTEGER, qualification TEXT,
        availability TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS appointments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER, doctor_id INTEGER,
        appointment_date TEXT, appointment_time TEXT,
        reason TEXT, notes TEXT, status TEXT DEFAULT 'Scheduled',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS bills(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        services TEXT, amount REAL,
        bill_date TEXT, status TEXT DEFAULT 'Unpaid',
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit()
    conn.close()
 
 
init_db()
 
 
# ─────────────────────────────
# DASHBOARD
# ─────────────────────────────
@app.route("/")
def index():
    conn = get_db_connection()
    patients_count      = conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
    doctors_count       = conn.execute("SELECT COUNT(*) FROM doctors").fetchone()[0]
    appointments_count  = conn.execute("SELECT COUNT(*) FROM appointments").fetchone()[0]
    bills_count         = conn.execute("SELECT COUNT(*) FROM bills").fetchone()[0]
    recent_appointments = conn.execute("""
        SELECT a.*, p.first_name AS pat_first, p.last_name AS pat_last,
               d.first_name AS doc_first, d.last_name AS doc_last
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors  d ON a.doctor_id  = d.id
        ORDER BY a.created_at DESC LIMIT 5
    """).fetchall()
    conn.close()
    return render_template("index.html",
        patients_count=patients_count, doctors_count=doctors_count,
        appointments_count=appointments_count, bills_count=bills_count,
        recent_appointments=recent_appointments)
 
 
# ─────────────────────────────
# PATIENTS
# ─────────────────────────────
@app.route("/patients")
def patients():
    conn = get_db_connection()
    patients = conn.execute("SELECT * FROM patients ORDER BY created_at DESC").fetchall()
    conn.close()
    return render_template("patients.html", patients=patients)
 
 
@app.route("/patients/add", methods=["GET", "POST"])
def add_patient():
    if request.method == "POST":
        conn = get_db_connection()
        conn.execute("""
        INSERT INTO patients
        (first_name,last_name,date_of_birth,gender,phone,email,address,blood_group,emergency_contact)
        VALUES (?,?,?,?,?,?,?,?,?)
        """, (request.form["first_name"], request.form["last_name"],
              request.form["dob"], request.form["gender"],
              request.form["phone"], request.form["email"],
              request.form["address"], request.form["blood_group"],
              request.form["emergency_contact"]))
        conn.commit(); conn.close()
        flash("Patient registered successfully!", "success")
        return redirect(url_for("patients"))
    return render_template("add_patient.html")
 
 
@app.route("/patients/<int:id>")
def view_patient(id):
    conn = get_db_connection()
    patient = conn.execute("SELECT * FROM patients WHERE id=?", (id,)).fetchone()
    appointments = conn.execute("""
        SELECT a.*, d.first_name AS doc_first, d.last_name AS doc_last, d.specialization
        FROM appointments a JOIN doctors d ON a.doctor_id=d.id
        WHERE a.patient_id=? ORDER BY a.appointment_date DESC
    """, (id,)).fetchall()
    bills = conn.execute("SELECT * FROM bills WHERE patient_id=? ORDER BY bill_date DESC", (id,)).fetchall()
    conn.close()
    return render_template("view_patient.html", patient=patient, appointments=appointments, bills=bills)
 
 
@app.route("/patients/edit/<int:id>", methods=["GET", "POST"])
def edit_patient(id):
    conn = get_db_connection()
    if request.method == "POST":
        conn.execute("""
        UPDATE patients SET first_name=?,last_name=?,date_of_birth=?,gender=?,
        phone=?,email=?,address=?,blood_group=?,emergency_contact=? WHERE id=?
        """, (request.form["first_name"], request.form["last_name"],
              request.form["dob"], request.form["gender"],
              request.form["phone"], request.form["email"],
              request.form["address"], request.form["blood_group"],
              request.form["emergency_contact"], id))
        conn.commit(); conn.close()
        flash("Patient updated!", "success")
        return redirect(url_for("view_patient", id=id))
    patient = conn.execute("SELECT * FROM patients WHERE id=?", (id,)).fetchone()
    conn.close()
    return render_template("edit_patient.html", patient=patient)
 
 
@app.route("/patients/delete/<int:id>", methods=["POST"])
def delete_patient(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM appointments WHERE patient_id=?", (id,))
    conn.execute("DELETE FROM bills WHERE patient_id=?", (id,))
    conn.execute("DELETE FROM patients WHERE id=?", (id,))
    conn.commit(); conn.close()
    flash("Patient deleted.", "info")
    return redirect(url_for("patients"))
 
 
# ─────────────────────────────
# DOCTORS
# ─────────────────────────────
@app.route("/doctors")
def doctors():
    conn = get_db_connection()
    doctors = conn.execute("SELECT * FROM doctors ORDER BY created_at DESC").fetchall()
    conn.close()
    return render_template("doctors.html", doctors=doctors)
 
 
@app.route("/doctors/add", methods=["GET", "POST"])
def add_doctor():
    if request.method == "POST":
        conn = get_db_connection()
        conn.execute("""
        INSERT INTO doctors
        (first_name,last_name,specialization,phone,email,experience_years,qualification,availability)
        VALUES (?,?,?,?,?,?,?,?)
        """, (request.form["first_name"], request.form["last_name"],
              request.form["specialization"], request.form["phone"],
              request.form["email"], request.form["experience"],
              request.form["qualification"], request.form["availability"]))
        conn.commit(); conn.close()
        flash("Doctor added successfully!", "success")
        return redirect(url_for("doctors"))
    return render_template("add_doctor.html")
 
 
@app.route("/doctors/<int:id>")
def view_doctor(id):
    conn = get_db_connection()
    doctor = conn.execute("SELECT * FROM doctors WHERE id=?", (id,)).fetchone()
    appointments = conn.execute("""
        SELECT a.*, p.first_name AS pat_first, p.last_name AS pat_last
        FROM appointments a JOIN patients p ON a.patient_id=p.id
        WHERE a.doctor_id=? ORDER BY a.appointment_date DESC
    """, (id,)).fetchall()
    conn.close()
    return render_template("view_doctor.html", doctor=doctor, appointments=appointments)
 
 
@app.route("/doctors/edit/<int:id>", methods=["GET", "POST"])
def edit_doctor(id):
    conn = get_db_connection()
    if request.method == "POST":
        conn.execute("""
        UPDATE doctors SET first_name=?,last_name=?,specialization=?,phone=?,
        email=?,experience_years=?,qualification=?,availability=? WHERE id=?
        """, (request.form["first_name"], request.form["last_name"],
              request.form["specialization"], request.form["phone"],
              request.form["email"], request.form["experience"],
              request.form["qualification"], request.form["availability"], id))
        conn.commit(); conn.close()
        flash("Doctor updated!", "success")
        return redirect(url_for("view_doctor", id=id))
    doctor = conn.execute("SELECT * FROM doctors WHERE id=?", (id,)).fetchone()
    conn.close()
    return render_template("edit_doctor.html", doctor=doctor)
 
 
@app.route("/doctors/delete/<int:id>", methods=["POST"])
def delete_doctor(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM appointments WHERE doctor_id=?", (id,))
    conn.execute("DELETE FROM doctors WHERE id=?", (id,))
    conn.commit(); conn.close()
    flash("Doctor removed.", "info")
    return redirect(url_for("doctors"))
 
 
# ─────────────────────────────
# APPOINTMENTS
# ─────────────────────────────
@app.route("/appointments")
def appointments():
    conn = get_db_connection()
    appointments = conn.execute("""
        SELECT a.*, p.first_name AS pat_first, p.last_name AS pat_last,
               d.first_name AS doc_first, d.last_name AS doc_last, d.specialization
        FROM appointments a
        JOIN patients p ON a.patient_id=p.id
        JOIN doctors  d ON a.doctor_id=d.id
        ORDER BY a.appointment_date DESC, a.appointment_time DESC
    """).fetchall()
    conn.close()
    return render_template("appointments.html", appointments=appointments)
 
 
@app.route("/appointments/book", methods=["GET", "POST"])
def book_appointment():
    conn = get_db_connection()
    if request.method == "POST":
        conn.execute("""
        INSERT INTO appointments
        (patient_id,doctor_id,appointment_date,appointment_time,reason,notes,status)
        VALUES (?,?,?,?,?,?,'Scheduled')
        """, (request.form["patient_id"], request.form["doctor_id"],
              request.form["appointment_date"], request.form["appointment_time"],
              request.form["reason"], request.form["notes"]))
        conn.commit(); conn.close()
        flash("Appointment booked!", "success")
        return redirect(url_for("appointments"))
    patients = conn.execute("SELECT id,first_name,last_name FROM patients ORDER BY first_name").fetchall()
    doctors  = conn.execute("SELECT id,first_name,last_name,specialization FROM doctors ORDER BY first_name").fetchall()
    conn.close()
    return render_template("book_appointment.html", patients=patients, doctors=doctors)
 
 
@app.route("/appointments/edit/<int:id>", methods=["GET", "POST"])
def edit_appointment(id):
    conn = get_db_connection()
    if request.method == "POST":
        conn.execute("""
        UPDATE appointments SET appointment_date=?,appointment_time=?,reason=?,notes=?,status=?
        WHERE id=?
        """, (request.form["appointment_date"], request.form["appointment_time"],
              request.form["reason"], request.form["notes"],
              request.form["status"], id))
        conn.commit(); conn.close()
        flash("Appointment updated!", "success")
        return redirect(url_for("appointments"))
    appointment = conn.execute("""
        SELECT a.*, p.first_name AS pat_first, p.last_name AS pat_last,
               d.first_name AS doc_first, d.last_name AS doc_last
        FROM appointments a
        JOIN patients p ON a.patient_id=p.id
        JOIN doctors  d ON a.doctor_id=d.id
        WHERE a.id=?
    """, (id,)).fetchone()
    conn.close()
    return render_template("edit_appointment.html", appointment=appointment)
 
 
@app.route("/appointments/delete/<int:id>", methods=["POST"])
def delete_appointment(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM appointments WHERE id=?", (id,))
    conn.commit(); conn.close()
    flash("Appointment cancelled.", "info")
    return redirect(url_for("appointments"))
 
 
@app.route("/api/appointment/<int:id>/status", methods=["POST"])
def update_status(id):
    data = request.get_json()
    conn = get_db_connection()
    conn.execute("UPDATE appointments SET status=? WHERE id=?", (data["status"], id))
    conn.commit(); conn.close()
    return jsonify({"success": True})
 
 
# ─────────────────────────────
# BILLING
# ─────────────────────────────
@app.route("/billing")
def billing():
    conn = get_db_connection()
    bills = conn.execute("""
        SELECT b.*, p.first_name AS pat_first, p.last_name AS pat_last
        FROM bills b JOIN patients p ON b.patient_id=p.id
        ORDER BY b.created_at DESC
    """).fetchall()
    conn.close()
    return render_template("billing.html", bills=bills)
 
 
@app.route("/billing/add", methods=["GET", "POST"])
def add_bill():
    conn = get_db_connection()
    if request.method == "POST":
        conn.execute("""
        INSERT INTO bills (patient_id,services,amount,bill_date,status,notes)
        VALUES (?,?,?,?,?,?)
        """, (request.form["patient_id"], request.form["services"],
              request.form["amount"], request.form["bill_date"],
              request.form["status"], request.form["notes"]))
        conn.commit(); conn.close()
        flash("Invoice created!", "success")
        return redirect(url_for("billing"))
    patients = conn.execute("SELECT id,first_name,last_name FROM patients ORDER BY first_name").fetchall()
    conn.close()
    return render_template("add_bill.html", patients=patients)
 
 
@app.route("/billing/<int:id>")
def view_bill(id):
    conn = get_db_connection()
    bill = conn.execute("""
        SELECT b.*, p.first_name AS pat_first, p.last_name AS pat_last
        FROM bills b JOIN patients p ON b.patient_id=p.id WHERE b.id=?
    """, (id,)).fetchone()
    conn.close()
    return render_template("view_bill.html", bill=bill)
 
 
@app.route("/billing/delete/<int:id>", methods=["POST"])
def delete_bill(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM bills WHERE id=?", (id,))
    conn.commit(); conn.close()
    flash("Invoice deleted.", "info")
    return redirect(url_for("billing"))
 
 
@app.route("/billing/mark-paid/<int:id>", methods=["POST"])
def mark_paid(id):
    conn = get_db_connection()
    conn.execute("UPDATE bills SET status='Paid' WHERE id=?", (id,))
    conn.commit(); conn.close()
    flash("Invoice marked as paid!", "success")
    return redirect(url_for("view_bill", id=id))
 
 
# ─────────────────────────────
# REPORTS
# ─────────────────────────────
@app.route("/reports")
def reports():
    conn = get_db_connection()
    total_revenue = conn.execute("SELECT COALESCE(SUM(amount),0) FROM bills").fetchone()[0]
    paid_revenue  = conn.execute("SELECT COALESCE(SUM(amount),0) FROM bills WHERE status='Paid'").fetchone()[0]
    pending_bills = conn.execute("SELECT COUNT(*) FROM bills WHERE status='Unpaid'").fetchone()[0]
    completed_appointments = conn.execute("SELECT COUNT(*) FROM appointments WHERE status='Completed'").fetchone()[0]
    appt_scheduled = conn.execute("SELECT COUNT(*) FROM appointments WHERE status='Scheduled'").fetchone()[0]
    appt_completed = conn.execute("SELECT COUNT(*) FROM appointments WHERE status='Completed'").fetchone()[0]
    appt_cancelled = conn.execute("SELECT COUNT(*) FROM appointments WHERE status='Cancelled'").fetchone()[0]
    appt_noshow    = conn.execute("SELECT COUNT(*) FROM appointments WHERE status='No-Show'").fetchone()[0]
    top_doctors = conn.execute("""
        SELECT d.first_name, d.last_name, d.specialization, COUNT(a.id) AS appt_count
        FROM doctors d LEFT JOIN appointments a ON d.id=a.doctor_id
        GROUP BY d.id ORDER BY appt_count DESC LIMIT 5
    """).fetchall()
    conn.close()
    return render_template("reports.html",
        total_revenue=total_revenue, paid_revenue=paid_revenue,
        pending_bills=pending_bills, completed_appointments=completed_appointments,
        appt_scheduled=appt_scheduled, appt_completed=appt_completed,
        appt_cancelled=appt_cancelled, appt_noshow=appt_noshow,
        top_doctors=top_doctors)
 
 
# ─────────────────────────────
# RUN
# ─────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))