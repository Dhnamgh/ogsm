"""
Microsoft Graph API Client powered by MSAL and Tenacity for resilient HTTP calls.
"""

import io
from typing import Optional, Dict, Any
import requests
import msal
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from core.config import AppConfig, load_config
from core.exceptions import GraphAPIError, OneDriveFileNotFoundError
from core.logger import get_logger

logger = get_logger()


class MicrosoftGraphClient:
    """
    Client for acquiring tokens via MSAL and executing REST API calls to MS Graph.
    """

    def __init__(self, config: Optional[AppConfig] = None):
        self.config = config or load_config()
        self._authority = f"https://login.microsoftonline.com/{self.config.azure.tenant_id}"
        self._scopes = ["https://graph.microsoft.com/.default"]
        self._msal_app = msal.ConfidentialClientApplication(
            client_id=self.config.azure.client_id,
            client_credential=self.config.azure.client_secret,
            authority=self._authority,
        )

    def _get_access_token(self) -> str:
        """
        Acquires an app-only token from Azure AD using Client Credentials Flow.
        """
        result = self._msal_app.acquire_token_for_client(scopes=self._scopes)
        if "access_token" in result:
            return result["access_token"]
        
        error_desc = result.get("error_description", "Unknown authentication error")
        logger.error(f"Authentication failed: {error_desc}")
        raise GraphAPIError(f"Failed to acquire MS Graph token: {error_desc}", status_code=401)

    def _get_headers(self) -> Dict[str, str]:
        token = self._get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    @retry(
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.RequestException, GraphAPIError)),
        reraise=True,
    )
    def download_file_bytes(self, file_path: str) -> bytes:
        """
        Downloads a file directly from OneDrive as a binary byte stream.
        
        Args:
            file_path: Relative path inside the configured OneDrive folder or root.
        """
        drive_id = self.config.onedrive.drive_id
        folder = self.config.onedrive.folder_path.strip("/")
        full_path = f"{folder}/{file_path}".strip("/")
        
        url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{full_path}:/content"
        headers = self._get_headers()

        logger.info(f"Downloading file from OneDrive via MS Graph: {full_path}")
        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code == 404:
            raise OneDriveFileNotFoundError(f"File not found on OneDrive: {full_path}")
        
        if response.status_code not in (200, 302):
            logger.error(f"Graph download error ({response.status_code}): {response.text}")
            raise GraphAPIError(f"Error downloading file {file_path}", status_code=response.status_code)

        return response.content

    @retry(
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.RequestException, GraphAPIError)),
        reraise=True,
    )
    def upload_file_bytes(self, file_path: str, content: bytes) -> Dict[str, Any]:
        """
        Uploads or overwrites a file in OneDrive.
        
        Args:
            file_path: Target relative path in OneDrive.
            content: Raw byte array of the file (e.g., exported Excel file).
        """
        drive_id = self.config.onedrive.drive_id
        folder = self.config.onedrive.folder_path.strip("/")
        full_path = f"{folder}/{file_path}".strip("/")

        url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{full_path}:/content"
        headers = self._get_headers()
        headers["Content-Type"] = "application/octet-stream"

        logger.info(f"Uploading file to OneDrive via MS Graph: {full_path} ({len(content)} bytes)")
        response = requests.put(url, headers=headers, data=content, timeout=60)

        if response.status_code not in (200, 201):
            logger.error(f"Graph upload error ({response.status_code}): {response.text}")
            raise GraphAPIError(f"Failed to upload file {file_path}", status_code=response.status_code)

        return response.json()
