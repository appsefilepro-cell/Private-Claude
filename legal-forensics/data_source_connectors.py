"""
Multi-Source Data Connectors for Forensic Legal Analysis
Integrates Gmail, Dropbox, SharePoint, OneDrive for case document extraction
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('DataConnectors')


class DataSourceConnector(ABC):
    """Abstract base class for data source connectors"""

    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the data source"""
        pass

    @abstractmethod
    def list_files(self, path: str = "/") -> List[Dict[str, Any]]:
        """List all files in the data source"""
        pass

    @abstractmethod
    def get_file_content(self, file_id: str) -> bytes:
        """Get file content"""
        pass

    @abstractmethod
    def extract_metadata(self, file_id: str) -> Dict[str, Any]:
        """Extract file metadata"""
        pass


class GmailForensicConnector(DataSourceConnector):
    """
    Gmail forensic connector for email and attachment extraction
    REQUIRES: Gmail API credentials configured
    """

    def __init__(self, credentials_path: str = "config/gmail_credentials.json"):
        self.credentials_path = credentials_path
        self.service = None
        self.authenticated = False

    def authenticate(self) -> bool:
        """Authenticate with Gmail API"""
        logger.info("Gmail: Attempting authentication")

        if not os.path.exists(self.credentials_path):
            logger.error(f"Gmail credentials not found: {self.credentials_path}")
            logger.info("To configure Gmail access:")
            logger.info("1. Enable Gmail API in Google Cloud Console")
            logger.info("2. Download OAuth credentials")
            logger.info(f"3. Save to {self.credentials_path}")
            return False

        # In production, this would use actual Gmail API
        # from google.oauth2.credentials import Credentials
        # from googleapiclient.discovery import build

        logger.warning("Gmail connector ready but requires actual API credentials")
        return False

    def search_emails(self, query: str) -> List[Dict[str, Any]]:
        """
        Search emails with litigation-specific keywords

        Args:
            query: Gmail search query (e.g., "from:lapd.gov OR subject:eviction")

        Returns:
            List of email metadata
        """
        # In production:
        # results = self.service.users().messages().list(userId='me', q=query).execute()

        logger.info(f"Would search Gmail with query: {query}")
        return []

    def get_email_with_attachments(self, message_id: str) -> Dict[str, Any]:
        """Get email and all attachments"""
        # In production: Fetch full email and decode attachments
        return {}

    def list_files(self, path: str = "/") -> List[Dict[str, Any]]:
        """List all emails (not applicable for Gmail)"""
        return []

    def get_file_content(self, file_id: str) -> bytes:
        """Get email content"""
        return b""

    def extract_metadata(self, file_id: str) -> Dict[str, Any]:
        """Extract email metadata"""
        return {}


