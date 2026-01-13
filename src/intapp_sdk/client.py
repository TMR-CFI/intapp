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

    @staticmethod
    def sanitize_filename(name):
        """
        Utility to convert a request title into a safe filename.
        """
        safe = re.sub(r'[\\/*?:\"<>|]', '', name).strip()
        return re.sub(r'\s+', '_', safe)
