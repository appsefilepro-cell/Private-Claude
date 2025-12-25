#!/usr/bin/env python3
"""
Microsoft 365 Document Migration Tool
Extract all documents from Microsoft 365 (OneDrive, SharePoint) and migrate to alternative storage

For research, development, and educational purposes only.
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import requests
from msal import PublicClientApplication
import time

class Microsoft365Migrator:
    """Migrate documents from Microsoft 365 to alternative storage"""

    def __init__(
        self,
        client_id: str = None,
        tenant_id: str = "common",
        output_dir: str = "../migrated-docs"
    ):
        """
        Initialize Microsoft 365 migrator

        Args:
            client_id: Azure AD application client ID
            tenant_id: Azure AD tenant ID (default: 'common' for personal accounts)
            output_dir: Directory to save migrated documents
        """
        self.client_id = client_id or os.getenv('MICROSOFT365_CLIENT_ID')
        self.tenant_id = tenant_id
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # MSAL app for authentication
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.app = PublicClientApplication(
            self.client_id,
            authority=self.authority
        ) if self.client_id else None

        # API scopes
        self.scopes = [
            "Files.Read.All",
            "Sites.Read.All",
            "User.Read"
        ]

        self.access_token = None
        self.headers = None

        # Setup logging
        self.logger = self._setup_logging()

        # Migration statistics
        self.stats = {
            'total_files': 0,
            'migrated_files': 0,
            'failed_files': 0,
            'total_size_bytes': 0,
            'start_time': None,
            'end_time': None
        }

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        log_dir = Path("../logs/system-integration")
        log_dir.mkdir(parents=True, exist_ok=True)

        logger = logging.getLogger('Microsoft365Migrator')
        logger.setLevel(logging.INFO)

        # File handler
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        fh = logging.FileHandler(
            log_dir / f'microsoft365_migration_{timestamp}.log'
        )
        fh.setLevel(logging.INFO)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)

        return logger

    def authenticate(self) -> bool:
        """
        Authenticate with Microsoft 365 using device code flow
        Returns True if successful
        """
        if not self.app:
            self.logger.error("Client ID not configured")
            return False

        try:
            # Check for cached token
            accounts = self.app.get_accounts()
            if accounts:
                self.logger.info("Found cached account, attempting silent authentication")
                result = self.app.acquire_token_silent(self.scopes, account=accounts[0])
                if result and "access_token" in result:
                    self.access_token = result["access_token"]
                    self.headers = {
                        "Authorization": f"Bearer {self.access_token}",
                        "Content-Type": "application/json"
                    }
                    self.logger.info("✅ Silent authentication successful")
                    return True

            # Device code flow for interactive authentication
            self.logger.info("Starting device code authentication flow")
            flow = self.app.initiate_device_flow(scopes=self.scopes)

            if "user_code" not in flow:
                self.logger.error("Failed to create device flow")
                return False

            print("\n" + "="*60)
            print("MICROSOFT 365 AUTHENTICATION REQUIRED")
            print("="*60)
            print(flow["message"])
            print("="*60 + "\n")

            # Wait for user to authenticate
            result = self.app.acquire_token_by_device_flow(flow)

            if "access_token" in result:
                self.access_token = result["access_token"]
                self.headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                }
                self.logger.info("✅ Authentication successful")
                return True
            else:
                self.logger.error(f"Authentication failed: {result.get('error_description')}")
                return False

        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            return False

    def get_onedrive_files(self, folder_path: str = None) -> List[Dict[str, Any]]:
        """
        Get all files from OneDrive

        Args:
            folder_path: Optional specific folder path (e.g., '/Documents')

        Returns:
            List of file metadata dictionaries
        """
        if not self.headers:
            self.logger.error("Not authenticated")
            return []

        try:
            # Microsoft Graph API endpoint
            if folder_path:
                url = f"https://graph.microsoft.com/v1.0/me/drive/root:{folder_path}:/children"
            else:
                url = "https://graph.microsoft.com/v1.0/me/drive/root/children"

            files = []
            while url:
                response = requests.get(url, headers=self.headers)

                if response.status_code != 200:
                    self.logger.error(f"Failed to get files: {response.status_code} - {response.text}")
                    break

                data = response.json()
                items = data.get('value', [])

                for item in items:
                    if 'file' in item:  # It's a file, not a folder
                        files.append({
                            'id': item['id'],
                            'name': item['name'],
                            'size': item['size'],
                            'download_url': item.get('@microsoft.graph.downloadUrl'),
                            'path': item.get('parentReference', {}).get('path', ''),
                            'created': item.get('createdDateTime'),
                            'modified': item.get('lastModifiedDateTime'),
                            'type': 'onedrive'
                        })
                        self.stats['total_files'] += 1
                        self.stats['total_size_bytes'] += item['size']
                    elif 'folder' in item:  # It's a folder, recurse
                        folder_files = self.get_onedrive_files(
                            f"{item.get('parentReference', {}).get('path', '')}/{item['name']}"
                        )
                        files.extend(folder_files)

                # Handle pagination
                url = data.get('@odata.nextLink')

            return files

        except Exception as e:
            self.logger.error(f"Error getting OneDrive files: {e}")
            return []

    def get_sharepoint_files(self, site_id: str = None) -> List[Dict[str, Any]]:
        """
        Get all files from SharePoint

        Args:
            site_id: SharePoint site ID (if None, gets all accessible sites)

        Returns:
            List of file metadata dictionaries
        """
        if not self.headers:
            self.logger.error("Not authenticated")
            return []

        try:
            files = []

            # Get all sites if site_id not specified
            if not site_id:
                sites_url = "https://graph.microsoft.com/v1.0/sites?search=*"
                sites_response = requests.get(sites_url, headers=self.headers)

                if sites_response.status_code != 200:
                    self.logger.error(f"Failed to get sites: {sites_response.status_code}")
                    return []

                sites = sites_response.json().get('value', [])

                # Get files from each site
                for site in sites:
                    site_files = self._get_site_files(site['id'])
                    files.extend(site_files)
            else:
                files = self._get_site_files(site_id)

            return files

        except Exception as e:
            self.logger.error(f"Error getting SharePoint files: {e}")
            return []

    def _get_site_files(self, site_id: str) -> List[Dict[str, Any]]:
        """Get all files from a specific SharePoint site"""
        files = []

        try:
            # Get document libraries
            libraries_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives"
            libraries_response = requests.get(libraries_url, headers=self.headers)

            if libraries_response.status_code != 200:
                return []

            libraries = libraries_response.json().get('value', [])

            # Get files from each library
            for library in libraries:
                drive_id = library['id']
                items_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/root/children"

                while items_url:
                    items_response = requests.get(items_url, headers=self.headers)

                    if items_response.status_code != 200:
                        break

                    data = items_response.json()
                    items = data.get('value', [])

                    for item in items:
                        if 'file' in item:
                            files.append({
                                'id': item['id'],
                                'name': item['name'],
                                'size': item['size'],
                                'download_url': item.get('@microsoft.graph.downloadUrl'),
                                'path': item.get('parentReference', {}).get('path', ''),
                                'created': item.get('createdDateTime'),
                                'modified': item.get('lastModifiedDateTime'),
                                'type': 'sharepoint',
                                'site_id': site_id,
                                'drive_id': drive_id
                            })
                            self.stats['total_files'] += 1
                            self.stats['total_size_bytes'] += item['size']

                    items_url = data.get('@odata.nextLink')

            return files

        except Exception as e:
            self.logger.error(f"Error getting site files: {e}")
            return []

    def download_file(self, file_info: Dict[str, Any]) -> bool:
        """
        Download a single file

        Args:
            file_info: File metadata dictionary

        Returns:
            True if successful
        """
        try:
            download_url = file_info.get('download_url')
            if not download_url:
                self.logger.warning(f"No download URL for {file_info['name']}")
                return False

            # Create subdirectory based on source
            source_dir = self.output_dir / file_info['type']
            source_dir.mkdir(parents=True, exist_ok=True)

            # Download file
            response = requests.get(download_url, stream=True)

            if response.status_code != 200:
                self.logger.error(
                    f"Failed to download {file_info['name']}: {response.status_code}"
                )
                self.stats['failed_files'] += 1
                return False

            # Save file
            file_path = source_dir / file_info['name']

            # Handle duplicate names
            counter = 1
            while file_path.exists():
                stem = Path(file_info['name']).stem
                suffix = Path(file_info['name']).suffix
                file_path = source_dir / f"{stem}_{counter}{suffix}"
                counter += 1

            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            self.logger.info(f"✅ Downloaded: {file_info['name']} ({file_info['size']} bytes)")
            self.stats['migrated_files'] += 1

            # Save metadata
            metadata_path = file_path.with_suffix(file_path.suffix + '.metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(file_info, f, indent=2)

            return True

        except Exception as e:
            self.logger.error(f"Error downloading {file_info['name']}: {e}")
            self.stats['failed_files'] += 1
            return False

    def migrate_all(
        self,
        include_onedrive: bool = True,
        include_sharepoint: bool = True
    ) -> Dict[str, Any]:
        """
        Migrate all documents from Microsoft 365

        Args:
            include_onedrive: Include OneDrive files
            include_sharepoint: Include SharePoint files

        Returns:
            Migration statistics dictionary
        """
        self.stats['start_time'] = datetime.now().isoformat()

        self.logger.info("="*60)
        self.logger.info("MICROSOFT 365 DOCUMENT MIGRATION")
        self.logger.info("For research, development, and educational purposes")
        self.logger.info("="*60)

        # Authenticate
        if not self.authenticate():
            self.logger.error("Authentication failed")
            return self.stats

        all_files = []

        # Get OneDrive files
        if include_onedrive:
            self.logger.info("\n📂 Scanning OneDrive...")
            onedrive_files = self.get_onedrive_files()
            all_files.extend(onedrive_files)
            self.logger.info(f"Found {len(onedrive_files)} files in OneDrive")

        # Get SharePoint files
        if include_sharepoint:
            self.logger.info("\n📂 Scanning SharePoint...")
            sharepoint_files = self.get_sharepoint_files()
            all_files.extend(sharepoint_files)
            self.logger.info(f"Found {len(sharepoint_files)} files in SharePoint")

        self.logger.info(f"\n📊 Total files to migrate: {len(all_files)}")
        total_size_mb = self.stats['total_size_bytes'] / (1024 * 1024)
        self.logger.info(f"📊 Total size: {total_size_mb:.2f} MB")

        # Download all files
        self.logger.info("\n⬇️  Starting download...\n")

        for i, file_info in enumerate(all_files, 1):
            self.logger.info(f"[{i}/{len(all_files)}] Downloading: {file_info['name']}")
            self.download_file(file_info)

            # Rate limiting
            time.sleep(0.1)

        self.stats['end_time'] = datetime.now().isoformat()

        # Save migration report
        self._save_migration_report(all_files)

        # Print summary
        self.logger.info("\n" + "="*60)
        self.logger.info("MIGRATION COMPLETE")
        self.logger.info("="*60)
        self.logger.info(f"✅ Successfully migrated: {self.stats['migrated_files']} files")
        self.logger.info(f"❌ Failed: {self.stats['failed_files']} files")
        self.logger.info(f"📁 Output directory: {self.output_dir.absolute()}")
        self.logger.info("="*60)

        return self.stats

    def _save_migration_report(self, files: List[Dict[str, Any]]):
        """Save detailed migration report"""
        report_path = self.output_dir / 'migration_report.json'

        report = {
            'statistics': self.stats,
            'files': files,
            'output_directory': str(self.output_dir.absolute()),
            'generated': datetime.now().isoformat()
        }

        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"\n📄 Migration report saved: {report_path}")

        # Also save CSV for easy viewing
        csv_path = self.output_dir / 'migration_report.csv'
        with open(csv_path, 'w') as f:
            f.write("Name,Size,Type,Created,Modified,Status\n")
            for file_info in files:
                f.write(
                    f"{file_info['name']},"
                    f"{file_info['size']},"
                    f"{file_info['type']},"
                    f"{file_info.get('created', 'N/A')},"
                    f"{file_info.get('modified', 'N/A')},"
                    f"Migrated\n"
                )

        self.logger.info(f"📄 CSV report saved: {csv_path}")


def main():
    """Main execution"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     MICROSOFT 365 DOCUMENT MIGRATION TOOL                       ║
