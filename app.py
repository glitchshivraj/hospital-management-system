from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import psycopg2
import psycopg2.extras
import os

app = Flask(__name__)
app.secret_key = "ms_hospital_secret_2024"

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn


def dict_cursor(conn):
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


# ─────────────────────────────
# DASHBOARD
# ─────────────────────────────
@app.route("/")
def index():
    conn = get_db_connection()
    cur = dict_cursor(conn)

    cur.execute("SELECT COUNT(*) AS cnt FROM patients")
    patients_count = cur.fetchone()["cnt"]

    cur.execute("SELECT COUNT(*) AS cnt FROM doctors")
    doctors_count = cur.fetchone()["cnt"]

    cur.execute("SELECT COUNT(*) AS cnt FROM appointments")
    appointments_count = cur.fetchone()["cnt"]

    cur.execute("SELECT COUNT(*) AS cnt FROM bills")
    bills_count = cur.fetchone()["cnt"]

    cur.execute("""
        SELECT a.*, p.first_name AS pat_first, p.last_name AS pat_last,
               d.first_name AS doc_first, d.last_name AS doc_last
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors  d ON a.doctor_id  = d.id
        ORDER BY a.created_at DESC LIMIT 5
    """)
    recent_appointments = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("index.html",
        patients_count=patients_count,
        doctors_count=doctors_count,
        appointments_count=appointments_count,
        bills_count=bills_count,
        recent_appointments=recent_appointments)


# ─────────────────────────────
# PATIENTS
# ─────────────────────────────
@app.route("/patients")
def patients():
    conn = get_db_connection()
    cur = dict_cursor(conn)
    cur.execute("SELECT * FROM patients ORDER BY created_at DESC")
    patients = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("patients.html", patients=patients)


@app.route("/patients/add", methods=["GET", "POST"])
def add_patient():
    if request.method == "POST":
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO patients
            (first_name, last_name, date_of_birth, gender, phone, email,
             address, blood_group, emergency_contact)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            request.form["first_name"], request.form["last_name"],
            request.form["dob"], request.form["gender"],
            request.form["phone"], request.form["email"],
            request.form["address"], request.form["blood_group"],
            request.form["emergency_contact"]
        ))
        conn.commit()
        cur.close()
        conn.close()
        flash("Patient registered successfully!", "success")
        return redirect(url_for("patients"))
    return render_template("add_patient.html")


@app.route("/patients/<int:id>")
def view_patient(id):
    conn = get_db_connection()
    cur = dict_cursor(conn)

    cur.execute("SELECT * FROM patients WHERE id=%s", (id,))
    patient = cur.fetchone()

    cur.execute("""
        SELECT a.*, d.first_name AS doc_first, d.last_name AS doc_last,
               d.specialization
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.id
        WHERE a.patient_id = %s
        ORDER BY a.appointment_date DESC
    """, (id,))
    appointments = cur.fetchall()

    cur.execute("SELECT * FROM bills WHERE patient_id=%s ORDER BY bill_date DESC", (id,))
    bills = cur.fetchall()

    cur.close()
    conn.close()
    return render_template("view_patient.html",
        patient=patient, appointments=appointments, bills=bills)


@app.route("/patients/edit/<int:id>", methods=["GET", "POST"])
def edit_patient(id):
    conn = get_db_connection()
    cur = dict_cursor(conn)

    if request.method == "POST":
        cur.execute("""
            UPDATE patients
            SET first_name=%s, last_name=%s, date_of_birth=%s, gender=%s,
                phone=%s, email=%s, address=%s, blood_group=%s,
                emergency_contact=%s
            WHERE id=%s
        """, (
            request.form["first_name"], request.form["last_name"],
            request.form["dob"], request.form["gender"],
            request.form["phone"], request.form["email"],
            request.form["address"], request.form["blood_group"],
            request.form["emergency_contact"], id
        ))
        conn.commit()
        cur.close()
        conn.close()
        flash("Patient updated!", "success")
        return redirect(url_for("view_patient", id=id))

    cur.execute("SELECT * FROM patients WHERE id=%s", (id,))
    patient = cur.fetchone()
    cur.close()
    conn.close()
    return render_template("edit_patient.html", patient=patient)


@app.route("/patients/delete/<int:id>", methods=["POST"])
def delete_patient(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM appointments WHERE patient_id=%s", (id,))
    cur.execute("DELETE FROM bills WHERE patient_id=%s", (id,))
    cur.execute("DELETE FROM patients WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Patient deleted.", "info")
    return redirect(url_for("patients"))


# ─────────────────────────────
# DOCTORS
# ─────────────────────────────
@app.route("/doctors")
def doctors():
    conn = get_db_connection()
    cur = dict_cursor(conn)
    cur.execute("SELECT * FROM doctors ORDER BY created_at DESC")
    doctors = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("doctors.html", doctors=doctors)


@app.route("/doctors/add", methods=["GET", "POST"])
def add_doctor():
    if request.method == "POST":
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO doctors
            (first_name, last_name, specialization, phone, email,
             experience_years, qualification, availability)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            request.form["first_name"], request.form["last_name"],
            request.form["specialization"], request.form["phone"],
            request.form["email"], request.form["experience"],
            request.form["qualification"], request.form["availability"]
        ))
        conn.commit()
        cur.close()
        conn.close()
        flash("Doctor added successfully!", "success")
        return redirect(url_for("doctors"))
    return render_template("add_doctor.html")


