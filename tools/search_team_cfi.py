import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from intapp_sdk import IntappIntakeClient

def team_search():
    load_dotenv()
    BASE_URL = "https://marcum-flow.open.intapp.com/api"
    TOKEN = os.getenv("INTAPP_TOKEN", "INTAPP_TOKEN_REDACTED")
    client = IntappIntakeClient(BASE_URL, TOKEN)

    print("Searching for CFI Team requests (Mark Rob as QC or Michael Sloan as Analyst)...")
    print("Excluding Canceled, Complete and Finalized requests.")
    
    try:
        # Use the SDK method which now includes the cancellation and completion filter
        matches = client.get_cfi_team_requests(limit=15, lookback_days=60)
        
        print(f"\nFound {len(matches)} matching (active) requests.")
        print(f"Top 15 Most Recent Team Results:")
        print(client.format_request_table(matches))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    team_search()