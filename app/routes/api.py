from datetime import datetime
from unittest import result
from click import prompt
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_current_user, jwt_required
from werkzeug.utils import secure_filename
from app.services.gemini_service import generate_json
from app.models import Appointment, Bed, Department, Doctor, EmergencyCase, Inventory, MedicalReport, Medicine, Patient, Prescription, User, db
from app.services.ai_service import ai_chatbot, extract_text_from_file, summarize_report
from app.services.gemini_service import generate_json
from app.services.symptom_checker import analyze_symptoms
from app.services.drug_interaction_checker import check_drug_interaction
from app.services.prescription_explainer import explain_prescription
from app.utils.security import role_required
from app import socketio

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/dashboard/stats")
@jwt_required(optional=True)
def dashboard_stats():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({
        "role": user.role.name,
        "doctors": Doctor.query.count(),
        "patients": Patient.query.count(),
        "appointments": Appointment.query.count(),
        "beds": Bed.query.count(),
        "medicines": Medicine.query.count(),
    })


@api_bp.route("/appointments")
@jwt_required(optional=True)
def get_appointments():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    if user.role.name == "patient":
        patient = Patient.query.filter_by(user_id=user.id).first()
        appointments = Appointment.query.filter_by(patient_id=patient.id).all() if patient else []
    else:
        appointments = Appointment.query.all()
    return jsonify([appointment_to_dict(a) for a in appointments])


@api_bp.route("/appointments", methods=["POST"])
@jwt_required(optional=True)
def create_appointment_api():
    user = get_current_user()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    # Safely get JSON data
    data = request.get_json(silent=True) or {}

    # Validate appointment date
    appointment_date = data.get("appointment_date")

    if not appointment_date:
        return jsonify({
            "success": False,
            "message": "Appointment date is required."
        }), 400

    try:
        appointment_date = datetime.fromisoformat(appointment_date)
    except ValueError:
        return jsonify({
            "success": False,
            "message": "Invalid appointment date format."
        }), 400

    try:
        # Find or create patient
        patient = Patient.query.filter_by(user_id=user.id).first()

        if not patient:
            patient = Patient(user_id=user.id)
            db.session.add(patient)
            db.session.commit()

        # Create appointment
        appt = Appointment(
            patient_id=patient.id,
            doctor_id=data.get("doctor_id", 1),
            department_id=data.get("department_id", 1),
            appointment_date=appointment_date,
            status="pending",
            symptoms=data.get("symptoms", ""),
            priority=data.get("priority", "normal"),
            notes=data.get("notes", "")
        )

        db.session.add(appt)
        db.session.commit()

        socketio.emit(
            "queue_update",
            {
                "message": "New appointment booked",
                "appointment_id": appt.id
            },
            namespace="/"
        )

        return jsonify(appointment_to_dict(appt)), 201

    except Exception as e:
        db.session.rollback()

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500



@api_bp.route("/appointments/<int:appointment_id>/status", methods=["POST"])
@role_required("admin", "doctor", "receptionist")
def update_appointment_status_api(appointment_id):
    try:
        appointment = Appointment.query.get_or_404(appointment_id)

        data = request.get_json(silent=True) or {}

        appointment.status = data.get("status", appointment.status)

        db.session.commit()

        return jsonify({
            "success": True,
            "status": appointment.status
        })

    except Exception as e:
        db.session.rollback()

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@api_bp.route("/doctors")
def get_doctors():
    return jsonify([doctor_to_dict(d) for d in Doctor.query.all()])


@api_bp.route("/patients")
@jwt_required(optional=True)
def get_patients():
    return jsonify([patient_to_dict(p) for p in Patient.query.all()])


@api_bp.route("/departments")
def get_departments():
    return jsonify([department_to_dict(d) for d in Department.query.all()])


@api_bp.route("/beds")
def get_beds():
    return jsonify([bed_to_dict(b) for b in Bed.query.all()])


@api_bp.route("/medicines")
def get_medicines():
    return jsonify([medicine_to_dict(m) for m in Medicine.query.all()])


@api_bp.route("/reports")
@jwt_required(optional=True)
def get_reports():
    return jsonify([report_to_dict(r) for r in MedicalReport.query.all()])


@api_bp.route("/prescriptions")
@jwt_required(optional=True)
def get_prescriptions():
    return jsonify([prescription_to_dict(p) for p in Prescription.query.all()])


@api_bp.route("/ai/appointment-assistant", methods=["POST"])
@jwt_required(optional=True)
def ai_appointment_assistant():
    data = request.get_json(silent=True) or {}
    symptoms = data.get("symptoms", "")
    try:
        result = generate_json(prompt)
        return jsonify(result)

    except Exception:
        return jsonify({
        "department": "General Medicine",
        "doctor": "Dr. Ravi Patel",
        "priority": "Medium",
        "summary": f"Based on the symptoms '{symptoms}', consult a General Medicine specialist.",
        "precautions": [
            "Drink plenty of fluids",
            "Take adequate rest",
            "Monitor your symptoms"
        ],
        "disclaimer": "This AI recommendation is for educational purposes only and is not a medical diagnosis."
    })