@app.route("/doctors/<int:id>")
def view_doctor(id):
    conn = get_db_connection()
    cur = dict_cursor(conn)

    cur.execute("SELECT * FROM doctors WHERE id=%s", (id,))
    doctor = cur.fetchone()

    cur.execute("""
        SELECT a.*, p.first_name AS pat_first, p.last_name AS pat_last
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        WHERE a.doctor_id = %s
        ORDER BY a.appointment_date DESC
    """, (id,))
    appointments = cur.fetchall()

    cur.close()
    conn.close()
    return render_template("view_doctor.html", doctor=doctor,
                           appointments=appointments)


@app.route("/doctors/edit/<int:id>", methods=["GET", "POST"])
def edit_doctor(id):
    conn = get_db_connection()
    cur = dict_cursor(conn)

    if request.method == "POST":
        cur.execute("""
            UPDATE doctors
            SET first_name=%s, last_name=%s, specialization=%s, phone=%s,
                email=%s, experience_years=%s, qualification=%s,
                availability=%s
            WHERE id=%s
        """, (
            request.form["first_name"], request.form["last_name"],
            request.form["specialization"], request.form["phone"],
            request.form["email"], request.form["experience"],
            request.form["qualification"], request.form["availability"], id
        ))
        conn.commit()
        cur.close()
        conn.close()
        flash("Doctor updated!", "success")
        return redirect(url_for("view_doctor", id=id))

    cur.execute("SELECT * FROM doctors WHERE id=%s", (id,))
    doctor = cur.fetchone()
    cur.close()
    conn.close()
    return render_template("edit_doctor.html", doctor=doctor)


