import os
import sys
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from intapp_sdk import IntappIntakeClient
from intapp_sdk.auth import get_intapp_token


def search_for_qc(client: IntappIntakeClient, user_name: str, limit: int = 500):
    print(f"Searching for '{user_name}' in CVG QC fields...")
    print(f"Fetching most recent {limit} requests...")

    requests_list = client.list_requests()[:limit]

    def process_req(req):
        req_id = req["id"]
        try:
            detail = client.get_request(req_id)
            if not detail:
                return None

            qc_fields = [
                "ARI - Engagement Quality Reviewer",
                "ARI - Previous Reviewer",
                "ARI - QC Reviewer",
            ]

            for a in detail.get("answers", []):
                q_name = a.get("questionName") or ""
                val = str(a.get("displayValue", "") or "")

                if user_name.lower() in val.lower():
                    if q_name in qc_fields or "QC" in q_name or "Reviewer" in q_name:
                        return {
                            "id": req_id,
                            "name": req["name"],
                            "field": q_name,
                            "value": val,
                            "status": detail.get("status"),
                        }
            return None
        except Exception:
            return None

    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(process_req, requests_list))

    return [r for r in results if r]


def main() -> None:
    load_dotenv()

    base_url = "https://marcum-flow.open.intapp.com/api"
    token = get_intapp_token()
    client = IntappIntakeClient(base_url, token)

    user_to_find = "Mark Rob"
    results = search_for_qc(client, user_to_find, limit=1000)

    if results:
        print(f"\nFound {len(results)} requests where '{user_to_find}' is in a QC/Reviewer field:")
        print("-" * 100)
        print(f"{'ID':<10} | {'Status':<15} | {'Field':<35} | {'Request Name'}")
        print("-" * 100)
        for r in results:
            print(f"{r['id']:<10} | {r['status']:<15} | {r['field']:<35} | {r['name'][:50]}")

        import yaml

        os.makedirs("../data", exist_ok=True)
        output_file = f"../data/qc_requests_{user_to_find.replace(' ', '_')}.yaml"
        with open(output_file, "w", encoding="utf-8") as file:
            yaml.dump(results, file, sort_keys=False)
        print(f"\nResults saved to {output_file}")
    else:
        print(f"\nNo requests found for '{user_to_find}' in the last 1000 entries.")


if __name__ == "__main__":
    main()
