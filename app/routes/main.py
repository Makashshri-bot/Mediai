from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_jwt_extended import get_current_user, jwt_required
from werkzeug.security import check_password_hash, generate_password_hash

from app.models import Appointment, Bed, Department, Doctor, EmergencyCase, Inventory, MedicalReport, Medicine, Notification, Patient, Prescription, Role, User, db
from app.utils.security import role_required
from app import socketio

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    stats = {
        "doctors": Doctor.query.count(),
        "patients": Patient.query.count(),
        "departments": Department.query.count(),
        "beds": Bed.query.count(),
    }
    departments = Department.query.all()
    doctors = Doctor.query.all()
    return render_template("index.html", stats=stats, departments=departments, doctors=doctors)


@main_bp.route("/dashboard")
@role_required("admin", "doctor", "receptionist", "nurse", "pharmacist", "patient")
def dashboard():
    user = get_current_user()
    role_name = user.role.name
    stats = {
        "doctors": Doctor.query.count(),
        "patients": Patient.query.count(),
        "appointments": Appointment.query.count(),
        "beds": Bed.query.count(),
    }
    appointments = Appointment.query.order_by(Appointment.created_at.desc()).limit(10).all()
    departments = Department.query.all()
    doctors = Doctor.query.all()
    patients = Patient.query.all()
    beds = Bed.query.all()
    medicines = Medicine.query.all()
    reports = MedicalReport.query.order_by(MedicalReport.report_date.desc()).limit(10).all()
    prescriptions = Prescription.query.order_by(Prescription.created_at.desc()).limit(10).all()
    notifications = Notification.query.filter_by(user_id=user.id).order_by(Notification.created_at.desc()).limit(10).all()
    return render_template(
        "dashboard.html",
        user=user,
        role_name=role_name,
        stats=stats,
        appointments=appointments,
        departments=departments,
        doctors=doctors,
        patients=patients,
        beds=beds,
        medicines=medicines,
        reports=reports,
        prescriptions=prescriptions,
        notifications=notifications,
    )


@main_bp.route("/profile")
@role_required("admin", "doctor", "receptionist", "nurse", "pharmacist", "patient")
def profile():
    user = get_current_user()
    return render_template("profile.html", user=user)


@main_bp.route("/profile/password", methods=["POST"])
@role_required("admin", "doctor", "receptionist", "nurse", "pharmacist", "patient")
def change_password():
    user = get_current_user()
    old_password = request.form.get("old_password", "")
    new_password = request.form.get("new_password", "")
    if not check_password_hash(user.password_hash, old_password):
        flash("Old password is incorrect.", "danger")
        return redirect(url_for("main.profile"))
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    flash("Password updated.", "success")
    return redirect(url_for("main.profile"))


@main_bp.route("/dashboard/appointment", methods=["POST"])
@role_required("admin", "doctor", "receptionist", "patient")
def create_appointment():
    user = get_current_user()
    patient = Patient.query.filter_by(user_id=user.id).first()
    if not patient:
        patient = Patient(user_id=user.id)
        db.session.add(patient)
        db.session.commit()
    doctor_id = request.form.get("doctor_id", type=int)
    department_id = request.form.get("department_id", type=int)
    appointment_date = request.form.get("appointment_date")
    if not doctor_id or not department_id or not appointment_date:
        flash("Please provide doctor, department and date.", "danger")
        return redirect(url_for("main.dashboard"))
    appointment = Appointment(patient_id=patient.id, doctor_id=doctor_id, department_id=department_id, appointment_date=datetime.fromisoformat(appointment_date), status="pending", symptoms=request.form.get("symptoms", ""), priority=request.form.get("priority", "normal"), notes=request.form.get("notes", ""))
    db.session.add(appointment)
    db.session.commit()
    socketio.emit("queue_update", {"message": "New appointment booked", "appointment_id": appointment.id}, namespace="/")
    flash("Appointment booked successfully.", "success")
    return redirect(url_for("main.dashboard"))


@main_bp.route("/dashboard/report", methods=["POST"])
@role_required("admin", "doctor")
def create_report():
    user = get_current_user()
    patient_id = request.form.get("patient_id", type=int)
    doctor = Doctor.query.filter_by(user_id=user.id).first()
    if not doctor:
        flash("Doctor record not found.", "danger")
        return redirect(url_for("main.dashboard"))
    report = MedicalReport(patient_id=patient_id, doctor_id=doctor.id, title=request.form.get("title", "Report"), summary=request.form.get("summary", ""), content=request.form.get("content", ""))
    db.session.add(report)
    db.session.commit()
    flash("Medical report saved.", "success")
    return redirect(url_for("main.dashboard"))


