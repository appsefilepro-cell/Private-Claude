"""
Microsoft 365 Connector
Connects to OneDrive and SharePoint using Microsoft Graph API
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any

# Microsoft Graph API (would need msal and requests in production)
# from msal import ConfidentialClientApplication

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('Microsoft365Connector')


class Microsoft365Connector:
    """
    Microsoft 365 Connector for OneDrive and SharePoint
    """

    def __init__(self, credentials_file: str = "config/microsoft_365_credentials.json"):
        self.credentials_file = credentials_file
        self.access_token = None
        self.download_dir_onedrive = "data/onedrive"
        self.download_dir_sharepoint = "data/sharepoint"

        # Tenant info (from the prompt)
        self.tenant = "APPSHOLDINGSWYINC.onmicrosoft.com"
        self.sharepoint_site = "appsholdingswyinc.sharepoint.com"

        # Ensure download directories exist
        os.makedirs(self.download_dir_onedrive, exist_ok=True)
        os.makedirs(self.download_dir_sharepoint, exist_ok=True)

        logger.info("Microsoft 365 Connector initialized")

    def authenticate(self) -> bool:
        """
        Authenticate with Microsoft Graph API

        Returns:
            True if successful
        """
        try:
            if not os.path.exists(self.credentials_file):
                logger.warning(f"Credentials file not found: {self.credentials_file}")
                self._create_template_credentials()
                return False

            # In production, this would use MSAL for authentication
            # authority = f"https://login.microsoftonline.com/{tenant_id}"
            # app = ConfidentialClientApplication(
            #     client_id, authority=authority, client_credential=client_secret
            # )
            # result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])

            logger.info("Microsoft 365 authentication successful (simulated)")
            return True

        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False

    def _create_template_credentials(self) -> None:
        """Create template credentials file"""
        template = {
            "tenant_id": "YOUR_TENANT_ID",
            "client_id": "YOUR_CLIENT_ID",
            "client_secret": "YOUR_CLIENT_SECRET",
            "tenant": "APPSHOLDINGSWYINC.onmicrosoft.com",
            "sharepoint_site": "appsholdingswyinc.sharepoint.com",
            "instructions": [
                "1. Go to Azure Portal: https://portal.azure.com/",
                "2. Navigate to 'Azure Active Directory' > 'App registrations'",
                "3. Click 'New registration'",
                "4. Name: 'Agent X2.0 Integration'",
                "5. Supported account types: 'Single tenant'",
                "6. Register the application",
                "7. Note the 'Application (client) ID' and 'Directory (tenant) ID'",
                "8. Create a client secret:",
                "   - Go to 'Certificates & secrets'",
                "   - Click 'New client secret'",
                "   - Copy the secret value (only shown once!)",
                "9. Add API permissions:",
                "   - Microsoft Graph > Application permissions:",
                "   - Files.Read.All (OneDrive)",
                "   - Sites.Read.All (SharePoint)",
                "   - Mail.Read (if needed)",
                "10. Grant admin consent for the permissions",
                "11. Update this file with your credentials"
            ]
        }

        os.makedirs(os.path.dirname(self.credentials_file), exist_ok=True)
        with open(self.credentials_file, 'w') as f:
            json.dump(template, f, indent=2)

        logger.info(f"Created template credentials file: {self.credentials_file}")

    def list_onedrive_files(self, folder_path: str = "/") -> List[Dict[str, Any]]:
        """
        List files in OneDrive

        Args:
            folder_path: Path to folder (default: root)

        Returns:
            List of file metadata
        """
        logger.info(f"Listing OneDrive files in: {folder_path}")

        # In production:
        # url = f"https://graph.microsoft.com/v1.0/me/drive/root/children"
        # headers = {"Authorization": f"Bearer {self.access_token}"}
        # response = requests.get(url, headers=headers)
        # files = response.json().get('value', [])

        files = []
        logger.info(f"Found {len(files)} files in OneDrive")

        return files

    def list_sharepoint_files(self, site_path: str = "/Shared Documents") -> List[Dict[str, Any]]:
        """
        List files in SharePoint

        Args:
            site_path: Path to SharePoint folder

        Returns:
            List of file metadata
        """
        logger.info(f"Listing SharePoint files in: {site_path}")

        # In production:
        # Get site ID first
        # url = f"https://graph.microsoft.com/v1.0/sites/{sharepoint_site}:/sites/root"
        # Then list files
        # url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root/children"

        files = []
        logger.info(f"Found {len(files)} files in SharePoint")

        return files

    def download_file(self, file_id: str, filename: str, source: str = "onedrive") -> str:
        """
        Download a file from OneDrive or SharePoint

        Args:
            file_id: File ID from Microsoft Graph
            filename: Filename to save as
            source: 'onedrive' or 'sharepoint'

        Returns:
            Path to downloaded file
        """
        try:
            download_dir = self.download_dir_onedrive if source == "onedrive" else self.download_dir_sharepoint

            # In production:
            # url = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/content"
            # headers = {"Authorization": f"Bearer {self.access_token}"}
            # response = requests.get(url, headers=headers)
            # content = response.content

            filepath = os.path.join(download_dir, filename)

            # Simulated download
            logger.info(f"Downloaded {source} file: {filename}")

            return filepath

        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            return None

    def create_sharepoint_folder(self, folder_name: str, parent_path: str = "/Shared Documents") -> bool:
        """
        Create a folder in SharePoint

        Args:
            folder_name: Name of folder to create
            parent_path: Parent folder path

        Returns:
            True if successful
        """
        try:
            logger.info(f"Creating SharePoint folder: {parent_path}/{folder_name}")

            # In production:
            # url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{parent_path}:/children"
            # data = {"name": folder_name, "folder": {}}
            # response = requests.post(url, headers=headers, json=data)

            logger.info(f"Folder created successfully (simulated)")
            return True

        except Exception as e:
            logger.error(f"Error creating folder: {e}")
            return False

    def upload_to_sharepoint(self, local_file: str, sharepoint_path: str) -> bool:
        """
        Upload a file to SharePoint

        Args:
            local_file: Path to local file
            sharepoint_path: Destination path in SharePoint

        Returns:
            True if successful
        """
        try:
            logger.info(f"Uploading {local_file} to SharePoint: {sharepoint_path}")

            # In production:
            # url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{sharepoint_path}:/content"
            # with open(local_file, 'rb') as f:
            #     response = requests.put(url, headers=headers, data=f)

            logger.info(f"Upload successful (simulated)")
            return True

        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return False

    def setup_sharepoint_structure(self) -> bool:
        """
        Create the complete SharePoint folder structure for Agent X2.0
        """
        logger.info("Setting up SharePoint folder structure")

        folders = [
            # Legal Operations (Pillar B)
            "/Shared Documents/Legal Operations",
            "/Shared Documents/Legal Operations/01_Templates",
            "/Shared Documents/Legal Operations/02_Active_Cases",
            "/Shared Documents/Legal Operations/02_Active_Cases/NOVU_Apartments",
            "/Shared Documents/Legal Operations/02_Active_Cases/NOVU_Apartments/Evidence",
            "/Shared Documents/Legal Operations/02_Active_Cases/NOVU_Apartments/Drafts",
            "/Shared Documents/Legal Operations/02_Active_Cases/BMO_Dispute",
            "/Shared Documents/Legal Operations/02_Active_Cases/United_Airlines",
            "/Shared Documents/Legal Operations/03_Automation_Output",

            # Trading Operations (Pillar A)
            "/Shared Documents/Trading Operations",
            "/Shared Documents/Trading Operations/Trade_Logs",
            "/Shared Documents/Trading Operations/Performance_Reports",
            "/Shared Documents/Trading Operations/Compliance",

            # Federal Contracting (Pillar C)
            "/Shared Documents/Federal Contracting",
            "/Shared Documents/Federal Contracting/8a_Application_Package",
            "/Shared Documents/Federal Contracting/Opportunities",
            "/Shared Documents/Federal Contracting/Proposals",

            # Grant Intelligence (Pillar D)
            "/Shared Documents/Grant Intelligence",
            "/Shared Documents/Grant Intelligence/Resource_Library",
            "/Shared Documents/Grant Intelligence/Active_Grants"
        ]

        try:
            for folder_path in folders:
                # Extract folder name and parent path
                parts = folder_path.rsplit('/', 1)
                parent = parts[0] if len(parts) > 1 else "/"
                folder_name = parts[1] if len(parts) > 1 else parts[0]

                self.create_sharepoint_folder(folder_name, parent)

            logger.info("SharePoint structure setup complete")
            return True

        except Exception as e:
            logger.error(f"Error setting up SharePoint structure: {e}")
            return False

    def process_all_files(self) -> Dict[str, Any]:
        """
        Process all files from OneDrive and SharePoint

        Returns:
            Statistics dictionary
        """
        stats = {
            "onedrive_files": 0,
            "sharepoint_files": 0,
            "downloaded": 0,
            "errors": 0
        }

        try:
            # Authenticate
            if not self.authenticate():
                logger.error("Authentication failed")
                return stats

            # Process OneDrive
            onedrive_files = self.list_onedrive_files()
            stats["onedrive_files"] = len(onedrive_files)

            for file in onedrive_files:
                try:
                    self.download_file(file.get('id'), file.get('name'), 'onedrive')
                    stats["downloaded"] += 1
                except Exception as e:
                    logger.error(f"Error downloading OneDrive file: {e}")
                    stats["errors"] += 1

            # Process SharePoint
            sharepoint_files = self.list_sharepoint_files()
            stats["sharepoint_files"] = len(sharepoint_files)

            for file in sharepoint_files:
                try:
                    self.download_file(file.get('id'), file.get('name'), 'sharepoint')
                    stats["downloaded"] += 1
                except Exception as e:
                    logger.error(f"Error downloading SharePoint file: {e}")
                    stats["errors"] += 1

            logger.info(f"Microsoft 365 processing complete: {json.dumps(stats)}")

        except Exception as e:
            logger.error(f"Error in process_all_files: {e}")
            stats["errors"] += 1

        return stats

    def get_connection_instructions(self) -> List[str]:
        """Get instructions for setting up Microsoft 365 connection"""
        return [
            "=== Microsoft 365 API Setup Instructions ===",
            "",
            "1. Go to Azure Portal: https://portal.azure.com/",
            "2. Sign in with your APPSHOLDINGSWYINC account",
            "3. Navigate to 'Azure Active Directory' > 'App registrations'",
            "4. Click 'New registration':",
            "   - Name: 'Agent X2.0 Integration'",
            "   - Supported account types: 'Single tenant'",
            "   - Redirect URI: Not needed for daemon app",
            "5. After registration, note these values:",
            "   - Application (client) ID",
            "   - Directory (tenant) ID",
            "6. Create a client secret:",
            "   - Go to 'Certificates & secrets' > 'New client secret'",
            "   - Description: 'Agent X2.0'",
            "   - Expires: 24 months",
            "   - COPY THE SECRET VALUE (shown only once!)",
            "7. Add API permissions:",
            "   - Click 'API permissions' > 'Add a permission'",
            "   - Microsoft Graph > Application permissions",
            "   - Add these permissions:",
            "     * Files.Read.All",
            "     * Files.ReadWrite.All",
            "     * Sites.Read.All",
            "     * Sites.ReadWrite.All",
            "     * Mail.Read (optional, if syncing email)",
            "8. Grant admin consent:",
            "   - Click 'Grant admin consent for [tenant]'",
            "   - Confirm",
            "9. Update config/microsoft_365_credentials.json with:",
            "   - tenant_id",
            "   - client_id",
            "   - client_secret",
            "10. Run the connector to test connection",
            "",
            f"Your Tenant: {self.tenant}",
            f"Your SharePoint: {self.sharepoint_site}",
            "",
            "For detailed documentation:",
            "https://docs.microsoft.com/en-us/graph/auth-v2-service"
        ]


def main():
    """Main entry point"""
    connector = Microsoft365Connector()

    print("\n".join(connector.get_connection_instructions()))
    print("\n")

    # Setup SharePoint structure
    connector.setup_sharepoint_structure()

    # Process files
    stats = connector.process_all_files()
    print(f"\nMicrosoft 365 Processing Stats:")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
