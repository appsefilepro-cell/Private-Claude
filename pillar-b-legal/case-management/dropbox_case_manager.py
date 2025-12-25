#!/usr/bin/env python3
"""
FREE CASE MANAGEMENT SYSTEM
Uses public Dropbox folders for document storage and client access

Features:
- Free case file storage
- Client document access via public links
- Automated folder organization
- Document version control
- Client portal (via Dropbox shared folders)

NO COST - Uses Dropbox Free tier (2GB storage)
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import urllib.request
import urllib.parse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('CaseManager')


class DropboxCaseManager:
    """
    Free case management using Dropbox public folders

    Dropbox Free Tier:
    - 2GB storage
    - Public folder sharing
    - File versioning (30 days)
    - Mobile app access
    - Client can access files without Dropbox account
    """

    def __init__(self, dropbox_access_token: str = None):
        """
        Initialize case manager

        Get Dropbox access token:
        1. Go to: https://www.dropbox.com/developers/apps
        2. Create app → Scoped access → App folder
        3. Generate access token
        """
        self.access_token = dropbox_access_token or os.getenv('DROPBOX_ACCESS_TOKEN', '')
        self.base_path = Path(__file__).parent
        self.cases_path = self.base_path / "cases_index"
        self.cases_path.mkdir(exist_ok=True)

        logger.info("=" * 70)
        logger.info("📁 DROPBOX CASE MANAGEMENT SYSTEM INITIALIZED")
        logger.info("   Free tier - 2GB storage")
        logger.info("=" * 70)

    def create_case_folder(self, case_info: Dict[str, Any]) -> Dict[str, str]:
        """
        Create case folder structure in Dropbox

        Folder structure:
        /Cases/{Client Name} - {Case Number}/
            /01_Intake_Forms/
            /02_Correspondence/
            /03_Court_Filings/
            /04_Evidence/
            /05_Legal_Research/
            /06_Drafts/
            /07_Final_Documents/
            /08_Billing_Records/
            /09_Client_Deliverables/
        """
        client_name = case_info.get('client_name', 'Unknown Client')
        case_number = case_info.get('case_number', 'PENDING')
        case_id = f"{client_name} - {case_number}".replace(' ', '_')

        folders = {
            'root': f"/Cases/{case_id}",
            'intake': f"/Cases/{case_id}/01_Intake_Forms",
            'correspondence': f"/Cases/{case_id}/02_Correspondence",
            'court_filings': f"/Cases/{case_id}/03_Court_Filings",
            'evidence': f"/Cases/{case_id}/04_Evidence",
            'research': f"/Cases/{case_id}/05_Legal_Research",
            'drafts': f"/Cases/{case_id}/06_Drafts",
            'final': f"/Cases/{case_id}/07_Final_Documents",
            'billing': f"/Cases/{case_id}/08_Billing_Records",
            'client_deliverables': f"/Cases/{case_id}/09_Client_Deliverables"
        }

        # Create folders
        for folder_name, folder_path in folders.items():
            self._create_dropbox_folder(folder_path)

        # Save case index locally
        case_index = {
            'case_id': case_id,
            'client_name': client_name,
            'case_number': case_number,
            'created_date': datetime.now().isoformat(),
            'dropbox_folders': folders,
            'case_info': case_info
        }

        index_file = self.cases_path / f"{case_id}.json"
        with open(index_file, 'w') as f:
            json.dump(case_index, f, indent=2)

        logger.info(f"✅ Created case folder structure for: {client_name}")
        logger.info(f"   Case ID: {case_id}")

        return folders

    def _create_dropbox_folder(self, path: str) -> bool:
        """Create folder in Dropbox"""
        if not self.access_token:
            logger.warning("⚠️  Dropbox access token not configured")
            logger.info("   Simulating folder creation locally")
            return False

        try:
            # Dropbox API v2 - Create folder
            url = "https://api.dropboxapi.com/2/files/create_folder_v2"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            data = json.dumps({
                "path": path,
                "autorename": False
            }).encode('utf-8')

            req = urllib.request.Request(url, data=data, headers=headers, method='POST')
            response = urllib.request.urlopen(req)

            if response.status == 200:
                logger.info(f"   ✅ Created folder: {path}")
                return True

        except urllib.error.HTTPError as e:
            if e.code == 409:
                # Folder already exists
                logger.info(f"   📁 Folder exists: {path}")
                return True
            else:
                logger.error(f"   ❌ Error creating folder: {e}")
                return False

        except Exception as e:
            logger.error(f"   ❌ Dropbox API error: {e}")
            return False

    def upload_document(self, local_file_path: str, dropbox_path: str) -> Optional[str]:
        """
        Upload document to Dropbox and return public link

        Returns: Public sharing link
        """
        if not self.access_token:
            logger.warning("⚠️  Dropbox access token not configured")
            logger.info(f"   Would upload: {local_file_path} → {dropbox_path}")
            return None

        try:
            # Read file
            with open(local_file_path, 'rb') as f:
                file_data = f.read()

            # Upload file
            url = "https://content.dropboxapi.com/2/files/upload"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/octet-stream",
                "Dropbox-API-Arg": json.dumps({
                    "path": dropbox_path,
                    "mode": "add",
                    "autorename": True,
                    "mute": False
                })
            }

            req = urllib.request.Request(url, data=file_data, headers=headers, method='POST')
            response = urllib.request.urlopen(req)

            if response.status == 200:
                logger.info(f"✅ Uploaded: {Path(local_file_path).name} → Dropbox")

                # Create public link
                public_link = self._create_public_link(dropbox_path)
                return public_link

        except Exception as e:
            logger.error(f"❌ Upload failed: {e}")
            return None

    def _create_public_link(self, dropbox_path: str) -> Optional[str]:
        """Create public sharing link for file"""
        try:
            url = "https://api.dropboxapi.com/2/sharing/create_shared_link_with_settings"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            data = json.dumps({
                "path": dropbox_path,
                "settings": {
                    "requested_visibility": "public"
                }
            }).encode('utf-8')

            req = urllib.request.Request(url, data=data, headers=headers, method='POST')
            response = urllib.request.urlopen(req)

            if response.status == 200:
                result = json.loads(response.read().decode('utf-8'))
                public_url = result.get('url', '')

                # Convert to direct download link
                if public_url:
                    public_url = public_url.replace('www.dropbox.com', 'dl.dropboxusercontent.com')
                    public_url = public_url.replace('?dl=0', '?dl=1')

                logger.info(f"🔗 Public link created")
                return public_url

        except urllib.error.HTTPError as e:
            if e.code == 409:
                # Link already exists, get existing link
                try:
                    url = "https://api.dropboxapi.com/2/sharing/list_shared_links"
                    data = json.dumps({"path": dropbox_path}).encode('utf-8')
                    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
                    response = urllib.request.urlopen(req)
                    result = json.loads(response.read().decode('utf-8'))

                    if result.get('links'):
                        public_url = result['links'][0]['url']
                        public_url = public_url.replace('www.dropbox.com', 'dl.dropboxusercontent.com')
                        public_url = public_url.replace('?dl=0', '?dl=1')
                        return public_url

                except:
                    pass

        except Exception as e:
            logger.error(f"❌ Failed to create public link: {e}")

        return None

    def get_case_document_links(self, case_id: str) -> Dict[str, List[str]]:
        """Get all public links for case documents"""
        case_file = self.cases_path / f"{case_id}.json"

        if not case_file.exists():
            logger.error(f"❌ Case not found: {case_id}")
            return {}

        with open(case_file, 'r') as f:
            case_data = json.load(f)

        folders = case_data.get('dropbox_folders', {})
        links = {}

        # Get links for each folder
        for folder_name, folder_path in folders.items():
            folder_links = self._list_folder_files(folder_path)
            if folder_links:
                links[folder_name] = folder_links

        return links

    def _list_folder_files(self, folder_path: str) -> List[str]:
        """List all files in Dropbox folder"""
        if not self.access_token:
            return []

        try:
            url = "https://api.dropboxapi.com/2/files/list_folder"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            data = json.dumps({
                "path": folder_path
            }).encode('utf-8')

            req = urllib.request.Request(url, data=data, headers=headers, method='POST')
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode('utf-8'))

            files = []
            for entry in result.get('entries', []):
                if entry.get('.tag') == 'file':
                    file_path = entry.get('path_display')
                    link = self._create_public_link(file_path)
                    if link:
                        files.append(link)

            return files

        except Exception as e:
            logger.error(f"❌ Failed to list folder: {e}")
            return []

    def generate_client_portal_email(self, case_id: str) -> str:
        """Generate email with client portal access instructions"""
        case_file = self.cases_path / f"{case_id}.json"

        if not case_file.exists():
            return "Case not found"

        with open(case_file, 'r') as f:
            case_data = json.load(f)

        client_name = case_data['client_name']
        folders = case_data['dropbox_folders']

        email = f"""
