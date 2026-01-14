import os
import sys
import json
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from intapp_sdk import IntappIntakeClient

def main():
    load_dotenv()
    BASE_URL = "https://marcum-flow.open.intapp.com/api"
    TOKEN = os.getenv("INTAPP_TOKEN", "INTAPP_TOKEN_REDACTED")

    client = IntappIntakeClient(BASE_URL, TOKEN)
    
    SEARCH_TERM = "Mark Rob"
    print(f"Searching for '{SEARCH_TERM}' in the most recent 200 requests...")
    print("This may take a few minutes as we have to fetch details for each request...")
    
    matches = client.search_requests_by_answer(SEARCH_TERM, limit=200)

    if matches:
        print(f"\nFound {len(matches)} matches:")
        print("-" * 80)
        for m in matches:
            print(f"Request ID: {m['request_id']}")
            print(f"Name      : {m['request_name']}")
            print(f"Field     : {m['field_name']}")
            print(f"Value     : {m['value']}")
            print("-" * 80)
    else:
        print(f"\nNo requests found with '{SEARCH_TERM}' in the last 50 requests.")

if __name__ == "__main__":
    main()
