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
            base_filename = client.sanitize_filename(data['name'])
            filename = f"{base_filename}.yaml"
            
            # Setup directories
            os.makedirs('../data', exist_ok=True)
            attachment_dir = os.path.join('../data', f"{base_filename}_attachments")
            os.makedirs(attachment_dir, exist_ok=True)
            
            filepath = os.path.join('../data', filename)
            
            # Save YAML metadata
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, sort_keys=False, default_flow_style=False)
            
            print(f"Successfully saved metadata to {filepath}")

            # Download Attachments
            attachments = data.get('attachments', [])
            if attachments:
                print(f"Downloading {len(attachments)} attachments...")
                for att in attachments:
                    att_id = att['id']
                    att_name = client.sanitize_filename(att['name'])
                    att_path = os.path.join(attachment_dir, att_name)
                    
                    try:
                        client.download_attachment(request_id, att_id, att_path)
                        print(f"  - Downloaded: {att['name']}")
                    except Exception as e:
                        print(f"  - Failed to download {att['name']}: {e}")
            else:
                print("No attachments found.")
        else:
            print("Request not found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
