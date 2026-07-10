from flask import Blueprint, render_template

from app.utils.security import role_required

views_bp = Blueprint("views", __name__)


@views_bp.route("/appointments")
@role_required("admin", "doctor", "receptionist", "nurse", "pharmacist", "patient")
def appointments():
    return render_template("appointments.html")


@views_bp.route("/doctors")
@role_required("admin", "doctor", "receptionist", "nurse", "pharmacist", "patient")
def doctors():
    return render_template("doctors.html")


@views_bp.route("/patients")
@role_required("admin", "doctor", "receptionist", "nurse", "pharmacist", "patient")
def patients():
    return render_template("patients.html")


@views_bp.route("/departments")
@role_required("admin", "doctor", "receptionist", "nurse", "pharmacist", "patient")
def departments():
    return render_template("departments.html")


@views_bp.route("/beds")
@role_required("admin", "doctor", "receptionist", "nurse", "pharmacist", "patient")
def beds():
    return render_template("beds.html")


@views_bp.route("/medicines")
@role_required("admin", "doctor", "receptionist", "nurse", "pharmacist", "patient")
def medicines():
    return render_template("medicines.html")


@views_bp.route("/reports")
@role_required("admin", "doctor", "receptionist", "nurse", "pharmacist", "patient")
def reports():
    return render_template("reports.html")


@views_bp.route("/prescriptions")
@role_required("admin", "doctor", "receptionist", "nurse", "pharmacist", "patient")
def prescriptions():
    return render_template("prescriptions.html")


@views_bp.route("/notifications")
@role_required("admin", "doctor", "receptionist", "nurse", "pharmacist", "patient")
def notifications():
    return render_template("notifications.html")


@views_bp.route("/ai/chatbot")
@role_required("admin", "doctor", "receptionist", "nurse", "pharmacist", "patient")
def ai_chatbot():
    return render_template("ai_chatbot.html")


@views_bp.route("/ai/report-summarizer")
@role_required("admin", "doctor", "receptionist", "nurse", "pharmacist", "patient")
def ai_report_summarizer():
    return render_template("ai_report_summarizer.html")


@views_bp.route("/ai/prescription-explainer")
@role_required("admin", "doctor", "receptionist", "nurse", "pharmacist", "patient")
def ai_prescription_explainer():
    return render_template("ai_prescription_explainer.html")


@views_bp.route("/ai/appointment-assistant")
@role_required("admin", "doctor", "receptionist", "nurse", "pharmacist", "patient")
def ai_appointment_assistant():
    return render_template("ai_appointment_assistant.html")

@views_bp.route("/ai/symptom-checker")
@role_required(
    "admin",
    "doctor",
    "receptionist",
    "nurse",
    "pharmacist",
    "patient"
)
def ai_symptom_checker():
    return render_template("ai_symptom_checker.html")

@views_bp.route("/ai/drug-interaction-checker")
@role_required(
    "admin",
    "doctor",
    "receptionist",
    "nurse",
    "pharmacist",
    "patient"
)
def ai_drug_interaction_checker():
    return render_template("ai_drug_interaction_checker.html")