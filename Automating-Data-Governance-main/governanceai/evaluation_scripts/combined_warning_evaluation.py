import csv
from pathlib import Path
import os
import time
import json
from collections import defaultdict

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

#loading the file paths for the prompts
SYSTEM_PROMPT_FILE = Path("governanceai/systemprompt.txt")
USER_PROMPT_FILE = Path("governanceai/userprompt.txt")

#load prompts from files
def load_prompts():
    with open(SYSTEM_PROMPT_FILE, 'r', encoding='utf-8') as f:
        system_prompt = f.read()
    with open(USER_PROMPT_FILE, 'r', encoding='utf-8') as f:
        user_template = f.read()
    return system_prompt, user_template

#prompt builder for the evaluation of the rewritten requests
def build_access_request(row):
    return {
        "title": row.get('Project Name', ''),
        "purpose": row.get('Purpose', ''),
        "provider": {
            "dataProductId": row.get('Data Provider', ''),
            "outputPortId": "api"
        },
        "consumer": {
            "teamId": row.get('Consumer Team', ''),
            "data_application_name": row.get('Consumer Name', ''),
            "data_application_description": row.get('Consumer Description', '')
        },
        "expected_decision": "accept"
    }

#LLM function for evaluation
def evaluate(system_prompt, user_template, request):
    user_prompt = user_template.format(
    accessRequest=json.dumps(request, indent=2),
    providerDataProductWithOutputPort="{}",
    providerDataContract="{}",
    providerTeam="{}",
    consumerDataProduct="{}",
    consumerDataContracts="[]",
    consumerTeam="{}",
    policies="Default policies: Data must be used only for stated purpose."
) + "\n\nProvide your response in valid JSON format."
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content)
        warnings = result.get('warnings', [])
        decision = "Accept" if not warnings else "Reject"
        warning_msgs = [w.get('message', str(w)) if isinstance(w, dict) else str(w) for w in warnings]
        return decision, "; ".join(warning_msgs)
    except Exception as e:
        return "Error", str(e)

#loading the file paths

INPUT_CSV = Path("variations_results/warning_combined_variations.csv")   
OUTPUT_CSV = Path("variations_results/warning_evaluation_results.csv")

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

    system_prompt, user_template = load_prompts()
    all_requests = load_csv(INPUT_CSV)

    if not all_requests:
        print("No data found.")
        return

    print(f"Loaded {len(all_requests)} requests")

    results = []

    for idx, row in enumerate(all_requests):
        print(f"\nProcessing request {idx+1}/{len(all_requests)}")
        request = build_access_request(row)
        decision, warnings = evaluate(system_prompt, user_template, request)
        row['AI Decision'] = decision
        row['AI Warnings'] = warnings
        results.append(row)
        time.sleep(0.2)

    # Save the evaluation results to a new CSV file
    if results:
        fieldnames = list(results[0].keys())
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

        end_time = time.time()  # End timing
        print(f"\nEvaluation completed. Results saved to {OUTPUT_CSV}. Time taken: {end_time - start_time:.2f} seconds.")

        # Quick summary
        accepted = sum(1 for r in results if r.get('AI Decision') == 'Accept')
        rejected = sum(1 for r in results if r.get('AI Decision') == 'Reject')
        print(f"Summary: {accepted} Accepted, {rejected} Rejected")

        # Produce a seperate CSV file with summary of results (for presentation purposes)
        summary_csv = Path("warning_evaluation_summary.csv")
        with open(summary_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            writer.writerow(["Variation Type", "Variation Value", "Total", "Accepted", "Rejected", "Acceptance Rate(%)", "Rejection Rate(%)"])
            
            grouped = defaultdict(lambda: {'total': 0, 'accepted': 0, 'rejected': 0})
            
            for r in results:
                vt = r.get('Variation Type', 'unknown')
                vv = r.get('Variation Value', 'unknown')
                key = (vt, vv)
                grouped[key]['total'] += 1
                if r.get('AI Decision') == 'Accept':
                    grouped[key]['accepted'] += 1
                elif r.get('AI Decision') == 'Reject':
                    grouped[key]['rejected'] += 1
            
            for (vt, vv), stats in sorted(grouped.items()):
                total = stats['total']
                acc = stats['accepted']
                rej = stats['rejected']
                acc_rate = (acc / total * 100) if total > 0 else 0
                rej_rate = (rej / total * 100) if total > 0 else 0
                writer.writerow([vt, vv, total, acc, rej, f"{acc_rate:.1f}", f"{rej_rate:.1f}"])
            
            writer.writerow([])
            writer.writerow(["TOTAL", "", len(results), accepted, rejected, 
                            f"{accepted/len(results)*100:.1f}", 
                            f"{rejected/len(results)*100:.1f}"])
        
        print(f"Detailed summary saved to {summary_csv}")

if __name__ == "__main__":
    main()