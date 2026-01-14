import os
import sys
import logging
from typing import Optional, List, Any
from fastmcp import FastMCP

# Add src to path so we can import the local SDK
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from intapp_sdk import IntappIntakeClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("intapp-mcp")

# Initialize MCP Server
mcp = FastMCP("Intapp Valuation Tools")

# Initialize SDK Client
def get_client():
    BASE_URL = "https://marcum-flow.open.intapp.com/api"
    TOKEN = os.getenv("INTAPP_TOKEN", "INTAPP_TOKEN_REDACTED")
    return IntappIntakeClient(BASE_URL, TOKEN)

@mcp.tool()
def list_valuation_requests(limit: int = 50) -> List[dict]:
    """
    List the most recent intake requests from Intapp.
    """
    client = get_client()
    logger.info(f"Listing {limit} requests")
    return client.list_requests()[:limit]

@mcp.tool()
def get_request_details(request_id: int) -> dict:
    """
    Get full metadata for a specific intake request including answers and status.
    """
    client = get_client()
    logger.info(f"Fetching details for request {request_id}")
    return client.get_request(request_id)

@mcp.tool()
def search_by_team_member(name: str = "Mark Rob", limit: int = 100) -> List[dict]:
    """
    Search for requests where a specific person is assigned to QC, Reviewer, or Analyst roles.
    Useful for finding assignments for specific individuals.
    """
    client = get_client()
    logger.info(f"Searching for user '{name}' in last {limit} requests")
    
    # We use our custom search logic from the SDK
    results = client.search_requests_by_answer(name, limit=limit)
    return results

@mcp.tool()
def download_attachment_to_data_dir(request_id: int, attachment_id: int, filename: str) -> str:
    """
    Downloads an attachment from a request and saves it to the local data directory.
    Returns the full local path to the saved file.
    """
    client = get_client()
    os.makedirs("data", exist_ok=True)
    safe_filename = client.sanitize_filename(filename)
    output_path = os.path.join("data", safe_filename)
    
    logger.info(f"Downloading attachment {attachment_id} to {output_path}")
    client.download_attachment(request_id, attachment_id, output_path)
    return os.path.abspath(output_path)

if __name__ == "__main__":
    mcp.run()
