import os
import sys

from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from intapp_sdk import IntappIntakeClient
from intapp_sdk.auth import get_intapp_token


def main() -> None:
    load_dotenv()

    base_url = "https://marcum-flow.open.intapp.com/api"
    token = get_intapp_token()
    client = IntappIntakeClient(base_url, token)

    search_term = "Mark Rob"
    print(f"Searching for '{search_term}' in the most recent 200 requests...")
    print("This may take a few minutes as we have to fetch details for each request...")

    matches = client.search_requests_by_answer(search_term, limit=200)

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
        print(f"\nNo requests found with '{search_term}' in the last 50 requests.")


if __name__ == "__main__":
    main()
