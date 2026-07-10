import os
from datetime import datetime, timedelta

from flask import Flask, flash, g, redirect, request, session, url_for
from flask_cors import CORS
from flask_jwt_extended import JWTManager, get_current_user, get_jwt_identity, jwt_required
from flask_mail import Mail
from flask_migrate import Migrate
from flask_socketio import SocketIO
from werkzeug.security import generate_password_hash

from app.config import Config
from app.models import Appointment, Bed, Department, Doctor, Inventory, Medicine, Patient, Role, User, AuditLog, Notification, db

jwt = JWTManager()
mail = Mail()
cors = CORS()
socketio = SocketIO(cors_allowed_origins="*")
migrate = Migrate()


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    cors.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    migrate.init_app(app, db)

    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.api import api_bp
    from app.routes.views import views_bp
    from app.socket import events  # noqa: F401

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(views_bp)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return db.session.get(User, int(identity))

    @app.context_processor
    def inject_user():
        try:
            user = get_current_user()
        except Exception:
            user = None
        return {"current_user": user}
    with app.app_context():
        db.create_all()
        if app.config.get("DEBUG", False):
            seed_data(app)

    return app


def seed_data(app):
    if Role.query.count() == 0:
        roles = [
            Role(name="admin", description="Administrator"),
            Role(name="doctor", description="Doctor"),
            Role(name="receptionist", description="Receptionist"),
            Role(name="nurse", description="Nurse"),
            Role(name="pharmacist", description="Pharmacist"),
            Role(name="patient", description="Patient"),
        ]
        db.session.add_all(roles)
        db.session.commit()

    if User.query.count() == 0:
        admin_role = Role.query.filter_by(name="admin").first()
        doctor_role = Role.query.filter_by(name="doctor").first()
        receptionist_role = Role.query.filter_by(name="receptionist").first()
        nurse_role = Role.query.filter_by(name="nurse").first()
        pharmacist_role = Role.query.filter_by(name="pharmacist").first()
        patient_role = Role.query.filter_by(name="patient").first()

        admin = User(username="admin", email="admin@mediai.com", password_hash=generate_password_hash("Admin@123"), full_name="Dr. Maya Chen", phone="555-0100", address="Main Hospital", role_id=admin_role.id)
        doctor = User(username="doctor", email="doctor@mediai.com", password_hash=generate_password_hash("Doctor@123"), full_name="Dr. Ravi Patel", phone="555-0101", address="Cardiology", role_id=doctor_role.id)
        receptionist = User(username="receptionist", email="receptionist@mediai.com", password_hash=generate_password_hash("Receptionist@123"), full_name="Sara Cole", phone="555-0102", address="Front Desk", role_id=receptionist_role.id)
        nurse = User(username="nurse", email="nurse@mediai.com", password_hash=generate_password_hash("Nurse@123"), full_name="Lina Gomez", phone="555-0103", address="Ward A", role_id=nurse_role.id)
        pharmacist = User(username="pharmacist", email="pharmacist@mediai.com", password_hash=generate_password_hash("Pharmacist@123"), full_name="Omar Lee", phone="555-0104", address="Pharmacy", role_id=pharmacist_role.id)
        patient = User(username="patient", email="patient@mediai.com", password_hash=generate_password_hash("Patient@123"), full_name="Ava Thompson", phone="555-0105", address="North Street", role_id=patient_role.id)
        db.session.add_all([admin, doctor, receptionist, nurse, pharmacist, patient])
        db.session.commit()

        department = Department(name="General Medicine", description="Primary care and wellness", bed_count=10)
        db.session.add(department)
        db.session.commit()

        db.session.add_all([
            Doctor(user_id=doctor.id, specialty="Cardiology", license_number="LIC-1001", bio="Experienced cardiologist"),
            Patient(user_id=patient.id, date_of_birth=datetime(1990, 5, 12), gender="Female", blood_group="O+", emergency_contact_name="Ben Thompson", emergency_contact_phone="555-0106", insurance_number="INS-1001", allergies="Penicillin"),
        ])
        db.session.commit()

        for i in range(1, 6):
            db.session.add(Bed(bed_number=f"B{i:02d}", department_id=department.id, status="available", room_number=f"R{i:02d}"))
        db.session.commit()

        medicines = [
            Medicine(name="Paracetamol", generic_name="Acetaminophen", category="Analgesic", stock_quantity=120, unit_price=1.25, expiry_date=datetime(2027, 5, 1), manufacturer="MediCorp", description="Pain relief"),
            Medicine(name="Amoxicillin", generic_name="Amoxicillin", category="Antibiotic", stock_quantity=60, unit_price=3.5, expiry_date=datetime(2026, 12, 1), manufacturer="HealLabs", description="Antibiotic"),
            Medicine(name="Insulin", generic_name="Insulin", category="Hormone", stock_quantity=30, unit_price=15.0, expiry_date=datetime(2026, 8, 1), manufacturer="MediCorp", description="Diabetes treatment"),
        ]
        db.session.add_all(medicines)
        db.session.commit()
        for medicine in medicines:
            db.session.add(Inventory(medicine_id=medicine.id, quantity=medicine.stock_quantity, reorder_level=20, location="A-1"))
        db.session.commit()

        appointment_doctor = Doctor.query.first()
        patient_record = Patient.query.first()
        db.session.add(Appointment(patient_id=patient_record.id, doctor_id=appointment_doctor.id, department_id=department.id, appointment_date=datetime.utcnow() + timedelta(days=1), status="approved", priority="normal", symptoms="Chest pain", notes="Routine review"))
        db.session.commit()

        db.session.add_all([
            Notification(user_id=admin.id, title="Welcome", message="Welcome to MediAI", notification_type="info"),
            Notification(user_id=patient.id, title="Appointment ready", message="Your appointment has been approved", notification_type="reminder"),
        ])
        db.session.commit()

        db.session.add(AuditLog(user_id=admin.id, action="seed", entity="system", details="Initial seed data created"))
        db.session.commit()