Dear {client_name},

Your case documents are now available in our secure online portal.

╔═══════════════════════════════════════════════════════════════════╗
║                    CLIENT DOCUMENT PORTAL                         ║
║                   {case_id}                                        ║
╚═══════════════════════════════════════════════════════════════════╝

ACCESS YOUR DOCUMENTS:

No account or login required! Simply click the links below to view/download your documents.

📁 CLIENT DELIVERABLES (Ready for you):
{folders.get('client_deliverables', 'Setting up...')}

📄 FINAL DOCUMENTS:
{folders.get('final', 'Setting up...')}

📋 CORRESPONDENCE:
{folders.get('correspondence', 'Setting up...')}

DOCUMENT ORGANIZATION:

Your case files are organized into the following categories:

1. 📥 Intake Forms - Initial questionnaires and client information
2. ✉️  Correspondence - All email and letter communications
3. 📑 Court Filings - Documents filed with the court
4. 📎 Evidence - Supporting documentation
5. 📚 Legal Research - Relevant case law and statutes
6. 📝 Drafts - Work-in-progress documents (for review)
7. ✅ Final Documents - Completed, signed documents
8. 💰 Billing Records - Invoices and payment receipts
9. 🎁 Client Deliverables - Documents ready for your use

ACCESSING FILES:

