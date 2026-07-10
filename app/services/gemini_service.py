from google import genai
from dotenv import load_dotenv
import os
import json
import traceback

load_dotenv()

print("Gemini Key Loaded:", bool(os.getenv("GEMINI_API_KEY")))

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_text(prompt):
    try:
        print("\n===== Sending Prompt =====")
        print(prompt)

        response = client.models.generate_content(
            model="models/gemini-3.5-flash",
            contents=prompt
        )

        print("\n===== Response Object =====")
        print(response)

        print("\n===== Response Text =====")
        print(response.text)

        return response.text

    except Exception:
        print("\n===== GEMINI ERROR =====")
        traceback.print_exc()
        raise

def generate_json(prompt):
    text = generate_text(prompt)

    text = text.replace("```json", "")
    text = text.replace("```", "")
    text = text.strip()

    # Extract only the JSON object
    start = text.find("{")
    end = text.rfind("}") + 1

    if start != -1 and end != -1:
        text = text[start:end]
    print("JSON TEXT:")
    print(text)

    data = json.loads(text)

    print("PARSED JSON:")
    print(data)
    return json.loads(text)