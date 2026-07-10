from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship


db = SQLAlchemy()


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    users = db.relationship("User", back_populates="role", lazy=True)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30))
    address = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    role = db.relationship("Role", back_populates="users")
    doctor = db.relationship("Doctor", back_populates="user", uselist=False)
    patient = db.relationship("Patient", back_populates="user", uselist=False)
    notifications = db.relationship("Notification", back_populates="user", lazy=True)
    audit_logs = db.relationship("AuditLog", back_populates="user", lazy=True)
    ai_chats = db.relationship("AIChat", back_populates="user", lazy=True)
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False


class Doctor(db.Model):
    __tablename__ = "doctors"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    specialty = db.Column(db.String(120), nullable=False)
    license_number = db.Column(db.String(80))
    bio = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="doctor")
    appointments = db.relationship("Appointment", back_populates="doctor", lazy=True)
    medical_reports = db.relationship("MedicalReport", back_populates="doctor", lazy=True)
    prescriptions = db.relationship("Prescription", back_populates="doctor", lazy=True)


class Patient(db.Model):
    __tablename__ = "patients"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    date_of_birth = db.Column(db.DateTime)
    gender = db.Column(db.String(20))
    blood_group = db.Column(db.String(10))
    emergency_contact_name = db.Column(db.String(120))
    emergency_contact_phone = db.Column(db.String(30))
    insurance_number = db.Column(db.String(80))
    allergies = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="patient")
    appointments = db.relationship("Appointment", back_populates="patient", lazy=True)
    medical_reports = db.relationship("MedicalReport", back_populates="patient", lazy=True)
    prescriptions = db.relationship("Prescription", back_populates="patient", lazy=True)
    payments = db.relationship("Payment", back_populates="patient", lazy=True)
    emergency_cases = db.relationship("EmergencyCase", back_populates="patient", lazy=True)
    admissions = db.relationship("Admission", back_populates="patient", lazy=True)


class Department(db.Model):
    __tablename__ = "departments"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    bed_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    appointments = db.relationship("Appointment", back_populates="department", lazy=True)
    beds = db.relationship("Bed", back_populates="department", lazy=True)


class Appointment(db.Model):
    __tablename__ = "appointments"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(30), default="pending")
    priority = db.Column(db.String(30), default="normal")
    symptoms = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship("Patient", back_populates="appointments")
    doctor = db.relationship("Doctor", back_populates="appointments")
    department = db.relationship("Department", back_populates="appointments")
    prescriptions = db.relationship("Prescription", back_populates="appointment", lazy=True)


class MedicalReport(db.Model):
    __tablename__ = "medical_reports"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    summary = db.Column(db.Text)
    content = db.Column(db.Text)
    file_path = db.Column(db.String(255))
    report_date = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship("Patient", back_populates="medical_reports")
    doctor = db.relationship("Doctor", back_populates="medical_reports")


class Prescription(db.Model):
    __tablename__ = "prescriptions"
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id"), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False)
    medicine_name = db.Column(db.String(200), nullable=False)
    dosage = db.Column(db.String(120))
    instructions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    appointment = db.relationship("Appointment", back_populates="prescriptions")
    patient = db.relationship("Patient", back_populates="prescriptions")
    doctor = db.relationship("Doctor", back_populates="prescriptions")


class Medicine(db.Model):
    __tablename__ = "medicines"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    generic_name = db.Column(db.String(160))
    category = db.Column(db.String(80))
    stock_quantity = db.Column(db.Integer, default=0)
    unit_price = db.Column(db.Float, default=0.0)
    expiry_date = db.Column(db.DateTime)
    manufacturer = db.Column(db.String(160))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    inventory = db.relationship("Inventory", back_populates="medicine", uselist=False)


class Inventory(db.Model):
    __tablename__ = "inventory"
    id = db.Column(db.Integer, primary_key=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey("medicines.id"), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    reorder_level = db.Column(db.Integer, default=10)
    location = db.Column(db.String(120))

    medicine = db.relationship("Medicine", back_populates="inventory")


class Admission(db.Model):
    __tablename__ = "admissions"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    bed_id = db.Column(db.Integer, db.ForeignKey("beds.id"), nullable=False)
    reason = db.Column(db.Text)
    admitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    discharged_at = db.Column(db.DateTime)

    patient = db.relationship("Patient", back_populates="admissions")
    bed = db.relationship("Bed", back_populates="admissions")


class Bed(db.Model):
    __tablename__ = "beds"
    id = db.Column(db.Integer, primary_key=True)
    bed_number = db.Column(db.String(80), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)
    status = db.Column(db.String(30), default="available")
    room_number = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    department = db.relationship("Department", back_populates="beds")
    admissions = db.relationship("Admission", back_populates="bed", lazy=True)


class Room(db.Model):
    __tablename__ = "rooms"
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(80), nullable=False)
    room_type = db.Column(db.String(80), default="General")
    status = db.Column(db.String(30), default="available")
    bed_count = db.Column(db.Integer, default=1)


class Payment(db.Model):
    __tablename__ = "payments"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default="USD")
    status = db.Column(db.String(30), default="pending")
    payment_type = db.Column(db.String(80))
    paid_at = db.Column(db.DateTime)

    patient = db.relationship("Patient", back_populates="payments")
    invoice = db.relationship("Invoice", back_populates="payment", uselist=False)


class Invoice(db.Model):
    __tablename__ = "invoices"
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey("payments.id"), nullable=False)
    invoice_number = db.Column(db.String(80), unique=True, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.DateTime)
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)

    payment = db.relationship("Payment", back_populates="invoice")


class EmergencyCase(db.Model):
    __tablename__ = "emergency_cases"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    severity = db.Column(db.String(30), default="high")
    description = db.Column(db.Text)
    status = db.Column(db.String(30), default="open")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship("Patient", back_populates="emergency_cases")


class Notification(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(80), default="info")
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="notifications")


class AIChat(db.Model):
    __tablename__ = "ai_chats"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    role = db.Column(db.String(80), default="patient")
    message = db.Column(db.Text)
    response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="ai_chats")


class AuditLog(db.Model):
    __tablename__ = "audit_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    action = db.Column(db.String(120), nullable=False)
    entity = db.Column(db.String(120))
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="audit_logs")
