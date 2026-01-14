# Intapp Valuation SDK

A Python-based SDK for interacting with the Intapp Intake API. This tool is designed to be used by both human developers and AI agents to programmatically manage and query valuation requests.

## Project Structure
- `src/intapp_sdk/`: Core SDK logic and API client.
- `docs/`: API documentation including the full `swagger.json` specification.
- `examples/`: Example scripts showing how to use the SDK.
- `data/`: Local storage for fetched request metadata and attachments (git-ignored).
- `tests/`: Unit and integration tests.

## Setup
1. **Install dependencies**:
   ```bash
   pip install requests pyyaml python-dotenv
   ```
2. **Configure Authentication**:
   Set your API token as an environment variable or in a `.env` file:
   ```powershell
   # PowerShell
   $env:INTAPP_TOKEN="your_token_here"
   ```

## Usage

### Basic Initialization
```python
import os
from intapp_sdk import IntappIntakeClient

token = os.getenv("INTAPP_TOKEN")
client = IntappIntakeClient("https://marcum-flow.open.intapp.com/api", token)
```

### Fetch and Download a Request
The SDK supports fetching full request metadata and downloading all associated attachments (automatically decoded from Base64).

```python
# Fetch metadata
request = client.get_request(531311)
print(f"Processing: {request['name']}")

# Download an attachment
# This uses the 'includeContent=true' flag internally
client.download_attachment(531311, 527948, "memo.pdf")
```

## Tools
The repository includes several specialized tools in the `tools/` and `examples/` directories:

### Core Tools (`tools/`)
- **`list_recent_requests.py`**: A generic tool to list the N most recent requests.
  - Usage: `python tools/list_recent_requests.py -n 25`
  - Defaults to "Valuation Request" type and last 30 days of activity.
- **`analyze_workload.py`**: Provides a summary of all `InProgress` valuation requests grouped by their current workflow state.
  - Usage: `python tools/analyze_workload.py`

### Examples (`examples/`)
- **`fetch_request.py`**: Fetches a single request and downloads all its attachments.
- **`get_qc_requests.py`**: A discovery tool that searches for requests assigned to specific individuals (e.g., "Mark Rob") in QC/Reviewer roles.

## AI Agent Integration



### MCP Server & Tool Registry

This repository is "Agent-Ready." The file `src/intapp_sdk/mcp_server.py` serves as the primary **Tool Registry**. 



**Instructions for AI Agents:**

> When interacting with this repository, please refer to `src/intapp_sdk/mcp_server.py` to understand the available tools. Use the `@mcp.tool()` definitions as the authoritative guide for function signatures and purposes.



**Available Tools:**



- `open_request_in_browser`: Opens a specific Intapp request ID in the default web browser.



- `get_cfi_team_requests`: Get the most recent requests for Mark Rob (QC) or Michael Sloan (Analyst).







- `list_valuation_requests`: View recent intake activity.





- `get_request_details`: Get full details for a specific request.

- `search_by_team_member`: Find requests assigned to specific people (e.g., "Mark Rob").

- `download_attachment_to_data_dir`: Programmatically download files for analysis.



#### Configuration for External AI Hosts (Claude Desktop, Cursor, Roo Code):

Add the following to your configuration:





```json

{

  "mcpServers": {

    "intapp": {

      "command": "python",

      "args": [

        "C:/Users/MRob0/dev/intapp/src/intapp_sdk/mcp_server.py"

      ],

      "env": {

        "INTAPP_TOKEN": "your_token_here"

      }

    }

  }

}

```



## Discovery

Agents can use `list_requests()` to identify new work.
