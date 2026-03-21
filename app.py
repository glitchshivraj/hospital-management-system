from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import pg8000
import urllib.parse as urlparse
import os
import ssl

app = Flask(__name__)
app.secret_key = "ms_hospital_secret_2024"

# ==============================
# DATABASE CONFIG (FINAL FIXED)
# ==============================
DATABASE_URL = os.environ.get("DATABASE_URL")

# Fix postgres:// issue
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print("DATABASE_URL loaded:", DATABASE_URL is not None)


def get_db_connection():
    if not DATABASE_URL:
        raise Exception("DATABASE_URL is not set!")

    url = urlparse.urlparse(DATABASE_URL)

    # 🔍 Debug logs (IMPORTANT)
    print("Parsed URL:", url)
    print("Username:", url.username)
    print("Host:", url.hostname)
    print("Port:", url.port)

    if not url.username:
        raise Exception("Database username is missing! Check DATABASE_URL")

    conn = pg8000.connect(
        host=url.hostname,
        port=url.port or 5432,
        database=url.path.lstrip('/'),
        user=url.username,
        password=url.password,
        ssl_context=ssl.create_default_context()   # ✅ FINAL FIX
    )
    return conn


# ==============================
# HELPERS
# ==============================
def fetchall_dict(cursor):
    cols = [d[0] for d in cursor.description]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]


def fetchone_dict(cursor):
    cols = [d[0] for d in cursor.description]
    row = cursor.fetchone()
    return dict(zip(cols, row)) if row else None


# ==============================
# DASHBOARD
# ==============================
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

    cur.execute("SELECT COUNT(*) FROM bills")
    bills_count = cur.fetchone()[0]

    cur.execute("""
        SELECT a.*, p.first_name AS pat_first, p.last_name AS pat_last,
               d.first_name AS doc_first, d.last_name AS doc_last
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors  d ON a.doctor_id  = d.id
        ORDER BY a.created_at DESC LIMIT 5
    """)
    recent_appointments = fetchall_dict(cur)

    cur.close()
    conn.close()

    return render_template("index.html",
        patients_count=patients_count,
        doctors_count=doctors_count,
        appointments_count=appointments_count,
        bills_count=bills_count,
        recent_appointments=recent_appointments)


# ==============================
# PATIENTS
# ==============================
@app.route("/patients")
def patients():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM patients ORDER BY created_at DESC")
    patients = fetchall_dict(cur)

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
    cur = conn.cursor()

    cur.execute("SELECT * FROM patients WHERE id=%s", (id,))
    patient = fetchone_dict(cur)

    cur.execute("""
        SELECT a.*, d.first_name AS doc_first, d.last_name AS doc_last,
               d.specialization
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.id
        WHERE a.patient_id = %s
        ORDER BY a.appointment_date DESC
    """, (id,))
    appointments = fetchall_dict(cur)

    cur.execute("SELECT * FROM bills WHERE patient_id=%s ORDER BY bill_date DESC", (id,))
    bills = fetchall_dict(cur)

    cur.close()
    conn.close()

    return render_template("view_patient.html",
        patient=patient, appointments=appointments, bills=bills)


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


# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))