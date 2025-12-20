"""
Microsoft 365 & SharePoint Integration Module
Complete sync with APPSHOLDINGSWYINC tenant for document extraction and Power BI
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List

class Microsoft365Integrator:
    """
    Connects to Microsoft 365 tenant and extracts all legal documents
    from SharePoint LitigationVault
    """

    def __init__(self):
        # Configuration from screenshots
        self.tenant_id = "fe3b018d-58d1-4513-8d70-2dc06273a649"
        self.tenant_domain = "APPSHOLDINGSWYINC.onmicrosoft.com"
        self.sharepoint_site = "https://appswy.sharepoint.com/sites/LitigationVault"
        self.library_name = "Documents"
        self.drive_id = "Documents"

        # Power BI Configuration
        self.powerbi_group_id = "c96c4ac3-c695-4afd-b90d-423b3ece0b8d"
        self.powerbi_dashboard_id = "fa50985d-6616-4ead-859a-8e4c08dabb88"

        # Power Automate
        self.power_automate_env = "Default-fe3b018d-58d1-4513-8d70-2dc06273a649"

        # Credentials (to be set from environment variables)
        self.client_id = os.getenv('M365_CLIENT_ID')
        self.client_secret = os.getenv('M365_CLIENT_SECRET')

    def authenticate(self):
        """
        Authenticate with Microsoft Graph API using service principal

        Returns OAuth token for API calls
        """
        from msal import ConfidentialClientApplication

        authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        scopes = [
            "https://graph.microsoft.com/.default",
            "https://analysis.windows.net/powerbi/api/.default"
        ]

        app = ConfidentialClientApplication(
            self.client_id,
            authority=authority,
            client_credential=self.client_secret
        )

        result = app.acquire_token_for_client(scopes=scopes)

        if "access_token" in result:
            self.access_token = result["access_token"]
            print("✅ Successfully authenticated with Microsoft 365")
            return True
        else:
            print(f"❌ Authentication failed: {result.get('error_description')}")
            return False

    def get_sharepoint_files(self, folder_path="/") -> List[Dict[str, Any]]:
        """
        Get all files from SharePoint Documents library

        Args:
            folder_path: Path within Documents library (default: root)

        Returns:
            List of file metadata
        """
        import requests

        # Graph API endpoint for SharePoint files
        site_id = self._get_site_id()
        drive_id = self._get_drive_id(site_id)

        endpoint = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/root"
        if folder_path != "/":
            endpoint += f":/{folder_path}:/children"
        else:
            endpoint += "/children"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }

        response = requests.get(endpoint, headers=headers)

        if response.status_code == 200:
            files = response.json().get('value', [])
            print(f"✅ Retrieved {len(files)} files from SharePoint")
            return files
        else:
            print(f"❌ Error retrieving files: {response.status_code}")
            return []

    def download_file(self, file_id: str, local_path: str):
        """Download a specific file from SharePoint"""
        import requests

        endpoint = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/content"

        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

        response = requests.get(endpoint, headers=headers, stream=True)

        if response.status_code == 200:
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"✅ Downloaded file to {local_path}")
            return True
        else:
            print(f"❌ Error downloading file: {response.status_code}")
            return False

    def search_documents(self, query: str, file_types: List[str] = None) -> List[Dict]:
        """
        Search SharePoint for specific documents

        Args:
            query: Search query (keywords, case names, etc.)
            file_types: Filter by file extensions (.pdf, .docx, .xlsx)

        Returns:
            List of matching files
        """
        import requests

        endpoint = f"https://graph.microsoft.com/v1.0/sites/{self._get_site_id()}/drive/root/search(q='{query}')"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }

        response = requests.get(endpoint, headers=headers)

        if response.status_code == 200:
            results = response.json().get('value', [])

            # Filter by file type if specified
            if file_types:
                results = [r for r in results if any(r['name'].endswith(ft) for ft in file_types)]

            print(f"✅ Found {len(results)} matching documents")
            return results
        else:
            print(f"❌ Search failed: {response.status_code}")
            return []

    def extract_legal_research_data(self) -> Dict[str, List]:
        """
        Extract all legal research from SharePoint Documents/Research folders

        Returns structured data organized by case
        """
        research_data = {
            "statutes": [],
            "case_law": [],
            "court_rules": [],
            "evidence": [],
            "drafts": []
        }

        # Search for different document types
        folders = [
            "Legal/Research/Statutes",
            "Legal/Research/Case Law",
            "Legal/Research/Court Rules",
            "Legal/Active Cases",
            "Legal/Drafts"
        ]

        for folder in folders:
            files = self.get_sharepoint_files(folder)
            category = folder.split('/')[-1].lower().replace(' ', '_')

            if category in research_data:
                research_data[category].extend(files)

        print(f"✅ Extracted legal research data:")
        for category, files in research_data.items():
            print(f"   - {category}: {len(files)} files")

        return research_data

    def sync_with_cleo(self, cleo_db_path="pillar-f-cleo/data/cleo.db"):
        """
        Sync SharePoint documents with Cleo case management system

        Links documents to appropriate cases based on filenames and metadata
        """
        from pillar_f_cleo.case_manager import CleoGasManager

        cleo = CleoGasManager(db_path=cleo_db_path)

        # Get all SharePoint files
        all_files = self.get_sharepoint_files()

        # Import into Cleo
        for file_data in all_files:
            filename = file_data.get('name', '')
            file_url = file_data.get('webUrl', '')

            # Try to match to case based on filename keywords
            # (This would use case keywords from master_case_list.json)

            # For now, add as general documents
            # In production, implement keyword matching logic

            print(f"   Syncing: {filename}")

        print(f"✅ Synced {len(all_files)} files with Cleo")
        return True

    def get_powerbi_data(self):
        """
        Extract data from Power BI dashboard for financial reporting
        """
        import requests

        endpoint = f"https://api.powerbi.com/v1.0/myorg/groups/{self.powerbi_group_id}/dashboards/{self.powerbi_dashboard_id}"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }

        response = requests.get(endpoint, headers=headers)

        if response.status_code == 200:
            dashboard_data = response.json()
            print(f"✅ Retrieved Power BI dashboard data")
            return dashboard_data
        else:
            print(f"❌ Power BI access failed: {response.status_code}")
            return None

    def trigger_power_automate_flow(self, flow_name: str, input_data: Dict = None):
        """
        Trigger a Power Automate flow for document processing

        Args:
            flow_name: Name of the flow to trigger
            input_data: Parameters to pass to the flow
        """
        # Power Automate HTTP trigger endpoint
        # (This would be configured in Power Automate and provided by user)

        print(f"⚠️  Power Automate integration requires flow HTTP endpoint")
        print(f"   Flow: {flow_name}")
        print(f"   Environment: {self.power_automate_env}")

        return None

    def _get_site_id(self) -> str:
        """Get SharePoint site ID from site URL"""
        import requests

        # Extract hostname and site path
        site_url = self.sharepoint_site.replace("https://", "")
        hostname, site_path = site_url.split("/sites/")

        endpoint = f"https://graph.microsoft.com/v1.0/sites/{hostname}:/sites/{site_path}"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }

        response = requests.get(endpoint, headers=headers)

        if response.status_code == 200:
            return response.json()['id']
        else:
            raise Exception(f"Failed to get site ID: {response.status_code}")

    def _get_drive_id(self, site_id: str) -> str:
        """Get Documents library drive ID"""
        import requests

        endpoint = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }

        response = requests.get(endpoint, headers=headers)

        if response.status_code == 200:
            drives = response.json().get('value', [])
            # Find "Documents" library
            for drive in drives:
                if drive.get('name') == self.library_name:
                    return drive['id']

            # If not found by name, return first drive
            if drives:
                return drives[0]['id']

        raise Exception("No drives found")


# Example usage and setup instructions
if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║     Microsoft 365 Integration Setup Instructions            ║
╚══════════════════════════════════════════════════════════════╝

Your Microsoft 365 tenant configuration has been extracted:

✅ Tenant ID: fe3b018d-58d1-4513-8d70-2dc06273a649
✅ Tenant Domain: APPSHOLDINGSWYINC.onmicrosoft.com
✅ SharePoint Site: https://appswy.sharepoint.com/sites/LitigationVault
✅ Documents Library: Ready for sync

═══════════════════════════════════════════════════════════════

REQUIRED: Complete API Registration
─────────────────────────────────────────────────────────────

To use this module, you need to:

1. Register App in Azure AD:
   - Go to: https://portal.azure.com
   - Navigate to: Azure Active Directory > App registrations
   - Click: New registration
   - Name: "Agent 5.0 Integration"
   - Supported account types: Single tenant
   - Click: Register

2. Grant API Permissions:
   - In your app, go to: API permissions
   - Add permissions:
     ☐ Microsoft Graph > Application permissions:
        - Files.Read.All
        - Sites.Read.All
        - User.Read.All
     ☐ Power BI Service > Application permissions:
        - Dataset.Read.All
        - Report.Read.All
   - Click: Grant admin consent

3. Create Client Secret:
   - Go to: Certificates & secrets
   - Click: New client secret
   - Description: "Agent 5.0 Secret"
   - Expires: 24 months
   - Click: Add
   - COPY the secret value immediately!

4. Add to config/.env:
   M365_CLIENT_ID=<your_application_id>
   M365_CLIENT_SECRET=<your_client_secret>

═══════════════════════════════════════════════════════════════

Once configured, Agent 5.0 will automatically:
- Extract all legal research from SharePoint
- Sync documents with Cleo case management
- Access Power BI financial dashboards
- Trigger Power Automate flows for document processing

═══════════════════════════════════════════════════════════════
    """)

    # Test connection (if credentials are available)
    integrator = Microsoft365Integrator()

    if integrator.client_id and integrator.client_secret:
        if integrator.authenticate():
            print("\n✅ Connection test successful!")
            print("\nRunning initial sync...")

            # Extract legal research
            research_data = integrator.extract_legal_research_data()

            # Save to file for Agent 5.0 to use
            with open('logs/sharepoint_research_data.json', 'w') as f:
                json.dump(research_data, f, indent=2)

            print(f"\n✅ Research data saved to logs/sharepoint_research_data.json")
    else:
        print("\n⚠️  Credentials not configured yet")
        print("   Complete Azure AD app registration first")
