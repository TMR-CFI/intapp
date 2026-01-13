# Intapp Valuation SDK

A Python-based SDK for interacting with the Intapp Intake API. This tool is designed to be used by both human developers and AI agents to programmatically manage and query valuation requests.

## Structure
- `src/intapp_sdk/`: Core SDK logic.
- `examples/`: Example scripts showing how to use the SDK.
- `data/`: Local storage for fetched request data (git-ignored).
- `tests/`: Unit and integration tests.

## Setup
1. Install dependencies:
   ```bash
   pip install requests pyyaml
   ```
2. Set your API token as an environment variable:
   ```bash
   $env:INTAPP_TOKEN="your_token_here"
   ```

## Usage
```python
from intapp_sdk import IntappIntakeClient

client = IntappIntakeClient("https://marcum-flow.open.intapp.com/api", "your_token")
request = client.get_request(531311)
print(request['name'])
```

## AI Agent Integration
This SDK is structured to be easily discoverable by AI agents. Agents can use `client.list_requests()` to scan for work and `client.get_request(id)` to extract specific details from YAML or JSON.
