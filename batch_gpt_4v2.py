import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# -------------------------
# SETUP & AUTHENTICATION
# -------------------------
load_dotenv()

endpoint = os.getenv("OPENAI_ENDPOINT")
deployment_name = os.getenv("DEPLOYMENT_NAME")
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(
    base_url=endpoint,
    api_key=api_key
)

# -------------------------
# PATHS
# -------------------------
emails_folder = "emails"
output_folder = "outputs_gpt4_v2"

os.makedirs(output_folder, exist_ok=True)

print("Starting email processing using JSON schema mode...\n")

# -------------------------
# JSON SCHEMA
# -------------------------
json_schema = {
    "name": "tour_email_parser",
    "schema": {
        "type": "object",
        "properties": {
            "tour_name": {"type": "string"},
            "destination_country": {"type": "string"},
            "destination_city": {"type": "string"},
            "departure_city": {"type": "string"},
            "start_date": {"type": ["string", "null"]},
            "end_date": {"type": ["string", "null"]},
            "duration_nights": {"type": ["integer", "null"]},
            "duration_days": {"type": ["integer", "null"]},
            "adults": {"type": ["integer", "null"]},
            "children": {"type": ["integer", "null"]},
            "infants": {"type": ["integer", "null"]},
            "hotel_category": {"type": ["string", "null"]},
            "meal_plan": {"type": ["string", "null"]},
            "budget": {"type": ["number", "null"]},
            "currency": {"type": ["string", "null"]},
            "special_requests": {"type": ["string", "null"]},
            "confidence_score": {"type": "number"}
        },
        "required": [
            "tour_name",
            "destination_country",
            "destination_city",
            "departure_city",
            "duration_nights",
            "duration_days",
            "adults",
            "children",
            "infants",
            "confidence_score"
        ]
    }
}

# -------------------------
# PROCESS EMAILS
# -------------------------
for filename in os.listdir(emails_folder):

    if filename.endswith(".txt"):

        print(f"Processing: {filename}")

        file_path = os.path.join(emails_folder, filename)

        with open(file_path, "r", encoding="utf-8") as f:
            email_text = f.read()

        try:

            response = client.chat.completions.create(
                model=deployment_name,
                messages=[
                    {
                        "role": "user",
                        "content": email_text
                    }
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": json_schema
                },
                temperature=0
            )

            result = response.choices[0].message.content
            data = json.loads(result)

        except Exception as e:

            print(f"API failed for {filename}: {e}")

            data = {
                "error": str(e)
            }

        json_filename = filename.replace(".txt", ".json")
        output_path = os.path.join(output_folder, json_filename)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print(f"Saved: {json_filename}\n")

print("All emails processed successfully!")