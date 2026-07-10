import json
import os
import re

from flask import jsonify




from app.services.gemini_service import generate_json

def summarize_report(report_text):

    prompt = f"""
You are an experienced hospital doctor.

Read the medical report and return ONLY valid JSON.

Medical Report:
{report_text}

Return EXACTLY this format:

{{
    "summary":"...",
    "findings":[
        "...",
        "...",
        "..."
    ],
    "follow_up":[
        "...",
        "...",
        "..."
    ],
    "severity":"Low"
}}

No markdown.
No explanation.
JSON only.
"""

    try:

        answer = generate_json(prompt)

        answer["mode"] = "gemini"

        return answer

    except Exception as e:

        print("JSON ERROR:", e)

        return {
            "summary": "Unable to generate summary.",
            "findings": [],
            "follow_up": [],
            "severity": "Unknown",
            "mode": "fallback"
        }