from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_mysqldb import MySQL
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'hospital_secret_key_2024'

# MySQL Configuration
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'hospital_db')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


# ─────────────────────────────────────────────
#  HOME
# ─────────────────────────────────────────────
@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) AS cnt FROM patients")
    patients_count = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) AS cnt FROM doctors")
    doctors_count = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) AS cnt FROM appointments")
    appointments_count = cur.fetchone()['cnt']
    cur.execute("""
        SELECT COUNT(*) AS cnt FROM appointments
        WHERE appointment_date >= CURDATE() AND status = 'Scheduled'
    """)
    upcoming_count = cur.fetchone()['cnt']
    cur.close()
    return render_template('index.html',
                           patients_count=patients_count,
                           doctors_count=doctors_count,
                           appointments_count=appointments_count,
                           upcoming_count=upcoming_count)


# ─────────────────────────────────────────────
#  PATIENTS
# ─────────────────────────────────────────────
@app.route('/patients')
def patients():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM patients ORDER BY created_at DESC")
    patients = cur.fetchall()
    cur.close()
    return render_template('patients.html', patients=patients)


@app.route('/patients/add', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        first_name   = request.form['first_name']
        last_name    = request.form['last_name']
        dob          = request.form['dob']
        gender       = request.form['gender']
        phone        = request.form['phone']
        email        = request.form['email']
        address      = request.form['address']
        blood_group  = request.form['blood_group']
        emergency_contact = request.form['emergency_contact']

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO patients
              (first_name, last_name, date_of_birth, gender, phone, email,
               address, blood_group, emergency_contact)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (first_name, last_name, dob, gender, phone, email,
              address, blood_group, emergency_contact))
        mysql.connection.commit()
        cur.close()
        flash('Patient registered successfully!', 'success')
        return redirect(url_for('patients'))

    return render_template('add_patient.html')