@app.route("/doctors/delete/<int:id>", methods=["POST"])
def delete_doctor(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM appointments WHERE doctor_id=%s", (id,))
    cur.execute("DELETE FROM doctors WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Doctor removed.", "info")
    return redirect(url_for("doctors"))


# ─────────────────────────────
# APPOINTMENTS
# ─────────────────────────────
@app.route("/appointments")
def appointments():
    conn = get_db_connection()
    cur = dict_cursor(conn)
    cur.execute("""
        SELECT a.*,
               p.first_name AS pat_first, p.last_name AS pat_last,
               d.first_name AS doc_first, d.last_name AS doc_last,
               d.specialization
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors  d ON a.doctor_id  = d.id
        ORDER BY a.appointment_date DESC, a.appointment_time DESC
    """)
    appointments = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("appointments.html", appointments=appointments)


@app.route("/appointments/book", methods=["GET", "POST"])
def book_appointment():
    conn = get_db_connection()
    cur = dict_cursor(conn)

    if request.method == "POST":
        cur.execute("""
            INSERT INTO appointments
            (patient_id, doctor_id, appointment_date, appointment_time,
             reason, notes, status)
            VALUES (%s,%s,%s,%s,%s,%s,'Scheduled')
        """, (
            request.form["patient_id"], request.form["doctor_id"],
            request.form["appointment_date"], request.form["appointment_time"],
            request.form["reason"], request.form["notes"]
        ))
        conn.commit()
        cur.close()
        conn.close()
        flash("Appointment booked!", "success")
        return redirect(url_for("appointments"))

    cur.execute("SELECT id, first_name, last_name FROM patients ORDER BY first_name")
    patients = cur.fetchall()

    cur.execute("SELECT id, first_name, last_name, specialization FROM doctors ORDER BY first_name")
    doctors = cur.fetchall()

    cur.close()
    conn.close()
    return render_template("book_appointment.html",
                           patients=patients, doctors=doctors)


@app.route("/appointments/edit/<int:id>", methods=["GET", "POST"])
def edit_appointment(id):
    conn = get_db_connection()
    cur = dict_cursor(conn)

    if request.method == "POST":
        cur.execute("""
            UPDATE appointments
            SET appointment_date=%s, appointment_time=%s,
                reason=%s, notes=%s, status=%s
            WHERE id=%s
        """, (
            request.form["appointment_date"], request.form["appointment_time"],
            request.form["reason"], request.form["notes"],
            request.form["status"], id
        ))
        conn.commit()
        cur.close()
        conn.close()
        flash("Appointment updated!", "success")
        return redirect(url_for("appointments"))

    cur.execute("""
        SELECT a.*,
               p.first_name AS pat_first, p.last_name AS pat_last,
               d.first_name AS doc_first, d.last_name AS doc_last
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors  d ON a.doctor_id  = d.id
        WHERE a.id = %s
    """, (id,))
    appointment = cur.fetchone()
    cur.close()
    conn.close()
    return render_template("edit_appointment.html", appointment=appointment)


@app.route("/appointments/delete/<int:id>", methods=["POST"])
def delete_appointment(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM appointments WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Appointment cancelled.", "info")
    return redirect(url_for("appointments"))


@app.route("/api/appointment/<int:id>/status", methods=["POST"])
def update_status(id):
    data = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE appointments SET status=%s WHERE id=%s",
                (data["status"], id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"success": True})


# ─────────────────────────────
# BILLING
# ─────────────────────────────
@app.route("/billing")
def billing():
    conn = get_db_connection()
    cur = dict_cursor(conn)
    cur.execute("""
        SELECT b.*, p.first_name AS pat_first, p.last_name AS pat_last
        FROM bills b
        JOIN patients p ON b.patient_id = p.id
        ORDER BY b.created_at DESC
    """)
    bills = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("billing.html", bills=bills)


@app.route("/billing/add", methods=["GET", "POST"])
def add_bill():
    conn = get_db_connection()
    cur = dict_cursor(conn)

    if request.method == "POST":
        cur.execute("""
            INSERT INTO bills
            (patient_id, services, amount, bill_date, status, notes)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (
            request.form["patient_id"], request.form["services"],
            request.form["amount"], request.form["bill_date"],
            request.form["status"], request.form["notes"]
        ))
        conn.commit()
        cur.close()
        conn.close()
        flash("Invoice created!", "success")
        return redirect(url_for("billing"))

    cur.execute("SELECT id, first_name, last_name FROM patients ORDER BY first_name")
    patients = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("add_bill.html", patients=patients)


@app.route("/billing/<int:id>")
def view_bill(id):
    conn = get_db_connection()
    cur = dict_cursor(conn)
    cur.execute("""
        SELECT b.*, p.first_name AS pat_first, p.last_name AS pat_last
        FROM bills b
        JOIN patients p ON b.patient_id = p.id
        WHERE b.id = %s
    """, (id,))
    bill = cur.fetchone()
    cur.close()
    conn.close()
    return render_template("view_bill.html", bill=bill)


@app.route("/billing/delete/<int:id>", methods=["POST"])
def delete_bill(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM bills WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Invoice deleted.", "info")
    return redirect(url_for("billing"))


@app.route("/billing/mark-paid/<int:id>", methods=["POST"])
def mark_paid(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE bills SET status='Paid' WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Invoice marked as paid!", "success")
    return redirect(url_for("view_bill", id=id))


# ─────────────────────────────
# REPORTS
# ─────────────────────────────
@app.route("/reports")
def reports():
    conn = get_db_connection()
    cur = dict_cursor(conn)

    cur.execute("SELECT COALESCE(SUM(amount),0) AS total FROM bills")
    total_revenue = cur.fetchone()["total"]

    cur.execute("SELECT COALESCE(SUM(amount),0) AS total FROM bills WHERE status='Paid'")
    paid_revenue = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) AS cnt FROM bills WHERE status='Unpaid'")
    pending_bills = cur.fetchone()["cnt"]

    cur.execute("SELECT COUNT(*) AS cnt FROM appointments WHERE status='Completed'")
    completed_appointments = cur.fetchone()["cnt"]

    cur.execute("SELECT COUNT(*) AS cnt FROM appointments WHERE status='Scheduled'")
    appt_scheduled = cur.fetchone()["cnt"]

    cur.execute("SELECT COUNT(*) AS cnt FROM appointments WHERE status='Completed'")
    appt_completed = cur.fetchone()["cnt"]

    cur.execute("SELECT COUNT(*) AS cnt FROM appointments WHERE status='Cancelled'")
    appt_cancelled = cur.fetchone()["cnt"]

    cur.execute("SELECT COUNT(*) AS cnt FROM appointments WHERE status='No-Show'")
    appt_noshow = cur.fetchone()["cnt"]

    cur.execute("""
        SELECT d.first_name, d.last_name, d.specialization,
               COUNT(a.id) AS appt_count
        FROM doctors d
        LEFT JOIN appointments a ON d.id = a.doctor_id
        GROUP BY d.id, d.first_name, d.last_name, d.specialization
        ORDER BY appt_count DESC LIMIT 5
    """)
    top_doctors = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("reports.html",
        total_revenue=total_revenue,
        paid_revenue=paid_revenue,
        pending_bills=pending_bills,
        completed_appointments=completed_appointments,
        appt_scheduled=appt_scheduled,
        appt_completed=appt_completed,
        appt_cancelled=appt_cancelled,
        appt_noshow=appt_noshow,
        top_doctors=top_doctors)


# ─────────────────────────────
# RUN
# ─────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
