import os
import re
from typing import Optional

from app.services.gemini_service import generate_text, generate_json
from pypdf import PdfReader
from dotenv import load_dotenv

load_dotenv()




def extract_text_from_file(file_storage) -> str:
    if not file_storage:
        return ""
    file_storage.stream.seek(0)
    if file_storage.filename and file_storage.filename.lower().endswith(".pdf"):
        reader = PdfReader(file_storage)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        return text
    return file_storage.read().decode("utf-8", errors="ignore")


def summarize_report(text: str) -> dict:
    """
    Summarize a medical report using Gemini AI.
    Falls back to a simple summary if Gemini is unavailable.
    """

    if not text.strip():
        return {
            "summary": "No report provided.",
            "mode": "fallback"
        }
    prompt = f"""
You are an experienced hospital doctor.

Analyze the following medical report.

Medical Report:
{text}

Return ONLY valid JSON in this format:

{{
    "summary": "",
    "findings": [],
    "follow_up": [],
    "severity": ""
}}
"""

    try:
        answer = generate_json(prompt)

        answer["mode"] = "gemini"

        return answer

    except Exception as e:
        print("Gemini Error:", e)

        # Local fallback
        return {
    "summary": text[:250] + "...",
    "findings": [],
    "follow_up": [],
    "severity": "Unknown",
    "mode": "fallback"
}


def explain_prescription(medicine_name, dosage, instructions):

    prompt = f"""
Explain this prescription in simple English.

Medicine:
{medicine_name}

Dosage:
{dosage}

Instructions:
{instructions}

Explain:

• What medicine is this?
• Why is it used?
• How should the patient take it?
• Common side effects.
• Important precautions.

Use simple language.
"""

    try:

        answer = generate_text(prompt)

        return {
            "summary": answer,
            "mode": "gemini"
        }

    except Exception as e:
        print(e)

        return {
            "summary": "Unable to explain prescription.",
            "mode": "fallback"
        }

def ai_chatbot(message: str):
    print("Message received:", message)

    prompt = f"""
You are MediAI, an AI hospital assistant.

Answer the patient's question in simple English.

Rules:

- Keep the answer under 80 words.
- Use short sentences.
- Use bullet points whenever possible.
- Never write long paragraphs.
- If it is an emergency, clearly say "Visit the nearest hospital immediately."
- If it is not an emergency, give simple self-care advice.
- End with:
"⚠️ This is not a medical diagnosis. Please consult a doctor."

Patient Question:
{message}
"""

    try:
        answer = generate_text(prompt)

        print("Gemini Response:", answer)

        return {
            "response": answer,
            "mode": "gemini"
        }

    except Exception as e:
        import traceback
        traceback.print_exc()

        return {
            "response": str(e),
            "mode": "fallback"
        }
