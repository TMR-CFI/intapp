import os
import sys
from dotenv import load_dotenv
from collections import Counter

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from intapp_sdk import IntappIntakeClient

def main():
    load_dotenv()
    
    BASE_URL = "https://marcum-flow.open.intapp.com/api"
    TOKEN = os.getenv("INTAPP_TOKEN", "INTAPP_TOKEN_REDACTED")
    
    client = IntappIntakeClient(BASE_URL, TOKEN)
    
    print("Analyzing current Intapp workload (InProgress Valuation Requests)...")
    
    try:
        # Fetch a large batch of valuation requests modified in the last 60 days
        from datetime import datetime, timedelta
        sixty_days_ago = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%dT%H:%M:%S")
        
        requests = client.list_requests(
            limit=1000,
            modified_from=sixty_days_ago
        )
        
        # Filter for InProgress
        active_requests = [r for r in requests if r.get('status') == "InProgress"]
        
        if not active_requests:
            print("No InProgress requests found in the last 60 days.")
            return

        print(f"\nSummary of {len(active_requests)} Active Requests:")
        print("-" * 60)
        
        # Breakdown by Current State
        state_counts = Counter(r.get('currentState', 'Unknown') for r in active_requests)
        print(f"{ 'Current State':<40} | {'Count'}")
        print("-" * 60)
        for state, count in state_counts.most_common():
            print(f"{state:<40} | {count}")
            
        # Optional: Show the top 5 oldest active requests
        print("\nTop 5 Oldest Active Requests (Might need attention):")
        active_requests.sort(key=lambda x: x.get('createdOn', ''))
        print(client.format_request_table(active_requests[:5]))
        
    except Exception as e:
        print(f"Error during analysis: {e}")

if __name__ == "__main__":
    main()
