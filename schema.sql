CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth TEXT NOT NULL,
    gender TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT,
    address TEXT,
    blood_group TEXT,
    emergency_contact TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS doctors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    specialization TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT,
    experience_years INTEGER DEFAULT 0,
    qualification TEXT,
    availability TEXT DEFAULT 'Mon-Fri 9AM-5PM',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    appointment_date TEXT NOT NULL,
    appointment_time TEXT NOT NULL,
    reason TEXT,
    notes TEXT,
    status TEXT DEFAULT 'Scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(id)
);

INSERT OR IGNORE INTO doctors (id, first_name, last_name, specialization, phone, email, experience_years, qualification, availability) VALUES
(1, 'Priya', 'Sharma', 'Cardiology', '9876543210', 'priya.sharma@hospital.com', 12, 'MBBS, MD Cardiology', 'Mon-Fri 9AM-4PM'),
(2, 'Arjun', 'Mehta', 'Neurology', '9876543211', 'arjun.mehta@hospital.com', 8, 'MBBS, DM Neurology', 'Mon-Wed 10AM-5PM'),
(3, 'Kavitha', 'Nair', 'Pediatrics', '9876543212', 'kavitha.nair@hospital.com', 15, 'MBBS, MD Pediatrics', 'Tue-Sat 9AM-3PM'),
(4, 'Rohan', 'Gupta', 'Orthopedics', '9876543213', 'rohan.gupta@hospital.com', 10, 'MBBS, MS Orthopedics', 'Mon-Fri 8AM-2PM'),
(5, 'Sneha', 'Iyer', 'Dermatology', '9876543214', 'sneha.iyer@hospital.com', 6, 'MBBS, MD Dermatology', 'Wed-Sun 11AM-6PM');

INSERT OR IGNORE INTO patients (id, first_name, last_name, date_of_birth, gender, phone, email, address, blood_group, emergency_contact) VALUES
(1, 'Amit', 'Verma', '1985-03-15', 'Male', '9123456780', 'amit.verma@email.com', '12 Gandhi Nagar, Jaipur', 'O+', 'Sunita Verma - 9123456781'),
(2, 'Meera', 'Singh', '1992-07-22', 'Female', '9123456781', 'meera.singh@email.com', '45 Shastri Colony, Delhi', 'A+', 'Raj Singh - 9123456782'),
(3, 'Deepak', 'Patel', '1978-11-08', 'Male', '9123456782', 'deepak.patel@email.com', '8 MG Road, Mumbai', 'B-', 'Anjali Patel - 9123456783'),
(4, 'Lakshmi', 'Rao', '2000-01-30', 'Female', '9123456783', 'lakshmi.rao@email.com', '33 Residency Rd, Chennai', 'AB+', 'Krishna Rao - 9123456784'),
(5, 'Kiran', 'Mishra', '1969-05-18', 'Male', '9123456784', 'kiran.mishra@email.com', '7 Civil Lines, Lucknow', 'O-', 'Uma Mishra - 9123456785');

INSERT OR IGNORE INTO appointments (id, patient_id, doctor_id, appointment_date, appointment_time, reason, notes, status) VALUES
(1, 1, 1, date('now'), '09:30', 'Chest pain follow-up', 'Patient reported mild discomfort last week', 'Scheduled'),
(2, 2, 3, date('now'), '11:00', 'Child wellness checkup', 'Annual routine checkup', 'Scheduled'),
(3, 3, 4, date('now', '+1 day'), '08:30', 'Knee pain', 'X-ray required', 'Scheduled'),
(4, 4, 5, date('now', '+2 days'), '14:00', 'Skin allergy', 'Recurring issue', 'Scheduled'),
(5, 5, 2, date('now', '-3 days'), '10:00', 'Migraine treatment', 'MRI report attached', 'Completed');