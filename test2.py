from app.services.gemini_service import generate_text

print(generate_text("""
You are an AI hospital assistant.

Question:
hi

Answer briefly.
"""))