import json
import sys
import re

# Set UTF-8 encoding for stdout
sys.stdout.reconfigure(encoding='utf-8')

# Read the JSON data
with open(r'C:\Users\MRob0\.cursor\projects\c-Users-MRob0-Dev-Intapp\agent-tools\35585325-0777-409b-89bd-f4ab2f754ac3.txt', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Filter for valuation requests
valuation_requests = [r for r in data if r.get('requestType') == 'Valuation Request']

# Sort by createdOn descending (newest creation date first)
sorted_requests = sorted(valuation_requests, key=lambda x: x.get('createdOn', ''), reverse=True)

# Get top 5
top5 = sorted_requests[:5]

print("\n5 Newest Valuation Requests (by Creation Date):\n")
print("=" * 100)

for i, req in enumerate(top5, 1):
    req_id = req.get('id', 'N/A')
    name = req.get('name', 'N/A')
    # Remove zero-width spaces and other special characters
    name = re.sub(r'[\u200b-\u200f\u202a-\u202e]', '', name)
    status = req.get('status', 'N/A')
    created = req.get('createdOn', 'N/A')[:10] if req.get('createdOn') else 'N/A'
    modified = req.get('modifiedOn', 'N/A')[:10] if req.get('modifiedOn') else 'N/A'
    client_name = req.get('clientName', '') or 'N/A'
    office = req.get('office', '') or 'N/A'
    
    print(f"\n{i}. Request #{req_id}")
    print(f"   Name: {name}")
    print(f"   Client: {client_name}")
    print(f"   Office: {office}")
    print(f"   Status: {status}")
    print(f"   Created: {created}")
    print(f"   Last Modified: {modified}")

print("\n" + "=" * 100)
