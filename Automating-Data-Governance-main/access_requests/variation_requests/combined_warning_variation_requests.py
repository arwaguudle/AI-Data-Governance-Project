import csv
from pathlib import Path 
import os
import time

from openai import OpenAI
from dotenv import load_dotenv  

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

seniority_vars = [
    "intern",
    "junior analyst",
    "senior manager",
    "executive/CEO"
]

hastiness_vars = [  
    "very hasty (typos, shorthand, missing punctuation, casual phrasing)",
    "neutral (standard professional, no particular urgency or formality)",
    "very formal (precise legal-style language, complete sentences, no contractions)"
]

def build_combined_prompt(original_purpose, seniority, hastiness):
    return f"""You are an expert in workplace communication.

Rewrite the following data access request as if it was written by a **{seniority}** employee who is **{hastiness}**.

Guidelines:
- {hastiness}
- Preserve the **original meaning** and the **specific data access request**.
- Do not change the underlying request (what data they want and why).
- Only change the tone, wording, and formality.
- Make it appropriate for a {seniority} employee.
- Output ONLY the rewritten request.

Original request:
"{original_purpose}"

Rewritten request (only the rewritten text, no extra explanation):
"""

def rewrite_with_combined(original_purpose, seniority, hastiness):
    prompt = build_combined_prompt(original_purpose, seniority, hastiness)
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error (combined): {e}")
        return ""

INSURANCE_WARNING__CSV = Path("Automating-Data-Governance-main/expert_opinions/insurance-expert_opinion_warnings-suggestions.csv")
ECOMMERCE_WARNING__CSV = Path("Automating-Data-Governance-main/expert_opinions/ecommerce-expert_opinion_warnings-suggestions.csv")
OUTPUT_CSV = Path("variations_results/warning_combined_variation_assessments.csv")

def load_csv(csv_path):
    if not csv_path.exists():
        print(f"Warning: {csv_path} not found")
        return []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)
#MAIN LOOP
def main():
    start_time = time.time()

    insurance_requests = load_csv(INSURANCE_WARNING__CSV)
    ecommerce_requests = load_csv(ECOMMERCE_WARNING__CSV)
    all_requests = insurance_requests + ecommerce_requests

    if not all_requests:
        print("No data found.")
        return

    # Testing for 3 requests before testing it all 
    #all_requests = all_requests[:3]

    print(f"Loading {len(all_requests)} requests")

    results = []

    for idx, row in enumerate(all_requests):
        original = row.get('Purpose', '')
        if not original:
            continue

        print(f"\nProcessing request {idx+1}/{len(all_requests)}")
        original_id = row.get('ID', '')


        original_row = {
            'ID': row.get('ID', ''),
            'Data Provider': row.get('Data Provider', ''),
            'Project Name': row.get('Project Name', ''),
            'Consumer Team': row.get('Consumer Team', ''),
            'Consumer Name': row.get('Consumer Name', ''),
            'Consumer Description': row.get('Consumer Description', ''),
            'Warnings': row.get('Warnings', ''),
            'Suggestion': row.get('Suggestions', ''),
            'Variation Type': 'none',
            'Variation Value': 'none',
            'Purpose': original,
            'Is this warning about the access request correct?': row.get('Is this warning about the access request correct?', ''),
            'How would you rate the provided suggestion?': row.get('How would you rate the provided suggestion?', '')
        }

        results.append((original_row))

        # Generate combined variations (seniority + hastiness)
        for seniority in seniority_vars:
            for hastiness in hastiness_vars:
                print(f"  Combined: {seniority} + {hastiness[:20]}...")
                modified = rewrite_with_combined(original, seniority, hastiness)

                combined_row = {
                    'ID': original_id,
                    'Data Provider': row.get('Data Provider', ''),
                    'Project Name': row.get('Project Name', ''),
                    'Consumer Team': row.get('Consumer Team', ''),
                    'Consumer Name': row.get('Consumer Name', ''),
                    'Consumer Description': row.get('Consumer Description', ''),
                    'Warnings': row.get('Warnings', ''),
                    'Suggestion': row.get('Suggestions', ''),
                    'Variation Type': 'combined',
                    'Variation Value': f"{seniority} + {hastiness}",
                    'Purpose': modified,
                    'Is this warning about the access request correct?': '',
                    'How would you rate the provided suggestion?': ''
                }
                results.append(combined_row)
                time.sleep(0.3)
    #saving results
    if results:
        fieldnames = [
            'ID',
            'Data Provider',
            'Project Name',
            'Consumer Team',
            'Consumer Name',
            'Consumer Description',
            'Warnings',
            'Suggestion',
            'Variation Type',
            'Variation Value',
            'Purpose',
            'Is this warning about the access request correct?',
            'How would you rate the provided suggestion?'
        ]
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Saved {len(results)} rows to {OUTPUT_CSV}")
        end_time = time.time()
        print(f"Generated {len(results)} requests in {end_time - start_time:.2f} seconds.")
    else:
        print("No variations generated")

if __name__ == "__main__":
    main()