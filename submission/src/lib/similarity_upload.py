#!/usr/bin/env python3
"""
similarity_upload.py - HTTP client for Lattica custom encrypted data upload
"""
import requests
from lattica_common import http_settings
from lattica_common.version_utils import get_module_info
from lattica_common.app_api import ClientVersionError
from lib.token_utils import extract_token_id


class SimilarityUploader:
    """Client for uploading custom encrypted data to Lattica."""
    
    def __init__(self, token: str):
        """
        Initialize custom encrypted data uploader.
        
        Args:
            token: JWT authentication token
        """
        self.token = token
        self.module_name = "fetch-by-similarity"
        self.module_version = get_module_info(self.module_name) if self.module_name else "unknown"
    
    def upload_database(self, db_file_path: str, model_id: str) -> dict:
        # Extract tokenId for filename
        token_id = extract_token_id(self.token)
        expected_filename = token_id
        
        url = f"{http_settings.get_be_url()}/api/files/upload_custom_encrypted_data"
        # modelId is required by the backend to:
        #  - Verifies the model exists in the database, and its status is ACTIVE or UPLOADED
        #  - Checks if the token has permission to access the model (for private models)
        params = {'modelId': model_id}
        
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/octet-stream',
        }

        # Add client info to headers
        # This allows the server to block access from outdated clients
        if self.module_name:
            headers['X-Client-Module'] = self.module_name
        if self.module_version:
            headers['X-Client-Version'] = self.module_version
        
        # Stream the file for efficient upload of large encrypted data
        with open(db_file_path, 'rb') as file:
            response = requests.post(
                url,
                params=params,
                data=file,
                headers=headers,
                stream=True
            )
        
        if not response.ok:
            try:
                error_info = response.json()
                if error_info.get("error_code") == "CLIENT_VERSION_INCOMPATIBLE":
                    raise ClientVersionError(
                        error_info.get("error"), 
                        error_info.get("min_version")
                    )
                else:
                    raise Exception(f"FAILED upload-custom-encrypted-data with error: {error_info}")
            except ValueError:
                # If response is not JSON, use text
                raise Exception(f"FAILED upload-custom-encrypted-data with error: {response.text}")
        
        result = response.json()
        
        # Verify the filename matches our expectation
        if result.get('filename') != expected_filename:
            print(f"Warning: Expected filename '{expected_filename}' but got '{result.get('filename')}'")
        
        return result