import argparse
import sys
import os

"""
Download Request Files Tool
---------------------------
Downloads all attachments for a specific Intapp request.
Files are saved to a directory named 'downloads_<request_id>' by default,
or a custom directory if specified.

Usage:
    python tools/download_request_files.py <REQUEST_ID> [--output-dir <DIR>]

Example:
    python tools/download_request_files.py 528623
"""

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from intapp_sdk import IntappIntakeClient
from intapp_sdk.auth import get_intapp_token

def main():
    parser = argparse.ArgumentParser(description="Download all attachments for an Intapp Request.")
    parser.add_argument("request_id", type=int, help="The Request ID")
    parser.add_argument("--output-dir", help="Directory to save files (default: downloads_<request_id>)")
    
    args = parser.parse_args()
    
    # Determine output directory
    if args.output_dir:
        output_dir = args.output_dir
    else:
        output_dir = os.path.join(os.getcwd(), f"downloads_{args.request_id}")

    base_url = "https://marcum-flow.open.intapp.com/api"
    try:
        token = get_intapp_token()
    except Exception as e:
        print(f"Authentication Error: {e}")
        return

    client = IntappIntakeClient(base_url, token)
    
    print(f"Fetching request {args.request_id}...")
    # We verify request exists first
    req = client.get_request(args.request_id)
    if not req:
        print("Request not found.")
        return

    count = len(req.get('attachments', []))
    print(f"Found {count} attachments.")
    
    if count == 0:
        return

    print(f"Downloading to: {output_dir}")
    try:
        downloaded = client.download_all_attachments(args.request_id, output_dir)
        print(f"\nSuccessfully downloaded {len(downloaded)} files:")
        for path in downloaded:
            print(f" - {os.path.basename(path)}")
    except Exception as e:
        print(f"Error downloading files: {e}")

if __name__ == "__main__":
    main()
