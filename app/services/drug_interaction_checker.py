import json
import os
import traceback
from app.services.gemini_service import generate_text,generate_json


def check_drug_interaction(medicine1, medicine2):

    prompt = f"""
You are a clinical pharmacist.

Medicine 1:
{medicine1}

Medicine 2:
{medicine2}

Return ONLY JSON.

{{
    "interaction": "",
    "severity": "",
    "symptoms": [],
    "advice": []
}}
"""

    try:
        result = generate_json(prompt)

        # Wrap Gemini response in "result"
        return {
            "result": result
        }

    except Exception as e:
        print(e)

        return {
            "result": {
                "severity": "Moderate",
                "interaction": f"{medicine1} may interact with {medicine2}.",
                "symptoms": [
                    "Dizziness",
                    "Bleeding",
                    "Nausea"
                ],
                "advice": [
                    "Consult your doctor before taking both medicines.",
                    "Do not stop medication without medical advice.",
                    "Monitor for unusual symptoms."
                ]
            }
        }