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

### Running Examples
You can run the provided example to see the SDK in action:
```bash
python examples/fetch_request.py
```

## AI Agent Integration



### MCP Server (Model Context Protocol)

This SDK includes a built-in MCP server that allows AI agents (like Claude Desktop) to use Intapp tools directly.



**Available Tools:**

- `list_valuation_requests`: View recent intake activity.

- `get_request_details`: Get full details for a specific request.

- `search_by_team_member`: Find requests assigned to specific people (e.g., "Mark Rob").

- `download_attachment_to_data_dir`: Programmatically download files for analysis.



#### How to use with Claude Desktop:

Add the following to your `claude_desktop_config.json`:



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
