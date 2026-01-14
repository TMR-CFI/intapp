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

    def list_requests(self, limit=1000):
        """
        Retrieves a list of intake requests.
        """
        url = f"{self.base_url}/api/intake/v1/requests"
        # Note: In a full SDK, we would handle pagination if the API supports it
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

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