class SharePointForensicConnector(DataSourceConnector):
    """
    SharePoint forensic connector for document extraction
    REQUIRES: Microsoft 365 credentials configured
    """

    def __init__(self):
        self.access_token = None
        self.site_url = os.getenv('SHAREPOINT_SITE_URL', '')
        self.authenticated = False

        # Target SharePoint folders
        self.target_folders = [
            "/Shared Documents",
            "/SharePoint Share Folder",
            "/Dr",
            "/Legal Operations",
            "/Case Files"
        ]

    def authenticate(self) -> bool:
        """Authenticate with SharePoint via Microsoft Graph API"""
        logger.info("SharePoint: Attempting authentication")

        tenant_id = os.getenv('MICROSOFT_TENANT_ID')
        client_id = os.getenv('MICROSOFT_CLIENT_ID')
        client_secret = os.getenv('MICROSOFT_CLIENT_SECRET')

        if not all([tenant_id, client_id, client_secret]):
            logger.error("SharePoint credentials not configured in .env")
            logger.info("Required environment variables:")
            logger.info("  - MICROSOFT_TENANT_ID")
            logger.info("  - MICROSOFT_CLIENT_ID")
            logger.info("  - MICROSOFT_CLIENT_SECRET")
            logger.info("  - SHAREPOINT_SITE_URL")
            return False

        # In production:
        # from msal import ConfidentialClientApplication
        # app = ConfidentialClientApplication(client_id, authority=authority, client_credential=client_secret)
        # result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])

        logger.warning("SharePoint connector ready but requires actual API credentials")
        return False

    def list_files(self, path: str = "/") -> List[Dict[str, Any]]:
        """
        Recursively list all files in SharePoint

        Args:
            path: SharePoint folder path

        Returns:
            List of file metadata including:
            - id, name, path, created, modified, size, content_type
        """
        # In production:
        # url = f"{self.site_url}/_api/web/GetFolderByServerRelativeUrl('{path}')/Files"
        # response = requests.get(url, headers={"Authorization": f"Bearer {self.access_token}"})

        logger.info(f"Would list SharePoint files in: {path}")
        return []

    def get_file_content(self, file_id: str) -> bytes:
        """Download file content from SharePoint"""
        # In production: Use Microsoft Graph API to download
        return b""

    def extract_metadata(self, file_id: str) -> Dict[str, Any]:
        """Extract SharePoint file metadata"""
        return {}

    def get_case_documents(self, case_keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Search SharePoint for documents matching case keywords

        Args:
            case_keywords: List of keywords (names, case numbers, etc.)

        Returns:
            List of matching documents
        """
        documents = []

        for folder in self.target_folders:
            files = self.list_files(folder)
            for file in files:
                # Check if any keyword matches filename or path
                filename_lower = file.get('name', '').lower()
                path_lower = file.get('path', '').lower()

                if any(kw.lower() in filename_lower or kw.lower() in path_lower
                       for kw in case_keywords):
                    documents.append(file)

        return documents


class OneDriveForensicConnector(DataSourceConnector):
    """
    OneDrive forensic connector (Personal and Business)
    REQUIRES: Microsoft 365 credentials configured
    """

    def __init__(self, account_type: str = "business"):
        self.account_type = account_type  # "business" or "personal"
        self.access_token = None
        self.authenticated = False

    def authenticate(self) -> bool:
        """Authenticate with OneDrive via Microsoft Graph API"""
        logger.info(f"OneDrive ({self.account_type}): Attempting authentication")

        # Same credentials as SharePoint for business account
        # For personal account, would use different OAuth flow

        logger.warning("OneDrive connector ready but requires actual API credentials")
        return False

    def list_files(self, path: str = "/") -> List[Dict[str, Any]]:
        """List all files in OneDrive"""
        # In production: Use Microsoft Graph API
        # url = "https://graph.microsoft.com/v1.0/me/drive/root/children"

        logger.info(f"Would list OneDrive ({self.account_type}) files in: {path}")
        return []

    def get_file_content(self, file_id: str) -> bytes:
        """Download file from OneDrive"""
        return b""

    def extract_metadata(self, file_id: str) -> Dict[str, Any]:
        """Extract OneDrive file metadata"""
        return {}


class DropboxForensicConnector(DataSourceConnector):
    """
    Dropbox forensic connector
    REQUIRES: Dropbox API token configured
    """

    def __init__(self):
        self.access_token = os.getenv('DROPBOX_ACCESS_TOKEN')
        self.dbx = None
        self.authenticated = False

    def authenticate(self) -> bool:
        """Authenticate with Dropbox API"""
        logger.info("Dropbox: Attempting authentication")

        if not self.access_token:
            logger.error("Dropbox access token not configured")
            logger.info("Set DROPBOX_ACCESS_TOKEN in .env file")
            logger.info("Get token from: https://www.dropbox.com/developers/apps")
            return False

        # In production:
        # import dropbox
        # self.dbx = dropbox.Dropbox(self.access_token)
        # self.dbx.users_get_current_account()  # Test connection

        logger.warning("Dropbox connector ready but requires actual API token")
        return False

    def list_files(self, path: str = "") -> List[Dict[str, Any]]:
        """List all files in Dropbox"""
        # In production:
        # result = self.dbx.files_list_folder(path, recursive=True)

        logger.info(f"Would list Dropbox files in: {path}")
        return []

    def get_file_content(self, file_id: str) -> bytes:
        """Download file from Dropbox"""
        # In production:
        # metadata, response = self.dbx.files_download(file_id)
        # return response.content

        return b""

    def extract_metadata(self, file_id: str) -> Dict[str, Any]:
        """Extract Dropbox file metadata"""
        return {}


class MultiSourceOrchestrator:
    """
    Orchestrates data collection from all sources for forensic analysis
    """

    def __init__(self):
        self.gmail = GmailForensicConnector()
        self.sharepoint = SharePointForensicConnector()
        self.onedrive_business = OneDriveForensicConnector("business")
        self.onedrive_personal = OneDriveForensicConnector("personal")
        self.dropbox = DropboxForensicConnector()

        self.all_connectors = [
            ("Gmail", self.gmail),
            ("SharePoint", self.sharepoint),
            ("OneDrive Business", self.onedrive_business),
            ("OneDrive Personal", self.onedrive_personal),
            ("Dropbox", self.dropbox)
        ]

    def authenticate_all(self) -> Dict[str, bool]:
        """Attempt to authenticate all data sources"""
        results = {}

        logger.info("=== AUTHENTICATING ALL DATA SOURCES ===")

        for name, connector in self.all_connectors:
            try:
                results[name] = connector.authenticate()
                status = "✓ SUCCESS" if results[name] else "✗ FAILED"
                logger.info(f"{name}: {status}")
            except Exception as e:
                results[name] = False
                logger.error(f"{name}: Error - {e}")

        return results

    def collect_all_documents(self, case_keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Collect documents from all sources matching case keywords

        Args:
            case_keywords: Keywords to search for

        Returns:
            Consolidated list of all documents from all sources
        """
        all_documents = []

        for name, connector in self.all_connectors:
            if not connector.authenticated:
                logger.warning(f"Skipping {name} - not authenticated")
                continue

            try:
                logger.info(f"Collecting documents from {name}")
                docs = connector.list_files()

                # Add source metadata
                for doc in docs:
                    doc['source'] = name
                    doc['collected_at'] = datetime.now().isoformat()

                all_documents.extend(docs)
                logger.info(f"Collected {len(docs)} documents from {name}")

            except Exception as e:
                logger.error(f"Error collecting from {name}: {e}")

        return all_documents

    def get_connection_status(self) -> Dict[str, str]:
        """Get status of all connections"""
        status = {}

        for name, connector in self.all_connectors:
            if connector.authenticated:
                status[name] = "CONNECTED"
            elif hasattr(connector, 'credentials_path') and not os.path.exists(connector.credentials_path):
                status[name] = "MISSING CREDENTIALS"
            else:
                status[name] = "NOT AUTHENTICATED"

        return status


def main():
    """Test multi-source connector"""
    logger.info("=== MULTI-SOURCE FORENSIC DATA CONNECTOR ===")

    orchestrator = MultiSourceOrchestrator()

    # Attempt authentication
    auth_results = orchestrator.authenticate_all()

    # Print status
    print("\n" + "="*60)
    print("DATA SOURCE CONNECTION STATUS")
    print("="*60)

    status = orchestrator.get_connection_status()
    for source, state in status.items():
        icon = "✓" if state == "CONNECTED" else "✗"
        print(f"{icon} {source}: {state}")

    print("="*60)

    # Print configuration instructions
    print("\nTO ENABLE DATA COLLECTION:")
    print("1. Configure credentials in config/.env")
    print("2. Enable required APIs (Gmail, Microsoft Graph)")
    print("3. Grant necessary permissions")
    print("4. Re-run authentication")
    print("\nSee docs/API_SETUP_INSTRUCTIONS.md for detailed steps")


if __name__ == "__main__":
    main()