@app.route('/patients/<int:id>')
def view_patient(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM patients WHERE id = %s", (id,))
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
    cur.close()
    return render_template('view_patient.html', patient=patient,
                           appointments=appointments)


@app.route('/patients/edit/<int:id>', methods=['GET', 'POST'])
def edit_patient(id):
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        first_name   = request.form['first_name']
        last_name    = request.form['last_name']
        dob          = request.form['dob']
        gender       = request.form['gender']
        phone        = request.form['phone']
        email        = request.form['email']
        address      = request.form['address']
        blood_group  = request.form['blood_group']
        emergency_contact = request.form['emergency_contact']

        cur.execute("""
            UPDATE patients
            SET first_name=%s, last_name=%s, date_of_birth=%s, gender=%s,
                phone=%s, email=%s, address=%s, blood_group=%s,
                emergency_contact=%s
            WHERE id=%s
        """, (first_name, last_name, dob, gender, phone, email,
              address, blood_group, emergency_contact, id))
        mysql.connection.commit()
        cur.close()
        flash('Patient updated successfully!', 'success')
        return redirect(url_for('view_patient', id=id))

    cur.execute("SELECT * FROM patients WHERE id = %s", (id,))
    patient = cur.fetchone()
    cur.close()
    return render_template('edit_patient.html', patient=patient)


@app.route('/patients/delete/<int:id>', methods=['POST'])
def delete_patient(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM appointments WHERE patient_id = %s", (id,))
    cur.execute("DELETE FROM patients WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    flash('Patient deleted.', 'info')
    return redirect(url_for('patients'))


# ─────────────────────────────────────────────
#  DOCTORS
# ─────────────────────────────────────────────
@app.route('/doctors')
def doctors():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM doctors ORDER BY created_at DESC")
    doctors = cur.fetchall()
    cur.close()
    return render_template('doctors.html', doctors=doctors)


@app.route('/doctors/add', methods=['GET', 'POST'])
def add_doctor():
    if request.method == 'POST':
        first_name      = request.form['first_name']
        last_name       = request.form['last_name']
        specialization  = request.form['specialization']
        phone           = request.form['phone']
        email           = request.form['email']
        experience      = request.form['experience']
        qualification   = request.form['qualification']
        availability    = request.form['availability']

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO doctors
              (first_name, last_name, specialization, phone, email,
               experience_years, qualification, availability)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (first_name, last_name, specialization, phone, email,
              experience, qualification, availability))
        mysql.connection.commit()
        cur.close()
        flash('Doctor added successfully!', 'success')
        return redirect(url_for('doctors'))

    return render_template('add_doctor.html')


@app.route('/doctors/<int:id>')
def view_doctor(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM doctors WHERE id = %s", (id,))
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
    return render_template('view_doctor.html', doctor=doctor,
                           appointments=appointments)


@app.route('/doctors/edit/<int:id>', methods=['GET', 'POST'])
def edit_doctor(id):
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        first_name      = request.form['first_name']
        last_name       = request.form['last_name']
        specialization  = request.form['specialization']
        phone           = request.form['phone']
        email           = request.form['email']
        experience      = request.form['experience']
        qualification   = request.form['qualification']
        availability    = request.form['availability']

        cur.execute("""
            UPDATE doctors
            SET first_name=%s, last_name=%s, specialization=%s, phone=%s,
                email=%s, experience_years=%s, qualification=%s,
                availability=%s
            WHERE id=%s
        """, (first_name, last_name, specialization, phone, email,
              experience, qualification, availability, id))
        mysql.connection.commit()
        cur.close()
        flash('Doctor updated successfully!', 'success')
        return redirect(url_for('view_doctor', id=id))

    cur.execute("SELECT * FROM doctors WHERE id = %s", (id,))
    doctor = cur.fetchone()
    cur.close()
    return render_template('edit_doctor.html', doctor=doctor)


@app.route('/doctors/delete/<int:id>', methods=['POST'])
def delete_doctor(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM appointments WHERE doctor_id = %s", (id,))
    cur.execute("DELETE FROM doctors WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    flash('Doctor removed.', 'info')
    return redirect(url_for('doctors'))


# ─────────────────────────────────────────────
#  APPOINTMENTS
# ─────────────────────────────────────────────
@app.route('/appointments')
def appointments():
    cur = mysql.connection.cursor()
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
    return render_template('appointments.html', appointments=appointments)


@app.route('/appointments/book', methods=['GET', 'POST'])
def book_appointment():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        patient_id   = request.form['patient_id']
        doctor_id    = request.form['doctor_id']
        appt_date    = request.form['appointment_date']
        appt_time    = request.form['appointment_time']
        reason       = request.form['reason']
        notes        = request.form['notes']

        cur.execute("""
            INSERT INTO appointments
              (patient_id, doctor_id, appointment_date, appointment_time,
               reason, notes, status)
            VALUES (%s,%s,%s,%s,%s,%s,'Scheduled')
        """, (patient_id, doctor_id, appt_date, appt_time, reason, notes))
        mysql.connection.commit()
        cur.close()
        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('appointments'))

    cur.execute("SELECT id, first_name, last_name FROM patients ORDER BY first_name")
    patients = cur.fetchall()
    cur.execute("SELECT id, first_name, last_name, specialization FROM doctors ORDER BY first_name")
    doctors = cur.fetchall()
    cur.close()
    return render_template('book_appointment.html',
                           patients=patients, doctors=doctors)


@app.route('/appointments/edit/<int:id>', methods=['GET', 'POST'])
def edit_appointment(id):
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        appt_date  = request.form['appointment_date']
        appt_time  = request.form['appointment_time']
        reason     = request.form['reason']
        notes      = request.form['notes']
        status     = request.form['status']

        cur.execute("""
            UPDATE appointments
            SET appointment_date=%s, appointment_time=%s,
                reason=%s, notes=%s, status=%s
            WHERE id=%s
        """, (appt_date, appt_time, reason, notes, status, id))
        mysql.connection.commit()
        cur.close()
        flash('Appointment updated!', 'success')
        return redirect(url_for('appointments'))

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
    return render_template('edit_appointment.html', appointment=appointment)


@app.route('/appointments/delete/<int:id>', methods=['POST'])
def delete_appointment(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM appointments WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    flash('Appointment cancelled.', 'info')
    return redirect(url_for('appointments'))


# ─────────────────────────────────────────────
#  API – quick status update (AJAX)
# ─────────────────────────────────────────────
@app.route('/api/appointment/<int:id>/status', methods=['POST'])
def update_status(id):
    data   = request.get_json()
    status = data.get('status')
    cur = mysql.connection.cursor()
    cur.execute("UPDATE appointments SET status=%s WHERE id=%s", (status, id))
    mysql.connection.commit()
    cur.close()
    return jsonify({'success': True})


if __name__ == '__main__':
    app.run(debug=True)
