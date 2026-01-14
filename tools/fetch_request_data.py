import argparse
import sys
import os
import re

"""
Fetch Request Data Tool
-----------------------
A unified tool to retrieve various details about an Intapp request.
Combines functionality for retrieving People, Dates, Valuation Details,
General Info, and Financials (Fee/Materiality).

Usage:
    python tools/fetch_request_data.py <REQUEST_ID> [options]

Options:
    --all           Fetch all available data (default)
    --people        Fetch team and personnel info
    --dates         Fetch key dates
    --valuation     Fetch technical valuation details
    --general       Fetch general scope and client info
    --financials    Fetch fee and materiality info
"""

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from intapp_sdk import IntappIntakeClient
from intapp_sdk.auth import get_intapp_token

def parse_name_email(value):
    """Parses 'Name (email)' format into separate components."""
    if not value or value == "None":
        return None, None
    match = re.search(r'(.*?)\s*\((.*?@.*?)\)', value)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return value.strip(), None

def get_answers_map(request):
    return {ans.get('questionName'): ans for ans in request.get('answers', [])}

def print_section(title, data):
    print(f"\n[{title}]")
    print("-" * 60)
    for k, v in data.items():
        if isinstance(v, list):
            print(f"{k}:")
            for item in v:
                if isinstance(item, dict):
                    # specific formatting for people list
                    print(f"  - Name: {item.get('name', 'N/A'):<25} Email: {item.get('email', 'N/A')}")
                else:
                    print(f"  - {item}")
        elif isinstance(v, dict):
             # specific formatting for single person
             print(f"{k:<25}: {v.get('name', 'N/A')}")
             if v.get('email'):
                 print(f"{ ' ' * 27}Email: {v.get('email')}")
        else:
            # Handle long text
            val_str = str(v)
            if len(val_str) > 80:
                print(f"{k}:")
                print(f"  {val_str}")
            else:
                print(f"{k:<25}: {v}")

def fetch_people(request, answers):
    people_data = {}
    
    # Creator
    creator = request.get('requestedBy') or request.get('createdBy')
    people_data['Creator'] = {'name': creator, 'email': None}

    # Helper
    def process(key, label):
        val = answers.get(key, {}).get('displayValue')
        n, e = parse_name_email(val)
        people_data[label] = {'name': n, 'email': e}

    process('ARI - Partner Assigned', 'CVG QC')
    process('ARI - Assigned Analyst', 'CVG Analyst')
    process('ARI - Engagement Partner', 'Engagement Shareholder')
    process('ARI - Engagement Quality Reviewer', 'Engagement Quality Reviewer')

    # Additional Analysts
    add_analysts = answers.get('ARI - Additional Analyst', {}).get('displayValue')
    people_data['Additional Analysts'] = []
    if add_analysts and add_analysts != "None":
        for p in add_analysts.split(','):
             n, e = parse_name_email(p)
             people_data['Additional Analysts'].append({'name': n, 'email': e})

    # Other Audit Team
    team = answers.get('RSD - Engagement Team Members', {}).get('displayValue')
    people_data['Other Audit Team'] = []
    if team and team != "None":
        for p in team.split(','):
             n, e = parse_name_email(p)
             people_data['Other Audit Team'].append({'name': n, 'email': e})
             
    return people_data

def fetch_dates(request, answers):
    dates = {}
    # Helper to find value even if key is slightly different (though map keys are exact from API)
    # We use the exact keys found in previous dumps
    
    def get_val(key):
        return answers.get(key, {}).get('displayValue') or "Not found"

    dates["Valuation Date"] = get_val("ARI - ValuationDate")
    dates["Docs Upload Expected"] = get_val("ARI - DeliverabletoMVG")
    dates["Requested Due Date"] = get_val("ARI - Due Date")
    dates["Issuance/Filing Date"] = get_val("ARI - Filing Date")
    dates["Planning Meeting Date"] = get_val("ARI - Planning Date")
    
    return dates

