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

# File paths
SYSTEM_PROMPT_FILE = Path("governanceai/systemprompt.txt")
USER_PROMPT_FILE = Path("governanceai/userprompt.txt")


# Load prompts
def load_prompts():
    with open(SYSTEM_PROMPT_FILE, 'r', encoding='utf-8') as f:
        system_prompt = f.read()
    with open(USER_PROMPT_FILE, 'r', encoding='utf-8') as f:
        user_template = f.read()
    return system_prompt, user_template

# Build request
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

# Evaluate one request
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
    

    
INPUT_CSV = Path("variations_results/combined_variations.csv")
OUTPUT_CSV = Path("variations_results/evaluation_results3.csv")
# Load CSV
def load_csv(csv_path):
    if not csv_path.exists():
        print(f"Warning: {csv_path} not found")
        return []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

# Majority vote
def majority_vote(decisions):
    accept = decisions.count('Accept')
    reject = decisions.count('Reject')
    error = decisions.count('Error')
    
    if error >= 2:
        return 'Error', f"{accept}-{reject}-{error}"
    elif accept > reject:
        return 'Accept', f"{accept}-{reject}"
    elif reject > accept:
        return 'Reject', f"{accept}-{reject}"
    else:
        return 'Tie', f"{accept}-{reject}"

# Main
def main():
    start_time = time.time()
    
    system_prompt, user_template = load_prompts()
    all_requests = load_csv(INPUT_CSV)
    
    if not all_requests:
        print("No data found.")
        return
    
    print(f"Loaded {len(all_requests)} requests. Running each 3 times...")
    
    results = []
    
    for idx, row in enumerate(all_requests):
        print(f"Processing {idx+1}/{len(all_requests)}")
        
        decisions = []
        warnings = []
        
        # Run 3 times
        for run in range(1, 4):
            request = build_access_request(row)
            decision, warning = evaluate(system_prompt, user_template, request)
            decisions.append(decision)
            warnings.append(warning)
            time.sleep(0.2)
        
        # Get majority vote
        final, vote = majority_vote(decisions)
        
        # Build result row
        new_row = dict(row)
        new_row['AI Decision 1'] = decisions[0]
        new_row['AI Decision 2'] = decisions[1]
        new_row['AI Decision 3'] = decisions[2]
        new_row['AI Warning 1'] = warnings[0]
        new_row['AI Warning 2'] = warnings[1]
        new_row['AI Warning 3'] = warnings[2]
        new_row['Vote Count'] = vote
        new_row['Final AI Decision'] = final
        
        results.append(new_row)
    
    # Save results
    if results:
        fieldnames = list(results[0].keys())
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        print(f"\nResults saved to {OUTPUT_CSV}")
        print(f"Time taken: {time.time() - start_time:.2f} seconds")
        
        # Summary
        accepted = sum(1 for r in results if r.get('Final AI Decision') == 'Accept')
        rejected = sum(1 for r in results if r.get('Final AI Decision') == 'Reject')
        ties = sum(1 for r in results if r.get('Final AI Decision') == 'Tie')
        errors = sum(1 for r in results if r.get('Final AI Decision') == 'Error')
        
        print(f"\nSummary:")
        print(f"  Accepted: {accepted}")
        print(f"  Rejected: {rejected}")
        print(f"  Ties: {ties}")
        print(f"  Errors: {errors}")

if __name__ == "__main__":
    main()