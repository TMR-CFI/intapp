import os
import sys
import argparse
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from intapp_sdk import IntappIntakeClient

def search_for_qc(client, user_name, limit=500):
    print(f"Searching for '{user_name}' in CVG QC fields...")
    print(f"Fetching most recent {limit} requests...")
    
    requests_list = client.list_requests()[:limit]
    matches = []
    
    def process_req(req):
        req_id = req['id']
        try:
            detail = client.get_request(req_id)
            if not detail:
                return None
            
            # Fields that could represent 'QC'
            qc_fields = [
                'ARI - Engagement Quality Reviewer',
                'ARI - Previous Reviewer',
                'ARI - QC Reviewer' # Guessing
            ]
            
            found = False
            for a in detail.get('answers', []):
                q_name = a.get('questionName')
                val = str(a.get('displayValue', ''))
                
                # Check if it matches 'Mark Rob' in any of the suspected QC fields
                if user_name.lower() in val.lower():
                    # If it's one of our suspected fields, or contains 'QC' or 'Reviewer'
                    if q_name in qc_fields or 'QC' in q_name or 'Reviewer' in q_name:
                        return {
                            'id': req_id,
                            'name': req['name'],
                            'field': q_name,
                            'value': val,
                            'status': detail.get('status')
                        }
            return None
        except:
            return None

    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(process_req, requests_list))
        matches = [r for r in results if r]
        
    return matches

def main():

    load_dotenv()

    BASE_URL = "https://marcum-flow.open.intapp.com/api"

    TOKEN = os.getenv("INTAPP_TOKEN", "INTAPP_TOKEN_REDACTED")



    client = IntappIntakeClient(BASE_URL, TOKEN)

    

    user_to_find = "Mark Rob"

    results = search_for_qc(client, user_to_find, limit=1000)



    if results:

        print(f"\nFound {len(results)} requests where '{user_to_find}' is in a QC/Reviewer field:")

        print("-" * 100)

        print(f"{'ID':<10} | {'Status':<15} | {'Field':<35} | {'Request Name'}")

        print("-" * 100)

        for r in results:

            print(f"{r['id']:<10} | {r['status']:<15} | {r['field']:<35} | {r['name'][:50]}")

            

        # Save to data directory

        import yaml

        os.makedirs('../data', exist_ok=True)

        output_file = f"../data/qc_requests_{user_to_find.replace(' ', '_')}.yaml"

        with open(output_file, 'w', encoding='utf-8') as f:

            yaml.dump(results, f, sort_keys=False)

        print(f"\nResults saved to {output_file}")

    else:

        print(f"\nNo requests found for '{user_to_find}' in the last 1000 entries.")



if __name__ == "__main__":
    main()
