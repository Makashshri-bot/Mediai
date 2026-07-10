"""
AI Symptom Checker Service - Hospital Triage Assistant

Analyzes patient symptoms and recommends appropriate department,
doctor, and urgency level. NOT a diagnostic tool.
"""
import json
import re
from typing import Optional, Dict
from app.services.gemini_service import generate_json
from app.models import Doctor, Department, db


def get_best_doctor_for_department(department_name: str) -> Optional[Dict]:
    """Find a doctor whose specialty matches the recommended department."""
    # Normalize department name for matching
    dept = department_name.lower().strip()
    
    # Try to find doctor with matching specialty
    doctor = Doctor.query.filter(
        db.func.lower(Doctor.specialty).contains(dept)
    ).first()
    
    if doctor:
        return {
            "id": doctor.id,
            "name": doctor.user.full_name,
            "specialty": doctor.specialty,
            "license": doctor.license_number or "N/A"
        }
    
    # Fallback: return first available doctor if no specialty match
    doctor = Doctor.query.first()
    if doctor:
        return {
            "id": doctor.id,
            "name": doctor.user.full_name,
            "specialty": doctor.specialty,
            "license": doctor.license_number or "N/A"
        }
    
    return None


def check_symptoms_with_ai(symptoms: str) -> Optional[Dict]:
    """
    Analyze symptoms using Gemini AI.
    """

    if not symptoms:
        return None

    prompt = f"""
You are an experienced hospital triage assistant.

Your ONLY purpose is to GUIDE patients to the correct hospital department.

Rules:
- Never diagnose diseases.
- Never prescribe medicine.
- Recommend the correct department.
- Mention urgency.
- Give 3 precautions.
- Give a short summary.

Return ONLY valid JSON.

{{
    "department": "",
    "urgency": "",
    "priority": "",
    "precautions": [],
    "summary": ""
}}

Patient Symptoms:
{symptoms}
"""

    try:
        result = generate_json(prompt)

        return {
            "department": result.get("department", "General Medicine"),
            "urgency": result.get("urgency", "Medium"),
            "priority": result.get("priority", "normal"),
            "precautions": result.get("precautions", [])[:3],
            "summary": result.get(
                "summary",
                "Please visit the recommended department."
            ),
            "mode": "gemini"
        }

    except Exception as e:
        print("Gemini Error:", e)
        return None

def check_symptoms_fallback(symptoms: str) -> Dict:
    """
    Fallback heuristic-based symptom triage when OpenAI is unavailable.
    
    Maps keywords to departments for basic routing.
    """
    symptoms_lower = symptoms.lower()
    
    # Keyword-to-department mapping for fallback
    routing_map = {
        "chest": ("Cardiology", "High"),
        "heart": ("Cardiology", "High"),
        "breath": ("Pulmonology", "High"),
        "lung": ("Pulmonology", "High"),
        "stomach": ("Gastroenterology", "Medium"),
        "abdomen": ("Gastroenterology", "Medium"),
        "head": ("Neurology", "Medium"),
        "wound": ("Emergency", "High"),
        "fever": ("General Medicine", "Medium"),
        "pain": ("General Medicine", "Medium"),
        "fracture": ("Orthopedics", "High"),
        "bone": ("Orthopedics", "Medium"),
        "eye": ("Ophthalmology", "Medium"),
        "ear": ("ENT", "Low"),
        "pregnant": ("OB/GYN", "Medium"),
    }
    
    department = "General Medicine"
    urgency = "Medium"
    
    for keyword, (dept, urg) in routing_map.items():
        if keyword in symptoms_lower:
            department = dept
            urgency = urg
            break
    
    priority_map = {"Low": "normal", "Medium": "medium", "High": "urgent", "Urgent": "urgent"}
    priority = priority_map.get(urgency, "normal")
    
    precautions_map = {
        "Cardiology": ["Avoid strenuous activity", "Monitor heart rate", "Keep medications handy"],
        "Pulmonology": ["Ensure adequate oxygen access", "Avoid triggers", "Monitor breathing"],
        "Emergency": ["Seek immediate care", "Apply first aid if trained", "Call emergency services if worsening"],
        "Orthopedics": ["Immobilize affected area", "Apply ice if available", "Avoid weight-bearing"],
    }
    
    precautions = precautions_map.get(department, [
        "Stay calm and hydrated",
        "Rest until evaluated",
        "Note any changes in symptoms"
    ])
    
    return {
        "department": department,
        "urgency": urgency,
        "priority": priority,
        "precautions": precautions[:3],
        "summary": f"Based on your symptoms, {department} is the recommended department.",
        "mode": "fallback"
    }


def analyze_symptoms(symptoms: str) -> Dict:
    """
    Main entry point for symptom analysis.
    
    Attempts OpenAI first, falls back to heuristic if needed.
    Always includes doctor recommendation and disclaimer.
    
    Returns:
        Complete triage recommendation with all fields
    """
    # Get AI analysis (or fallback)
    result = check_symptoms_with_ai(symptoms)
    
    if not result:
        result = check_symptoms_fallback(symptoms)
    
    # Add doctor recommendation
    doctor_info = get_best_doctor_for_department(result.get("department", "General Medicine"))
    if doctor_info:
        result["doctor"] = doctor_info["name"]
        result["doctor_specialty"] = doctor_info["specialty"]
    else:
        result["doctor"] = "Available doctor on duty"
        result["doctor_specialty"] = result.get("department", "General Medicine")
    
    # Add disclaimer
    result["disclaimer"] = (
        "⚠️ IMPORTANT: This is an AI-powered triage recommendation only, "
        "NOT a medical diagnosis. Please consult with a healthcare professional "
        "for proper evaluation and diagnosis."
    )
    
    return result
