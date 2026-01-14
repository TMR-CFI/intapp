import os
import sys
import json

# Add src to path
sys.path.append(os.path.abspath('src'))
from intapp_sdk import IntappIntakeClient

def main():
    BASE_URL = "https://marcum-flow.open.intapp.com/api"
    TOKEN = os.getenv("INTAPP_TOKEN", "INTAPP_TOKEN_REDACTED")
    
    client = IntappIntakeClient(BASE_URL, TOKEN)
    
    print("Fetching absolute most recent valuation requests...")
    try:
        # Defaults to 'Valuation Request' automatically now
        # Filtering for records modified since 2026-01-01
        valuation_requests = client.list_requests(
            modified_from="2026-01-01T00:00:00"
        )
        
        # Sort by createdOn descending
        valuation_requests.sort(key=lambda x: x.get('createdOn', ''), reverse=True)
        
        print(f"\nFound {len(valuation_requests)} Valuation Requests modified since 2026-01-01.")
        print(client.format_request_table(valuation_requests[:5]))
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
