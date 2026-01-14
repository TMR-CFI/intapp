import os
import sys

import yaml

# Add src to path so we can import the SDK
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from intapp_sdk import IntappIntakeClient
from intapp_sdk.auth import get_intapp_token


def main() -> None:
    base_url = "https://marcum-flow.open.intapp.com/api"
    bearer_token = get_intapp_token()

    client = IntappIntakeClient(base_url, bearer_token)

    request_id = 531311
    print(f"Fetching request {request_id}...")

    try:
        data = client.get_request(request_id)
        if not data:
            print("Request not found.")
            return

        base_filename = client.sanitize_filename(data["name"])
        filename = f"{base_filename}.yaml"

        os.makedirs("../data", exist_ok=True)
        attachment_dir = os.path.join("../data", f"{base_filename}_attachments")
        os.makedirs(attachment_dir, exist_ok=True)

        filepath = os.path.join("../data", filename)

        with open(filepath, "w", encoding="utf-8") as file:
            yaml.dump(data, file, sort_keys=False, default_flow_style=False)

        print(f"Successfully saved metadata to {filepath}")

        attachments = data.get("attachments", [])
        if not attachments:
            print("No attachments found.")
            return

        print(f"Downloading {len(attachments)} attachments...")
        for attachment in attachments:
            attachment_id = attachment["id"]
            attachment_name = client.sanitize_filename(attachment["name"])
            attachment_path = os.path.join(attachment_dir, attachment_name)

            try:
                client.download_attachment(request_id, attachment_id, attachment_path)
                print(f"  - Downloaded: {attachment['name']}")
            except Exception as exc:
                print(f"  - Failed to download {attachment['name']}: {exc}")
    except Exception as exc:
        print(f"Error: {exc}")


if __name__ == "__main__":
    main()
