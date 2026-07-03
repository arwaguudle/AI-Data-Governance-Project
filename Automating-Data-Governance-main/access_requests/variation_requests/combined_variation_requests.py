import csv
from pathlib import Path 
import os
import time  #To time the execution of the code

#for the AI clients
from openai import OpenAI #using the OpenAI API key
from dotenv import load_dotenv  

# Load environment variables from .env file 
load_dotenv()

# Initialize OpenAI client using the API key from environment
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

#was also told to make a virtual environment (.env)

#setting up the variation instructions
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

#Prompt builder for combined (seniority + hastiness)
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

#LLM function for combined (seniority + hastiness)
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

#gathering the file paths
INSURANCE_CSV = Path("expert_opinions/insurance-expert_assessment.csv")
ECOMMERCE_CSV = Path("expert_opinions/ecommerce-expert_assessment.csv")
OUTPUT_INSURANCE_CSV = Path("variations_results/insurance_combined_variations.csv")
OUTPUT_ECOMMERCE_CSV = Path("variations_results/ecommerce_combined_variations.csv")
JOINT_OUTPUT_CSV = Path("variations_results/combined_variations.csv")

#loading the files
def load_csv(csv_path):
    if not csv_path.exists():
        print(f"Warning: {csv_path} not found")
        return []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

#MAIN LOOP
def main():
    start_time = time.time()  # Start timing

    insurance_requests = load_csv(INSURANCE_CSV)
    ecommerce_requests = load_csv(ECOMMERCE_CSV)

    if not insurance_requests and not ecommerce_requests:
        print("No data found.")
        return

    # Testing for 3 requests before testing it all 
    #insurance_requests = insurance_requests[:3]
    #ecommerce_requests = ecommerce_requests[:3]

    all_insurance_results = []
    all_ecommerce_results = []

    if insurance_requests:
        print(f"Loaded {len(insurance_requests)} insurance requests")
        for idx, row in enumerate(insurance_requests):
            original = row.get('Purpose', '')
            if not original:
                continue

            print(f"\nProcessing insurance request {idx+1}/{len(insurance_requests)}")

            original_id = row.get('ID', '')

            # Original request (no variation)
            original_row = {
                'ID': original_id,
                'Data Provider': row.get('Data Provider', ''),
                'Project Name': row.get('Project Name', ''),
                'Consumer Team': row.get('Consumer Team', ''),
                'Consumer Name': row.get('Consumer Name', ''),
                'Consumer Description': row.get('Consumer Description', ''),
                'Variation Type': 'none',
                'Variation Value': 'none',
                'Purpose': original,
                'Realistic?': row.get('Realistic?', ''),
                'Decision': row.get('Decision?', '')
            }
            all_insurance_results.append(original_row)

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
                        'Variation Type': 'combined',
                        'Variation Value': f"{seniority} + {hastiness}",
                        'Purpose': modified,
                        'Realistic?': '',
                        'Decision': ''
                    }
                    all_insurance_results.append(combined_row)
                    time.sleep(0.3)

    # ECOMMERCE RESULTS
    if ecommerce_requests:
        print(f"Loaded {len(ecommerce_requests)} e-commerce requests")
        for idx, row in enumerate(ecommerce_requests):
            original = row.get('Purpose', '')
            if not original:
                continue

            print(f"\nProcessing e-commerce request {idx+1}/{len(ecommerce_requests)}")

            original_id = row.get('ID', '')

            # Original request (no variation)
            original_row = {
                'ID': original_id,
                'Data Provider': row.get('Data Provider', ''),
                'Project Name': row.get('Project Name', ''),
                'Consumer Team': row.get('Consumer Team', ''),
                'Consumer Name': row.get('Consumer Name', ''),
                'Consumer Description': row.get('Consumer Description', ''),
                'Variation Type': 'None',
                'Variation Value': 'Original Request',
                'Purpose': original,
                'Realistic?': row.get('Realistic?', ''),
                'Decision': row.get('Decision?', '')
            }
            all_ecommerce_results.append(original_row)

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
                        'Variation Type': 'combined',
                        'Variation Value': f"{seniority} + {hastiness}",
                        'Purpose': modified,
                        'Realistic?': '',
                        'Decision': ''
                    }
                    all_ecommerce_results.append(combined_row)
                    time.sleep(0.3)

    # INSURANCE RESULTS
    if all_insurance_results:
        fieldnames = [
            'ID',
            'Data Provider',
            'Project Name',
            'Consumer Team',
            'Consumer Name',
            'Consumer Description',
            'Variation Type',
            'Variation Value',
            'Purpose',
            'Realistic?',
            'Decision'
        ]
        OUTPUT_INSURANCE_CSV.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_INSURANCE_CSV, 'w', newline='', encoding='utf-8') as f: #Saving the insurance results
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_insurance_results)
        print(f"Saved {len(all_insurance_results)} rows to {OUTPUT_INSURANCE_CSV}")

    # Saving the ecommerce results
    if all_ecommerce_results:
        OUTPUT_ECOMMERCE_CSV.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_ECOMMERCE_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_ecommerce_results)
        print(f"Saved {len(all_ecommerce_results)} rows to {OUTPUT_ECOMMERCE_CSV}")


    # JOINT RESULTS (combine both)
    all_results = all_insurance_results + all_ecommerce_results
    if all_results:
        JOINT_OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
        with open(JOINT_OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_results)
        print(f"Saved {len(all_results)} rows to {JOINT_OUTPUT_CSV}")

    end_time = time.time()  # End timing
    total_results = len(all_insurance_results) + len(all_ecommerce_results)
    print(f"Generated {total_results} total requests in {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    main()