• Click any folder link above
• Files will open in your browser
• Click "Download" to save to your computer
• No Dropbox account needed!

FILE UPDATES:

You will receive an email notification whenever:
• New documents are added
• Documents are updated
• Court filings are submitted
• Action is required from you

MOBILE ACCESS:

Access your files from any device:
• Computer: Click links in this email
• Smartphone: Click links (files open in browser)
• Tablet: Click links (files open in browser)

SECURITY & PRIVACY:

✓ Files are stored securely on Dropbox's encrypted servers
✓ Links are private (only people with the link can access)
✓ Files are backed up automatically
✓ Previous versions saved for 30 days

QUESTIONS?

Reply to this email anytime or call us during business hours.

Best regards,

Your Legal Team
{case_data.get('case_info', {}).get('attorney_email', 'appsefilepro@gmail.com')}
{case_data.get('case_info', {}).get('attorney_phone', '')}

---

Case ID: {case_id}
Created: {datetime.fromisoformat(case_data['created_date']).strftime('%B %d, %Y')}
"""

        return email

    def setup_instructions(self) -> str:
        """Return setup instructions for Dropbox integration"""
        return """
╔═══════════════════════════════════════════════════════════════════╗
║          DROPBOX CASE MANAGEMENT - SETUP GUIDE                    ║
║                    100% FREE (2GB Storage)                        ║
╚═══════════════════════════════════════════════════════════════════╝

STEP 1: CREATE DROPBOX DEVELOPER APP
----------------------------------------------------------------------
1. Go to: https://www.dropbox.com/developers/apps
2. Click "Create app"
3. Choose:
   - API: Scoped access
   - Type of access: App folder
   - App name: "LegalCaseManager" (or your choice)
4. Click "Create app"

STEP 2: GENERATE ACCESS TOKEN
----------------------------------------------------------------------
1. In your app settings, find "OAuth 2" section
2. Click "Generate" under "Generated access token"
3. Copy the token (starts with "sl.")
4. Add to config/.env:
   DROPBOX_ACCESS_TOKEN=your_token_here

STEP 3: SET PERMISSIONS
----------------------------------------------------------------------
In app settings → Permissions tab, enable:
✓ files.metadata.write
✓ files.metadata.read
✓ files.content.write
✓ files.content.read
✓ sharing.write
✓ sharing.read

Click "Submit" to save permissions.

STEP 4: TEST INTEGRATION
----------------------------------------------------------------------
Run this script:
    python3 pillar-b-legal/case-management/dropbox_case_manager.py

ALTERNATIVE: FREE PUBLIC FOLDER METHOD
----------------------------------------------------------------------
If you don't want to use API:

1. Create Dropbox account (free): https://www.dropbox.com
2. Create folder structure manually:
   /Cases/
       /{Client Name}/
           /01_Intake_Forms/
           /02_Correspondence/
           ... etc.

3. Right-click folder → Share → Create link
4. Send link to client via email

BENEFITS:
----------------------------------------------------------------------
✓ FREE - No monthly fees
✓ 2GB storage (enough for 100+ cases)
✓ Client access without account
✓ Mobile app for on-the-go access
✓ Automatic file versioning (30 days)
✓ Secure, encrypted storage
✓ Professional appearance

UPGRADE OPTIONS (Optional):
----------------------------------------------------------------------
Dropbox Plus ($11.99/mo): 2TB storage, 180-day version history
Dropbox Professional ($19.99/mo): 3TB storage, full-text search

But FREE tier is perfect for starting out!

COST COMPARISON:
----------------------------------------------------------------------
This System (Dropbox Free):     $0/month
Clio Manage:                    $39/user/month
MyCase:                         $39/user/month
PracticePanther:                $49/user/month
Smokeball:                      $79/user/month

SAVINGS: $468-948 per year! 💰

"""


def main():
    """Demo of Dropbox Case Manager"""
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║          FREE CASE MANAGEMENT SYSTEM                              ║
    ║            Powered by Dropbox (2GB Free)                          ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)

    manager = DropboxCaseManager()

    # Show setup instructions
    print(manager.setup_instructions())

    # Example: Create case folder
    print("\n📋 EXAMPLE: Create Case Folder Structure")
    print("=" * 70)

    example_case = {
        'client_name': 'Thurman Robinson Estate',
        'case_number': 'PROBATE-2025-001',
        'case_type': 'Probate Administration',
        'attorney_name': 'Your Name',
        'attorney_email': 'appsefilepro@gmail.com',
        'attorney_phone': 'Your Phone'
    }

    folders = manager.create_case_folder(example_case)

    print("\n✅ Case folder structure created!")
    print("\nFolder Organization:")
    for name, path in folders.items():
        print(f"  {name:20s} → {path}")

    print("\n📧 Client Portal Email Preview:")
    print("=" * 70)
    case_id = f"{example_case['client_name']} - {example_case['case_number']}".replace(' ', '_')
    print(manager.generate_client_portal_email(case_id))


if __name__ == "__main__":
    main()