@main_bp.route("/dashboard/prescription", methods=["POST"])
@role_required("admin", "doctor")
def create_prescription():
    user = get_current_user()
    doctor = Doctor.query.filter_by(user_id=user.id).first()
    appointment_id = request.form.get("appointment_id", type=int)
    patient_id = request.form.get("patient_id", type=int)
    if not doctor:
        flash("Doctor record not found.", "danger")
        return redirect(url_for("main.dashboard"))
    prescription = Prescription(appointment_id=appointment_id, patient_id=patient_id, doctor_id=doctor.id, medicine_name=request.form.get("medicine_name", ""), dosage=request.form.get("dosage", ""), instructions=request.form.get("instructions", ""))
    db.session.add(prescription)
    db.session.commit()
    flash("Prescription created.", "success")
    return redirect(url_for("main.dashboard"))


@main_bp.route("/dashboard/doctor", methods=["POST"])
@role_required("admin")
def create_doctor():
    role = Role.query.filter_by(name="doctor").first()
    user = User(username=request.form.get("username"), email=request.form.get("email"), password_hash=generate_password_hash(request.form.get("password", "Welcome@123")), full_name=request.form.get("full_name"), phone=request.form.get("phone"), role_id=role.id)
    db.session.add(user)
    db.session.commit()
    doctor = Doctor(user_id=user.id, specialty=request.form.get("specialty"), license_number=request.form.get("license_number"), bio=request.form.get("bio"))
    db.session.add(doctor)
    db.session.commit()
    flash("Doctor created.", "success")
    return redirect(url_for("main.dashboard"))


@main_bp.route("/dashboard/department", methods=["POST"])
@role_required("admin")
def create_department():
    department = Department(name=request.form.get("name"), description=request.form.get("description", ""), bed_count=request.form.get("bed_count", type=int) or 0)
    db.session.add(department)
    db.session.commit()
    flash("Department created.", "success")
    return redirect(url_for("main.dashboard"))


@main_bp.route("/dashboard/bed", methods=["POST"])
@role_required("admin")
def create_bed():
    bed = Bed(bed_number=request.form.get("bed_number"), department_id=request.form.get("department_id", type=int), status=request.form.get("status", "available"), room_number=request.form.get("room_number", ""))
    db.session.add(bed)
    db.session.commit()
    socketio.emit("bed_update", {"message": "Bed created", "bed_id": bed.id}, namespace="/")
    flash("Bed created.", "success")
    return redirect(url_for("main.dashboard"))


@main_bp.route("/dashboard/medicine", methods=["POST"])
@role_required("admin", "pharmacist")
def create_medicine():
    medicine = Medicine(name=request.form.get("name"), generic_name=request.form.get("generic_name"), category=request.form.get("category"), stock_quantity=request.form.get("stock_quantity", type=int) or 0, unit_price=request.form.get("unit_price", type=float) or 0.0, manufacturer=request.form.get("manufacturer"), description=request.form.get("description"))
    db.session.add(medicine)
    db.session.commit()
    db.session.add(Inventory(medicine_id=medicine.id, quantity=medicine.stock_quantity, reorder_level=request.form.get("reorder_level", type=int) or 10, location=request.form.get("location", "")))
    db.session.commit()
    flash("Medicine created.", "success")
    return redirect(url_for("main.dashboard"))


@main_bp.route("/dashboard/emergency", methods=["POST"])
@role_required("admin", "receptionist", "doctor")
def create_emergency():
    patient_id = request.form.get("patient_id", type=int)
    case = EmergencyCase(patient_id=patient_id, severity=request.form.get("severity", "high"), description=request.form.get("description", ""), status="open")
    db.session.add(case)
    db.session.commit()
    socketio.emit("emergency_alert", {"message": "Emergency case received", "case_id": case.id}, namespace="/")
    flash("Emergency case logged.", "success")
    return redirect(url_for("main.dashboard"))


@main_bp.route("/dashboard/appointment/status/<int:appointment_id>", methods=["POST"])
@role_required("admin", "doctor", "receptionist")
def update_appointment_status(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.status = request.form.get("status", appointment.status)
    db.session.commit()
    flash("Appointment updated.", "success")
    return redirect(url_for("main.dashboard"))


@main_bp.route("/dashboard/bed/status/<int:bed_id>", methods=["POST"])
@role_required("admin")
def update_bed_status(bed_id):
    bed = Bed.query.get_or_404(bed_id)
    bed.status = request.form.get("status", bed.status)
    db.session.commit()
    socketio.emit("bed_update", {"message": "Bed status changed", "bed_id": bed.id}, namespace="/")
    flash("Bed status updated.", "success")
    return redirect(url_for("main.dashboard"))
