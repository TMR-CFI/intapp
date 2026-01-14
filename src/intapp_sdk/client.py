import requests
import re
import json
import logging

logger = logging.getLogger(__name__)

class IntappIntakeClient:
    """
    A programmatic interface for the Intapp Intake API.
    Designed for use by both human developers and AI Agents.
    """
    def __init__(self, base_url, token):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

    def list_requests(self, limit=1000, skip=0, request_types=None, modified_from=None):
        """
        Retrieves a list of intake requests with optional filtering.
        Defaults to 'Valuation Request' if no type is specified.
        """
        url = f"{self.base_url}/api/intake/v1/requests"
        
        # Default to Valuation Request if none provided
        if request_types is None:
            request_types = ["Valuation Request"]
            
        params = {
            'filter.rowsToTake': limit,
            'filter.rowsToSkip': skip
        }
        
        if request_types:
            params['filter.requestTypes'] = request_types
        if modified_from:
            params['filter.modifiedFrom'] = modified_from

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_cfi_team_requests(self, limit=15, lookback_days=60):
        """
        Specialized search for the CFI Team (Mark Rob as QC/Reviewer or Michael Sloan as Analyst).
        """
        from datetime import datetime, timedelta
        from concurrent.futures import ThreadPoolExecutor
        
        modified_from = (datetime.now() - timedelta(days=lookback_days)).strftime("%Y-%m-%dT%H:%M:%S")
        all_reqs = self.list_requests(limit=1000, modified_from=modified_from)
        
        matches = []
        
        def process_req(req):
            req_id = req['id']
            try:
                detail = self.get_request(req_id)
                if not detail: return None
                
                qc_match = False
                analyst_match = False
                
                for a in detail.get('answers', []):
                    val = str(a.get('displayValue', '')).lower()
                    field = a.get('questionName', '')
                    
                    if "mark rob" in val and ("Reviewer" in field or "QC" in field):
                        qc_match = True
                    if "michael sloan" in val and "Analyst" in field:
                        analyst_match = True
                
                if qc_match or analyst_match:
                    # Skip canceled requests
                    if detail.get('currentState') == "Canceled":
                        return None
                    return detail
            except:
                pass
            return None

        with ThreadPoolExecutor(max_workers=20) as executor:
            results = list(executor.map(process_req, all_reqs))
            matches = [r for r in results if r]

        matches.sort(key=lambda x: x.get('id', 0), reverse=True)
        return matches[:limit]

    @staticmethod
    def format_request_table(requests_data):
        """
        Returns a standardized ASCII table representation of request items.
        """
        if not requests_data:
            return "No requests found."

        # Sort by ID descending to ensure newest are on top
        sorted_data = sorted(requests_data, key=lambda x: x.get('id', 0), reverse=True)

        # Header
        header = f"{'ID':<8} | {'Date':<10} | {'Status':<12} | {'Current State':<25} | {'Type':<20} | {'Name'}"
        separator = "-" * 130
        
        lines = [header, separator]
        
        for r in sorted_data:
            req_id = str(r.get('id', ''))
            date = str(r.get('createdOn', ''))[:10]
            status = str(r.get('status', ''))
            state = str(r.get('currentState', ''))[:25]
            req_type = str(r.get('requestType', ''))[:20]
            name = str(r.get('name', ''))
            
            lines.append(f"{req_id:<8} | {date:<10} | {status:<12} | {state:<25} | {req_type:<20} | {name}")
            
        return "\n".join(lines)

    @staticmethod
    def format_request_table_markdown(requests_data):
        """
        Returns a markdown table representation of request items.
        """
        if not requests_data:
            return "No requests found."

        # Sort by ID descending to ensure newest are on top
        sorted_data = sorted(requests_data, key=lambda x: x.get('id', 0), reverse=True)

        # Markdown table header
        lines = ["| ID | Date | Status | Current State | Type | Name |"]
        lines.append("| --- | --- | --- | --- | --- | --- |")
        
        for r in sorted_data:
            req_id = str(r.get('id', ''))
            date = str(r.get('createdOn', ''))[:10]
            status = str(r.get('status', ''))
            state = str(r.get('currentState', ''))
            req_type = str(r.get('requestType', ''))
            name = str(r.get('name', '')).replace('|', '\\|')  # Escape pipe characters
            
            lines.append(f"| {req_id} | {date} | {status} | {state} | {req_type} | {name} |")
            
        return "\n".join(lines)

    def get_request(self, request_id):
        """
        Retrieves full details for a specific intake request by ID.
        """
        url = f"{self.base_url}/api/intake/v1/requests/{request_id}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()

    def download_attachment(self, request_id, attachment_id, output_path):
        """
        Downloads an attachment and saves it to the specified path.
        """
        import base64
        url = f"{self.base_url}/api/intake/v1/requests/{request_id}/attachments/{attachment_id}"
        params = {'includeContent': 'true'}
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        content_b64 = data.get('content')
        
        if not content_b64:
            raise ValueError(f"No content found for attachment {attachment_id}")
            
        file_content = base64.b64decode(content_b64)
        
        with open(output_path, 'wb') as f:
            f.write(file_content)
        
        return output_path

    def search_requests_by_answer(self, query, limit=50):
        """
        Searches the most recent requests for a specific string in any answer field.
        Returns a list of matching requests with the specific matching field details.
        """
        results = []
        requests_list = self.list_requests()[:limit]
        
        for req in requests_list:
            req_id = req['id']
            try:
                detail = self.get_request(req_id)
                if not detail:
                    continue
                
                answers = detail.get('answers', [])
                for a in answers:
                    display_val = str(a.get('displayValue', ''))
                    if query.lower() in display_val.lower():
                        results.append({
                            'request_id': req_id,
                            'request_name': req['name'],
                            'field_name': a.get('questionName'),
                            'value': display_val
                        })
            except Exception as e:
                logger.error(f"Error searching request {req_id}: {e}")
                
        return results

    @staticmethod
    def sanitize_filename(name):
        """
        Utility to convert a request title into a safe filename.
        """
        safe = re.sub(r'[\\/*?:\"<>|]', '', name).strip()
        return re.sub(r'\s+', '_', safe)
