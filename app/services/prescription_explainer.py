import os

from click import prompt
from app.services.gemini_service import generate_json, generate_text


def explain_prescription(medicine_name, dosage, instructions):
    prompt = f"""
You are an experienced hospital pharmacist.

Return ONLY valid JSON.

{{
  "data": {{
    "medicine": "",
    "used_for": "",
    "how_to_take": "",
    "side_effects": [],
    "precautions": []
  }}
}}

Medicine: {medicine_name}
Dosage: {dosage}
Instructions: {instructions}

Do not return Markdown.
Do not return explanation.
Return only the JSON object.
"""
    try:
        answer = generate_json(prompt)

        answer["mode"] = "gemini"

        return answer

    except Exception as e:
        print(e)

        return {
            "summary": "Unable to generate explanation.",
            "mode": "fallback"
        }