def fetch_valuation(request, answers):
    def get_val(key):
        return answers.get(key, {}).get('displayValue') or "Not specified"

    return {
        "Valuation Category": get_val('ARI - Category'),
        "Valuation Type": get_val('ARI - SubType') if get_val('ARI - SubType') != "Not specified" else get_val('ARI - ValuationOtherType'),
        "Monte Carlo Sim?": get_val('ARI - Monte Carlo'),
        "Reporting Framework": get_val('RSD - Accounting Basis') if get_val('RSD - Accounting Basis') != "Not specified" else get_val('ARI - FrameworkOther'),
        "Applicable Standards": get_val('ARI - Standard'),
        "Balance Sheet Class": get_val('ARI - ClassType'),
        "Specialist Firm": get_val('ARI - Appraisal Firm') if get_val('ARI - Appraisal Firm') != "Not specified" else get_val('ARI - Appraiser')
    }

def fetch_general(request, answers):
    def get_val(key, default="Not specified"):
        return answers.get(key, {}).get('displayValue') or default

    return {
        "Client Name": request.get('clientName') or get_val('ARI - Client Name'),
        "Public Company": get_val('ARI - Public Company', "No"),
        "Ticker": get_val('ARI - PublicTicker', "N/A"),
        "Current State": request.get('currentState'),
        "Created Date": request.get('createdOn'),
        "Scope": get_val('ARI - Scope'),
        "Document Matters": get_val('ARI - Informmatters', "None"),
        "Expected Deliverable": get_val('ARI - ExpecftedDeliverable'),
        "Docs Provided Now?": get_val('ARI - PBCBeforehand', "Unknown")
    }

def fetch_financials(request, answers):
    def get_val(key):
        # Prefer displayValue, fallback to numeric/text
        a = answers.get(key, {})
        return a.get('displayValue') or a.get('numericAnswer') or a.get('textAnswer') or "Not found"

    return {
        "Fee": get_val("ARI - Fee"),
        "Materiality (Trivial)": get_val("ARI - Materiality Trivial"),
        "Materiality (Perf)": get_val("ARI - Materiality Performance")
    }

def main():
    parser = argparse.ArgumentParser(description="Fetch unified data for an Intapp Request.")
    parser.add_argument("request_id", type=int, help="The Request ID")
    parser.add_argument("--all", action="store_true", help="Fetch all sections (default)")
    parser.add_argument("--people", action="store_true", help="Fetch people/team info")
    parser.add_argument("--dates", action="store_true", help="Fetch key dates")
    parser.add_argument("--valuation", action="store_true", help="Fetch valuation details")
    parser.add_argument("--general", action="store_true", help="Fetch general info")
    parser.add_argument("--financials", action="store_true", help="Fetch fee and materiality")
    parser.add_argument("--attachments", action="store_true", help="Fetch attachment list")
    
    args = parser.parse_args()
    
    # Default to all if no specific flag set
    if not any([args.people, args.dates, args.valuation, args.general, args.financials, args.attachments]):
        args.all = True

    base_url = "https://marcum-flow.open.intapp.com/api"
    try:
        token = get_intapp_token()
    except Exception as e:
        print(f"Authentication Error: {e}")
        return

    client = IntappIntakeClient(base_url, token)
    
    print(f"Fetching data for Request {args.request_id}...")
    request = client.get_request(args.request_id)
    
    if not request:
        print("Request not found.")
        return

    answers_map = get_answers_map(request)

    if args.all or args.general:
        data = fetch_general(request, answers_map)
        print_section("General Info", data)

    if args.all or args.dates:
        data = fetch_dates(request, answers_map)
        print_section("Key Dates", data)

    if args.all or args.people:
        data = fetch_people(request, answers_map)
        print_section("People & Team", data)

    if args.all or args.financials:
        data = fetch_financials(request, answers_map)
        print_section("Financials", data)

    if args.all or args.valuation:
        data = fetch_valuation(request, answers_map)
        print_section("Valuation Details", data)

    if args.all or args.attachments:
        atts = request.get('attachments', [])
        print(f"\n[Attachments] (Count: {len(atts)})")
        print("-" * 60)
        if atts:
            for att in atts:
                name = att.get('fileName') or att.get('name') or "Unknown"
                print(f"  - {name} (ID: {att.get('id')})")
        else:
            print("  No attachments found.")

if __name__ == "__main__":
    main()
