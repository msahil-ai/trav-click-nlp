import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from email_fetcher import fetch_next_pending_email

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
output_folder = "outputs"  # Keeping it 'outputs' so your RAG pipeline finds them easily
os.makedirs(output_folder, exist_ok=True)

print("Starting live email processing mode.....\n")

# -------------------------
# JSON SCHEMA
# -------------------------
'''''
json_schema = {
    "name": "tour_email_parser",
    "schema": {
        "type": "object",
        "properties": {
            "email": {"type": ["string", "null"]},
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
            "email",
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
'''
# -------------------------
# JSON SCHEMA (Updated to match Gemma pipeline exactly)
# -------------------------
json_schema = {
    "name": "tour_email_parser",
    "schema": {
        "type": "object",
        "properties": {
            "full_name": {"type": ["string", "null"]},
            "email": {"type": ["string", "null"]},
            "phone": {"type": ["string", "null"]},
            "tour_start_date": {"type": ["string", "null"]},
            "tour_end_date": {"type": ["string", "null"]},
            "city_to_travel": {"type": ["string", "null"]},
            "country_to_travel": {"type": ["string", "null"]},
            "arrival_at_airport": {"type": ["string", "null"]},
            "departure_port": {"type": ["string", "null"]},
            "number_of_adults": {"type": ["integer", "null"]},
            "number_of_males": {"type": ["integer", "null"]},
            "number_of_females": {"type": ["integer", "null"]},
            "number_of_children": {"type": ["integer", "null"]},
            "age_of_children": {"type": ["string", "null"]},
            "number_of_infant": {"type": ["integer", "null"]},
            "suggested_hotel": {"type": ["string", "null"]},
            "suggested_restaurants": {"type": ["string", "null"]},
            "attractions_to_visit": {"type": ["string", "null"]}
        },
        "required": [
            "email",
            "city_to_travel",
            "country_to_travel",
            "tour_start_date",
            "tour_end_date",
            "number_of_children",
            "number_of_infant",
            "number_of_adults"
        ],
        "additionalProperties": False
    }
}


# -------------------------
# PROCESS EMAILS FROM INBOX
# -------------------------
counter = 1

while True:
    # 1. Fetch live from the inbox
    email_text = fetch_next_pending_email()

    # 2. Break the loop if the inbox is clear
    if not email_text:
        print("......No more pending emails. Exiting.")
        break

    print(f"\n......Processing email #{counter}")

    try:
        # 3. Process with OpenAI
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
        print("..... JSON extracted successfully")

    except Exception as e:
        print(f"..... API failed for email #{counter}: {e}")
        data = {
            "error": str(e)
        }

    # 4. Save to the outputs folder
    json_filename = f"email_{counter}.json"
    output_path = os.path.join(output_folder, json_filename)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f":: Saved: {output_path}")

    counter += 1

print("\n.......All live emails processed successfully!")