import torch
import json
from transformers import AutoModelForCausalLM, AutoTokenizer
from email_fetcher import fetch_next_pending_email

# -------------------------
# Paths
# -------------------------
BASE_MODEL_PATH = "gemma2b_model"
MERGED_WEIGHTS_PATH = "gemma_merged_model.pt"
OUTPUT_DIR = "outputs"   # folder for multiple JSONs

import os
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------
# Load tokenizer & model
# -------------------------
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_PATH)

model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL_PATH,
    dtype=torch.float32,
)

state_dict = torch.load(MERGED_WEIGHTS_PATH, map_location="cpu")
model.load_state_dict(state_dict)
model.eval()

print("........Model loaded.\n........Starting email processing.\n")


counter = 1

while True:
    email_text = fetch_next_pending_email()

    if not email_text:
        print("......No more pending emails. Exiting.")
        break

    print(f"\n......Processing email #{counter}")

    prompt = f"""### Instruction:
You are an information extraction system.

Extract travel booking details from the email, correct grammar and spelling mistakes,
and return ONLY valid JSON.

JSON format:
{{
  "full_name": "",
  "email": "",
  "phone": "",
  "tour_start_date": "",
  "tour_end_date": "",
  "city_to_travel": "",
  "country_to_travel": "",
  "arrival_at_airport": "",
  "departure_port": "",
  "number_of_adults": "",
  "number_of_males": "",
  "number_of_females": "",
  "number_of_children": "",
  "age_of_children": "",
  "number_of_infant": "",
  "suggested_hotel": "",
  "suggested_restaurants": "",
  "attractions_to_visit": ""
}}

### Input:
{email_text}

### Response:
"""

    inputs = tokenizer(prompt, return_tensors="pt")

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=450,
            do_sample=False
        )

    decoded_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
    response_part = decoded_output.split("### Response:")[-1].strip()

    try:
        start = response_part.index("{")
        end = response_part.rindex("}") + 1
        json_text = response_part[start:end]
        extracted_data = json.loads(json_text)

        print("..... JSON extracted")

    except Exception as e:
        extracted_data = {
            "raw_output": response_part,
            "error": str(e)
        }
        print("..... JSON parsing failed")

    output_path = os.path.join(OUTPUT_DIR, f"email_{counter}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(extracted_data, f, indent=4, ensure_ascii=False)

    print(f":: Saved: {output_path}")

    counter += 1
print("\n......All emails processed.")