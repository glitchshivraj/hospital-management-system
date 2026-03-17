-- ============================================================
--  Hospital Management System — MySQL Schema
-- ============================================================

CREATE DATABASE IF NOT EXISTS hospital_db;
USE hospital_db;

-- ----------------------------------------------------------
--  PATIENTS
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS patients (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    first_name          VARCHAR(100) NOT NULL,
    last_name           VARCHAR(100) NOT NULL,
    date_of_birth       DATE         NOT NULL,
    gender              ENUM('Male','Female','Other') NOT NULL,
    phone               VARCHAR(20)  NOT NULL,
    email               VARCHAR(150),
    address             TEXT,
    blood_group         VARCHAR(5),
    emergency_contact   VARCHAR(100),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------
--  DOCTORS
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS doctors (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    first_name          VARCHAR(100) NOT NULL,
    last_name           VARCHAR(100) NOT NULL,
    specialization      VARCHAR(150) NOT NULL,
    phone               VARCHAR(20)  NOT NULL,
    email               VARCHAR(150),
    experience_years    INT          DEFAULT 0,
    qualification       VARCHAR(200),
    availability        VARCHAR(200) DEFAULT 'Mon-Fri 9AM-5PM',
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------
--  APPOINTMENTS
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS appointments (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    patient_id          INT NOT NULL,
    doctor_id           INT NOT NULL,
    appointment_date    DATE NOT NULL,
    appointment_time    TIME NOT NULL,
    reason              VARCHAR(300),
    notes               TEXT,
    status              ENUM('Scheduled','Completed','Cancelled','No-Show')
                        DEFAULT 'Scheduled',
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (doctor_id)  REFERENCES doctors(id)
);

-- ----------------------------------------------------------
--  SAMPLE DATA
-- ----------------------------------------------------------
INSERT INTO doctors (first_name, last_name, specialization, phone, email, experience_years, qualification, availability) VALUES
('Priya',   'Sharma',    'Cardiology',         '9876543210', 'priya.sharma@hospital.com',   12, 'MBBS, MD Cardiology',    'Mon-Fri 9AM-4PM'),
('Arjun',   'Mehta',     'Neurology',          '9876543211', 'arjun.mehta@hospital.com',    8,  'MBBS, DM Neurology',     'Mon-Wed 10AM-5PM'),
('Kavitha', 'Nair',      'Pediatrics',         '9876543212', 'kavitha.nair@hospital.com',   15, 'MBBS, MD Pediatrics',    'Tue-Sat 9AM-3PM'),
('Rohan',   'Gupta',     'Orthopedics',        '9876543213', 'rohan.gupta@hospital.com',    10, 'MBBS, MS Orthopedics',   'Mon-Fri 8AM-2PM'),
('Sneha',   'Iyer',      'Dermatology',        '9876543214', 'sneha.iyer@hospital.com',     6,  'MBBS, MD Dermatology',   'Wed-Sun 11AM-6PM');

INSERT INTO patients (first_name, last_name, date_of_birth, gender, phone, email, address, blood_group, emergency_contact) VALUES
('Amit',    'Verma',    '1985-03-15', 'Male',   '9123456780', 'amit.verma@email.com',    '12 Gandhi Nagar, Jaipur',  'O+',  'Sunita Verma – 9123456781'),
('Meera',   'Singh',    '1992-07-22', 'Female', '9123456781', 'meera.singh@email.com',   '45 Shastri Colony, Delhi', 'A+',  'Raj Singh – 9123456782'),
('Deepak',  'Patel',    '1978-11-08', 'Male',   '9123456782', 'deepak.patel@email.com',  '8 MG Road, Mumbai',        'B-',  'Anjali Patel – 9123456783'),
('Lakshmi', 'Rao',      '2000-01-30', 'Female', '9123456783', 'lakshmi.rao@email.com',   '33 Residency Rd, Chennai', 'AB+', 'Krishna Rao – 9123456784'),
('Kiran',   'Mishra',   '1969-05-18', 'Male',   '9123456784', 'kiran.mishra@email.com',  '7 Civil Lines, Lucknow',   'O-',  'Uma Mishra – 9123456785');

INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, reason, notes, status) VALUES
(1, 1, CURDATE(), '09:30:00', 'Chest pain follow-up', 'Patient reported mild discomfort last week', 'Scheduled'),
(2, 3, CURDATE(), '11:00:00', 'Child wellness checkup', 'Annual routine checkup', 'Scheduled'),
(3, 4, DATE_ADD(CURDATE(), INTERVAL 1 DAY), '08:30:00', 'Knee pain', 'X-ray required', 'Scheduled'),
(4, 5, DATE_ADD(CURDATE(), INTERVAL 2 DAY), '14:00:00', 'Skin allergy', 'Recurring issue', 'Scheduled'),
(5, 2, DATE_SUB(CURDATE(), INTERVAL 3 DAY), '10:00:00', 'Migraine treatment', 'MRI report attached', 'Completed');
