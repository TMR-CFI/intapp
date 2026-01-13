import os
import yaml
import sys
from dotenv import load_dotenv

# Add src to path so we can import the SDK
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from intapp_sdk import IntappIntakeClient

def main():
    # Recommended: Move your token to an environment variable or .env file
    BASE_URL = "https://marcum-flow.open.intapp.com/api"
    BEARER_TOKEN = os.getenv("INTAPP_TOKEN", "INTAPP_TOKEN_REDACTED")

    client = IntappIntakeClient(BASE_URL, BEARER_TOKEN)
    
    request_id = 531311
    print(f"Fetching request {request_id}...")
    
    try:
        data = client.get_request(request_id)
        if data:
            filename = f"{client.sanitize_filename(data['name'])}.yaml"
            # Save to the data directory
            os.makedirs('../data', exist_ok=True)
            filepath = os.path.join('../data', filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, sort_keys=False, default_flow_style=False)
            
            print(f"Successfully saved to {filepath}")
        else:
            print("Request not found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
