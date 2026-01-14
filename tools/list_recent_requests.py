import os
import sys
import argparse
from dotenv import load_dotenv

# Set UTF-8 encoding for stdout
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from intapp_sdk import IntappIntakeClient

def main():
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="List recent Intapp requests.")
    parser.add_argument("-n", "--count", type=int, default=15, help="Number of requests to return (default: 15)")
    parser.add_argument("-t", "--type", type=str, default="Valuation Request", help="Request type to filter by (default: 'Valuation Request')")
    parser.add_argument("--all", action="store_true", help="List all request types (ignores -t)")
    
    args = parser.parse_args()

    BASE_URL = "https://marcum-flow.open.intapp.com/api"
    TOKEN = os.getenv("INTAPP_TOKEN", "INTAPP_TOKEN_REDACTED")
    
    client = IntappIntakeClient(BASE_URL, TOKEN)
    
    req_type = None if args.all else [args.type]
    type_display = "All Types" if args.all else args.type
    
    # Calculate a date 30 days ago to ensure we get recent items
    from datetime import datetime, timedelta
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S")
    
    print(f"Fetching the {args.count} most recent requests ({type_display})...")
    
    try:
        # Fetch a large batch since 30 days ago to ensure accurate local sorting
        requests = client.list_requests(
            limit=1000,
            request_types=req_type,
            modified_from=thirty_days_ago
        )
        
        # Sort by createdOn descending
        requests.sort(key=lambda x: x.get('createdOn', ''), reverse=True)
        
        print(f"\nFound {len(requests)} matching requests modified recently.")
        print(f"\n{args.count} Most Recent Results:")
        print(client.format_request_table(requests[:args.count]))
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
