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
    
    print("Fetching 5 most recent requests...")
    try:
        requests = client.list_requests()[:5]
        for r in requests:
            print(f"ID: {r['id']} | Status: {r['status']} | Name: {r['name']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