║                                                                  ║
║     Extracts all documents from OneDrive and SharePoint         ║
║     For research, development, and educational purposes         ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    # Check for client ID
    client_id = os.getenv('MICROSOFT365_CLIENT_ID')

    if not client_id:
        print("\n⚠️  SETUP REQUIRED")
        print("="*60)
        print("To use this tool, you need to register an Azure AD application:")
        print()
        print("1. Go to: https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps")
        print("2. Click 'New registration'")
        print("3. Name: 'Document Migration Tool'")
        print("4. Supported account types: 'Personal Microsoft accounts only'")
        print("5. Redirect URI: Leave blank (we use device code flow)")
        print("6. Click 'Register'")
        print("7. Copy the 'Application (client) ID'")
        print("8. Set environment variable:")
        print("   export MICROSOFT365_CLIENT_ID='your-client-id'")
        print()
        print("9. Configure API permissions:")
        print("   - Microsoft Graph → Delegated → Files.Read.All")
        print("   - Microsoft Graph → Delegated → Sites.Read.All")
        print("   - Microsoft Graph → Delegated → User.Read")
        print("="*60)
        return

    # Create migrator
    migrator = Microsoft365Migrator(client_id=client_id)

    # Run migration
    stats = migrator.migrate_all(
        include_onedrive=True,
        include_sharepoint=True
    )

    print("\n✅ Migration complete!")
    print(f"Files migrated: {stats['migrated_files']}")
    print(f"Output directory: {migrator.output_dir.absolute()}")


if __name__ == "__main__":
    main()