@api_bp.route("/ai/report-summarizer", methods=["POST"])
@jwt_required(optional=True)
def ai_report_summarizer():
    text = request.form.get("text", "")
    file_storage = request.files.get("file")
    if file_storage:
        text = extract_text_from_file(file_storage)
    if not text:
        return jsonify({"error": "Report content is required"}), 400
    summary = summarize_report(text)
    print("=" * 50)
    print(summary)
    print(type(summary))
    print("=" * 50)
    return jsonify(summary)


@api_bp.route("/ai/prescription-explainer", methods=["POST"])
@jwt_required()
def ai_prescription_explainer_api():

    data = request.get_json(silent=True) or {}

    medicine = data.get("medicine_name", "")
    dosage = data.get("dosage", "")
    instructions = data.get("instructions", "")

    result = explain_prescription(
        medicine,
        dosage,
        instructions
    )

    return jsonify(result)

@api_bp.route("/ai/chatbot", methods=["POST"])
@jwt_required(optional=True)
def ai_chatbot_endpoint():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")
    if not message:
        return jsonify({"error": "Message is required"}), 400
    response = ai_chatbot(message)
    return jsonify(response)


@api_bp.route("/ai/symptom-checker", methods=["POST"])
@jwt_required(optional=True)
def ai_symptom_checker():
    """
    Analyze patient symptoms and provide hospital triage routing.
    
    NOT a diagnosis tool. Recommends department, doctor, and urgency level
    based on symptom analysis.
    """
    data = request.get_json(silent=True) or {}
    symptoms = data.get("symptoms", "").strip()
    
    if not symptoms:
        return jsonify({"error": "Symptoms description is required"}), 400
    
    if len(symptoms) < 5:
        return jsonify({"error": "Please provide more details about your symptoms"}), 400
    
    try:
        result = analyze_symptoms(symptoms)
        return jsonify(result)
    except Exception as e:
        print(f"Error in symptom checker: {e}")
        return jsonify({"error": "Unable to analyze symptoms. Please try again."}), 500


@api_bp.route("/ai/drug-interaction-checker", methods=["POST"])
@jwt_required(optional=True)
def ai_drug_interaction_checker():
    print("✅ Drug interaction API called")
    """
    Analyze potential drug interactions between two medications.
    
    NOT a diagnosis tool. Provides educational information about
    known drug interactions using OpenAI GPT or local knowledge base.
    """
    data = request.get_json(silent=True) or {}
    drug1 = data.get("drug1", "").strip()
    drug2 = data.get("drug2", "").strip()
    
    if not drug1 or not drug2:
        return jsonify({"error": "Both drug names are required"}), 400
    
    if len(drug1) < 2 or len(drug2) < 2:
        return jsonify({"error": "Please provide valid drug names"}), 400
    
    try:
        result = check_drug_interaction(drug1, drug2)
        return jsonify(result)
    except Exception as e:
        print(f"Error in drug interaction checker: {e}")
        return jsonify({"error": "Unable to analyze drug interactions. Please try again."}), 500


@api_bp.route("/notifications")
@jwt_required(optional=True)
def get_notifications():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify([{"id": n.id, "title": n.title, "message": n.message, "type": n.notification_type, "read": n.is_read} for n in user.notifications])


def appointment_to_dict(a):
    return {
        "id": a.id,
        "patient": a.patient.user.full_name if a.patient and a.patient.user else None,
        "doctor": a.doctor.user.full_name if a.doctor and a.doctor.user else None,
        "department": a.department.name if a.department else None,
        "date": a.appointment_date.isoformat(),
        "status": a.status,
        "priority": a.priority,
        "symptoms": a.symptoms,
        "notes": a.notes,
    }


def doctor_to_dict(d):
    return {"id": d.id, "full_name": d.user.full_name, "specialty": d.specialty, "license_number": d.license_number}


def patient_to_dict(p):
    return {"id": p.id, "full_name": p.user.full_name, "email": p.user.email, "phone": p.user.phone}


def department_to_dict(d):
    return {"id": d.id, "name": d.name, "description": d.description, "bed_count": d.bed_count}


def bed_to_dict(b):
    return {"id": b.id, "bed_number": b.bed_number, "status": b.status, "room_number": b.room_number, "department": b.department.name if b.department else None}


def medicine_to_dict(m):
    return {"id": m.id, "name": m.name, "stock_quantity": m.stock_quantity, "unit_price": m.unit_price, "manufacturer": m.manufacturer}


def report_to_dict(r):
    return {"id": r.id, "title": r.title, "summary": r.summary, "report_date": r.report_date.isoformat()}


def prescription_to_dict(p):
    return {"id": p.id, "medicine_name": p.medicine_name, "dosage": p.dosage, "instructions": p.instructions}
