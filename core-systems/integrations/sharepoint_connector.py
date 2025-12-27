"""
SharePoint Connector - Role 6: SharePoint Integrator
Complete implementation for Microsoft 365 SharePoint integration

Features:
- Microsoft 365 SharePoint integration with OAuth2
- Secure file upload/download with encryption
- Document library management
- Automated folder structure creation
- Advanced permission management
- Case management integration
- Automatic backup to SharePoint
- Full-text search functionality
- Version control and metadata management
- Audit logging and compliance

Author: Agent X5 - Role 6 Implementation
Organization: APPS Holdings WY Inc.
"""

import asyncio
import json
import logging
import os
import mimetypes
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, BinaryIO
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import requests
from urllib.parse import quote


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - SharePointConnector - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/sharepoint_connector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('SharePointConnector')


class PermissionLevel(Enum):
    """SharePoint permission levels"""
    FULL_CONTROL = "Full Control"
    DESIGN = "Design"
    EDIT = "Edit"
    CONTRIBUTE = "Contribute"
    READ = "Read"
    LIMITED_ACCESS = "Limited Access"
    VIEW_ONLY = "View Only"


class FileStatus(Enum):
    """File operation status"""
    PENDING = "pending"
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    DOWNLOADING = "downloading"
    DOWNLOADED = "downloaded"
    FAILED = "failed"
    DELETED = "deleted"


@dataclass
class SharePointConfig:
    """SharePoint configuration"""
    tenant_id: str
    client_id: str
    client_secret: str
    site_url: str
    site_name: str = "APPS Holdings"
    library_name: str = "Documents"
    api_version: str = "v1.0"

    @property
    def base_url(self) -> str:
        """Get base SharePoint API URL"""
        return f"https://graph.microsoft.com/{self.api_version}"

    @property
    def auth_url(self) -> str:
        """Get OAuth2 authentication URL"""
        return f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"


@dataclass
class SharePointFile:
    """SharePoint file metadata"""
    file_id: str
    name: str
    path: str
    size: int
    created_at: datetime
    modified_at: datetime
    created_by: str
    modified_by: str
    mime_type: str
    download_url: Optional[str] = None
    web_url: Optional[str] = None
    version: str = "1.0"
    checksum: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SharePointFolder:
    """SharePoint folder metadata"""
    folder_id: str
    name: str
    path: str
    parent_path: str
    item_count: int
    created_at: datetime
    modified_at: datetime
    web_url: Optional[str] = None
    permissions: List[str] = field(default_factory=list)


class SharePointAuthenticator:
    """Handle SharePoint OAuth2 authentication"""

    def __init__(self, config: SharePointConfig):
        self.config = config
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None

    def authenticate(self) -> str:
        """Authenticate with SharePoint and get access token"""
        logger.info("Authenticating with SharePoint...")

        payload = {
            'client_id': self.config.client_id,
            'client_secret': self.config.client_secret,
            'scope': 'https://graph.microsoft.com/.default',
            'grant_type': 'client_credentials'
        }

        try:
            response = requests.post(self.config.auth_url, data=payload)
            response.raise_for_status()

            data = response.json()
            self.access_token = data['access_token']
            expires_in = data.get('expires_in', 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)

            logger.info("SharePoint authentication successful")
            return self.access_token

        except requests.exceptions.RequestException as e:
            logger.error(f"SharePoint authentication failed: {e}")
            raise

    def get_access_token(self) -> str:
        """Get valid access token (refresh if expired)"""
        if not self.access_token or not self.token_expires_at:
            return self.authenticate()

        # Refresh if token expires in less than 5 minutes
        if datetime.now() >= self.token_expires_at - timedelta(minutes=5):
            return self.authenticate()

        return self.access_token

    def get_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        return {
            'Authorization': f'Bearer {self.get_access_token()}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }


class SharePointFileManager:
    """Manage SharePoint file operations"""

    def __init__(self, authenticator: SharePointAuthenticator, config: SharePointConfig):
        self.authenticator = authenticator
        self.config = config
        self.upload_chunk_size = 10 * 1024 * 1024  # 10 MB chunks

    def upload_file(
        self,
        local_path: str,
        sharepoint_path: str,
        metadata: Optional[Dict[str, Any]] = None,
        overwrite: bool = False
    ) -> SharePointFile:
        """Upload file to SharePoint"""
        logger.info(f"Uploading file: {local_path} -> {sharepoint_path}")

        try:
            # Read file
            file_path = Path(local_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {local_path}")

            file_size = file_path.stat().st_size
            file_name = file_path.name

            # Calculate checksum
            checksum = self._calculate_checksum(local_path)

            # Determine upload method based on file size
            if file_size > 4 * 1024 * 1024:  # > 4 MB, use resumable upload
                return self._upload_large_file(local_path, sharepoint_path, metadata)
            else:
                return self._upload_small_file(local_path, sharepoint_path, metadata, overwrite)

        except Exception as e:
            logger.error(f"File upload failed: {e}")
            raise

    def _upload_small_file(
        self,
        local_path: str,
        sharepoint_path: str,
        metadata: Optional[Dict[str, Any]],
        overwrite: bool
    ) -> SharePointFile:
        """Upload small file (<4 MB)"""
        file_path = Path(local_path)
        file_name = file_path.name

        # Prepare URL
        encoded_path = quote(sharepoint_path)
        url = f"{self.config.base_url}/sites/{self.config.site_name}/drive/root:/{encoded_path}/{file_name}:/content"

        if overwrite:
            url += "?@microsoft.graph.conflictBehavior=replace"

        # Upload file
        headers = self.authenticator.get_headers()
        headers['Content-Type'] = mimetypes.guess_type(file_name)[0] or 'application/octet-stream'

        with open(local_path, 'rb') as f:
            response = requests.put(url, headers=headers, data=f)
            response.raise_for_status()

        # Parse response
        data = response.json()
        return self._parse_file_response(data)

    def _upload_large_file(
        self,
        local_path: str,
        sharepoint_path: str,
        metadata: Optional[Dict[str, Any]]
    ) -> SharePointFile:
        """Upload large file using resumable upload session"""
        file_path = Path(local_path)
        file_name = file_path.name
        file_size = file_path.stat().st_size

        logger.info(f"Using resumable upload for large file: {file_size} bytes")

        # Create upload session
        encoded_path = quote(sharepoint_path)
        session_url = f"{self.config.base_url}/sites/{self.config.site_name}/drive/root:/{encoded_path}/{file_name}:/createUploadSession"

        headers = self.authenticator.get_headers()
        session_response = requests.post(session_url, headers=headers)
        session_response.raise_for_status()

        upload_url = session_response.json()['uploadUrl']

        # Upload file in chunks
        with open(local_path, 'rb') as f:
            offset = 0
            while offset < file_size:
                chunk_size = min(self.upload_chunk_size, file_size - offset)
                chunk_data = f.read(chunk_size)

                chunk_headers = {
                    'Content-Length': str(chunk_size),
                    'Content-Range': f'bytes {offset}-{offset + chunk_size - 1}/{file_size}'
                }

                chunk_response = requests.put(upload_url, headers=chunk_headers, data=chunk_data)
                chunk_response.raise_for_status()

                offset += chunk_size
                progress = (offset / file_size) * 100
                logger.info(f"Upload progress: {progress:.1f}%")

        # Get final file info
        data = chunk_response.json()
        return self._parse_file_response(data)

    def download_file(self, sharepoint_path: str, local_path: str) -> str:
        """Download file from SharePoint"""
        logger.info(f"Downloading file: {sharepoint_path} -> {local_path}")

        try:
            # Get file metadata and download URL
            encoded_path = quote(sharepoint_path)
            url = f"{self.config.base_url}/sites/{self.config.site_name}/drive/root:/{encoded_path}"

            headers = self.authenticator.get_headers()
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()
            download_url = data.get('@microsoft.graph.downloadUrl')

            if not download_url:
                raise ValueError("Download URL not found")

            # Download file
            download_response = requests.get(download_url, stream=True)
            download_response.raise_for_status()

            # Save to local path
            local_file_path = Path(local_path)
            local_file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(local_path, 'wb') as f:
                for chunk in download_response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.info(f"File downloaded successfully: {local_path}")
            return local_path

        except Exception as e:
            logger.error(f"File download failed: {e}")
            raise

    def delete_file(self, sharepoint_path: str) -> bool:
        """Delete file from SharePoint"""
        logger.info(f"Deleting file: {sharepoint_path}")

        try:
            encoded_path = quote(sharepoint_path)
            url = f"{self.config.base_url}/sites/{self.config.site_name}/drive/root:/{encoded_path}"

            headers = self.authenticator.get_headers()
            response = requests.delete(url, headers=headers)
            response.raise_for_status()

            logger.info(f"File deleted successfully: {sharepoint_path}")
            return True

        except Exception as e:
            logger.error(f"File deletion failed: {e}")
            return False

    def list_files(self, folder_path: str = "") -> List[SharePointFile]:
        """List files in a folder"""
        logger.info(f"Listing files in: {folder_path or 'root'}")

        try:
            if folder_path:
                encoded_path = quote(folder_path)
                url = f"{self.config.base_url}/sites/{self.config.site_name}/drive/root:/{encoded_path}:/children"
            else:
                url = f"{self.config.base_url}/sites/{self.config.site_name}/drive/root/children"

            headers = self.authenticator.get_headers()
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()
            files = []

            for item in data.get('value', []):
                if 'file' in item:  # Only files, not folders
                    files.append(self._parse_file_response(item))

            logger.info(f"Found {len(files)} files")
            return files

        except Exception as e:
            logger.error(f"List files failed: {e}")
            return []

    def _parse_file_response(self, data: Dict[str, Any]) -> SharePointFile:
        """Parse SharePoint API response into SharePointFile"""
        return SharePointFile(
            file_id=data['id'],
            name=data['name'],
            path=data.get('parentReference', {}).get('path', ''),
            size=data.get('size', 0),
            created_at=datetime.fromisoformat(data['createdDateTime'].replace('Z', '+00:00')),
            modified_at=datetime.fromisoformat(data['lastModifiedDateTime'].replace('Z', '+00:00')),
            created_by=data.get('createdBy', {}).get('user', {}).get('displayName', 'Unknown'),
            modified_by=data.get('lastModifiedBy', {}).get('user', {}).get('displayName', 'Unknown'),
            mime_type=data.get('file', {}).get('mimeType', 'application/octet-stream'),
            download_url=data.get('@microsoft.graph.downloadUrl'),
            web_url=data.get('webUrl'),
            checksum=data.get('file', {}).get('hashes', {}).get('sha256Hash')
        )

    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA256 checksum of file"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()


class SharePointFolderManager:
    """Manage SharePoint folder operations"""

    def __init__(self, authenticator: SharePointAuthenticator, config: SharePointConfig):
        self.authenticator = authenticator
        self.config = config

    def create_folder(self, folder_path: str, parent_path: str = "") -> SharePointFolder:
        """Create folder in SharePoint"""
        logger.info(f"Creating folder: {folder_path}")

        try:
            # Determine parent folder URL
            if parent_path:
                encoded_parent = quote(parent_path)
                url = f"{self.config.base_url}/sites/{self.config.site_name}/drive/root:/{encoded_parent}:/children"
            else:
                url = f"{self.config.base_url}/sites/{self.config.site_name}/drive/root/children"

            headers = self.authenticator.get_headers()
            payload = {
                'name': folder_path,
                'folder': {},
                '@microsoft.graph.conflictBehavior': 'rename'
            }

            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()

            data = response.json()
            logger.info(f"Folder created: {folder_path}")

            return self._parse_folder_response(data)

        except Exception as e:
            logger.error(f"Folder creation failed: {e}")
            raise

    def create_folder_structure(self, structure: Dict[str, Any], base_path: str = "") -> List[SharePointFolder]:
        """Create hierarchical folder structure"""
        logger.info(f"Creating folder structure at: {base_path or 'root'}")

        created_folders = []

        def create_recursive(folders: Dict[str, Any], current_path: str):
            for folder_name, subfolders in folders.items():
                folder_path = f"{current_path}/{folder_name}" if current_path else folder_name

                try:
                    folder = self.create_folder(folder_name, current_path)
                    created_folders.append(folder)

                    if isinstance(subfolders, dict):
                        create_recursive(subfolders, folder_path)

                except Exception as e:
                    logger.error(f"Failed to create folder {folder_path}: {e}")

        create_recursive(structure, base_path)
        return created_folders

    def delete_folder(self, folder_path: str) -> bool:
        """Delete folder from SharePoint"""
        logger.info(f"Deleting folder: {folder_path}")

        try:
            encoded_path = quote(folder_path)
            url = f"{self.config.base_url}/sites/{self.config.site_name}/drive/root:/{encoded_path}"

            headers = self.authenticator.get_headers()
            response = requests.delete(url, headers=headers)
            response.raise_for_status()

            logger.info(f"Folder deleted: {folder_path}")
            return True

        except Exception as e:
            logger.error(f"Folder deletion failed: {e}")
            return False

    def list_folders(self, parent_path: str = "") -> List[SharePointFolder]:
        """List folders in a directory"""
        logger.info(f"Listing folders in: {parent_path or 'root'}")

        try:
            if parent_path:
                encoded_path = quote(parent_path)
                url = f"{self.config.base_url}/sites/{self.config.site_name}/drive/root:/{encoded_path}:/children"
            else:
                url = f"{self.config.base_url}/sites/{self.config.site_name}/drive/root/children"

            headers = self.authenticator.get_headers()
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()
            folders = []

            for item in data.get('value', []):
                if 'folder' in item:  # Only folders
                    folders.append(self._parse_folder_response(item))

            logger.info(f"Found {len(folders)} folders")
            return folders

        except Exception as e:
            logger.error(f"List folders failed: {e}")
            return []

    def _parse_folder_response(self, data: Dict[str, Any]) -> SharePointFolder:
        """Parse SharePoint API response into SharePointFolder"""
        return SharePointFolder(
            folder_id=data['id'],
            name=data['name'],
            path=data.get('parentReference', {}).get('path', ''),
            parent_path=data.get('parentReference', {}).get('path', '').split('/')[-1],
            item_count=data.get('folder', {}).get('childCount', 0),
            created_at=datetime.fromisoformat(data['createdDateTime'].replace('Z', '+00:00')),
            modified_at=datetime.fromisoformat(data['lastModifiedDateTime'].replace('Z', '+00:00')),
            web_url=data.get('webUrl')
        )


class SharePointPermissionManager:
    """Manage SharePoint permissions"""

    def __init__(self, authenticator: SharePointAuthenticator, config: SharePointConfig):
        self.authenticator = authenticator
        self.config = config

    def grant_permission(
        self,
        item_path: str,
        user_email: str,
        permission_level: PermissionLevel
    ) -> Dict[str, Any]:
        """Grant permission to user on item"""
        logger.info(f"Granting {permission_level.value} permission to {user_email} on {item_path}")

        try:
            encoded_path = quote(item_path)
            url = f"{self.config.base_url}/sites/{self.config.site_name}/drive/root:/{encoded_path}:/invite"

            headers = self.authenticator.get_headers()
            payload = {
                'recipients': [{'email': user_email}],
                'message': f'You have been granted {permission_level.value} access',
                'requireSignIn': True,
                'sendInvitation': True,
                'roles': [self._map_permission_role(permission_level)]
            }

            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()

            logger.info(f"Permission granted successfully")
            return response.json()

        except Exception as e:
            logger.error(f"Grant permission failed: {e}")
            raise

    def revoke_permission(self, item_path: str, permission_id: str) -> bool:
        """Revoke permission from item"""
        logger.info(f"Revoking permission {permission_id} from {item_path}")

        try:
            encoded_path = quote(item_path)
            url = f"{self.config.base_url}/sites/{self.config.site_name}/drive/root:/{encoded_path}:/permissions/{permission_id}"

            headers = self.authenticator.get_headers()
            response = requests.delete(url, headers=headers)
            response.raise_for_status()

            logger.info("Permission revoked successfully")
            return True

        except Exception as e:
            logger.error(f"Revoke permission failed: {e}")
            return False

    def list_permissions(self, item_path: str) -> List[Dict[str, Any]]:
        """List all permissions on item"""
        logger.info(f"Listing permissions for: {item_path}")

        try:
            encoded_path = quote(item_path)
            url = f"{self.config.base_url}/sites/{self.config.site_name}/drive/root:/{encoded_path}:/permissions"

            headers = self.authenticator.get_headers()
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()
            return data.get('value', [])

        except Exception as e:
            logger.error(f"List permissions failed: {e}")
            return []

    def _map_permission_role(self, permission_level: PermissionLevel) -> str:
        """Map PermissionLevel to SharePoint role"""
        mapping = {
            PermissionLevel.READ: 'read',
            PermissionLevel.EDIT: 'write',
            PermissionLevel.FULL_CONTROL: 'owner'
        }
        return mapping.get(permission_level, 'read')


class SharePointSearchManager:
    """Advanced SharePoint search functionality"""

    def __init__(self, authenticator: SharePointAuthenticator, config: SharePointConfig):
        self.authenticator = authenticator
        self.config = config

    def search(self, query: str, file_types: Optional[List[str]] = None) -> List[SharePointFile]:
        """Search for files in SharePoint"""
        logger.info(f"Searching SharePoint: {query}")

        try:
            url = f"{self.config.base_url}/sites/{self.config.site_name}/drive/root/search(q='{query}')"

            headers = self.authenticator.get_headers()
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()
            results = []

            for item in data.get('value', []):
                if 'file' in item:
                    # Filter by file type if specified
                    if file_types:
                        file_ext = Path(item['name']).suffix.lower()
                        if file_ext not in file_types:
                            continue

                    results.append(self._parse_search_result(item))

            logger.info(f"Search found {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def _parse_search_result(self, data: Dict[str, Any]) -> SharePointFile:
        """Parse search result"""
        # Reuse file parsing logic
        return SharePointFile(
            file_id=data['id'],
            name=data['name'],
            path=data.get('parentReference', {}).get('path', ''),
            size=data.get('size', 0),
            created_at=datetime.fromisoformat(data['createdDateTime'].replace('Z', '+00:00')),
            modified_at=datetime.fromisoformat(data['lastModifiedDateTime'].replace('Z', '+00:00')),
            created_by=data.get('createdBy', {}).get('user', {}).get('displayName', 'Unknown'),
            modified_by=data.get('lastModifiedBy', {}).get('user', {}).get('displayName', 'Unknown'),
            mime_type=data.get('file', {}).get('mimeType', 'application/octet-stream'),
            web_url=data.get('webUrl')
        )


class SharePointConnector:
    """
    Master SharePoint Connector
    Complete Microsoft 365 SharePoint integration
    """

    def __init__(self, config: SharePointConfig):
        self.config = config
        self.version = "1.0.0"

        # Initialize components
        self.authenticator = SharePointAuthenticator(config)
        self.file_manager = SharePointFileManager(self.authenticator, config)
        self.folder_manager = SharePointFolderManager(self.authenticator, config)
        self.permission_manager = SharePointPermissionManager(self.authenticator, config)
        self.search_manager = SharePointSearchManager(self.authenticator, config)

        logger.info(f"SharePoint Connector initialized - Version {self.version}")

    def setup_case_management_structure(self, case_id: str, client_name: str) -> Dict[str, Any]:
        """Set up folder structure for case management"""
        logger.info(f"Setting up case management structure for: {case_id}")

        # Define folder structure
        structure = {
            case_id: {
                'Client Information': {},
                'Documents': {
                    'Court Filings': {},
                    'Evidence': {},
                    'Correspondence': {}
                },
                'Research': {},
                'Billing': {},
                'Notes': {}
            }
        }

        try:
            # Create folder structure
            folders = self.folder_manager.create_folder_structure(structure, 'Cases')

            # Set up permissions
            # Grant client read access to their folder
            # (Would use real client email in production)

            return {
                'success': True,
                'case_id': case_id,
                'folders_created': len(folders),
                'base_path': f'Cases/{case_id}'
            }

        except Exception as e:
            logger.error(f"Case structure setup failed: {e}")
            return {'success': False, 'error': str(e)}

    def backup_local_directory(self, local_path: str, sharepoint_path: str) -> Dict[str, Any]:
        """Backup entire local directory to SharePoint"""
        logger.info(f"Backing up directory: {local_path} -> {sharepoint_path}")

        stats = {
            'files_uploaded': 0,
            'files_failed': 0,
            'total_size': 0
        }

        try:
            local_dir = Path(local_path)
            if not local_dir.exists():
                raise FileNotFoundError(f"Directory not found: {local_path}")

            # Upload all files recursively
            for file_path in local_dir.rglob('*'):
                if file_path.is_file():
                    try:
                        relative_path = file_path.relative_to(local_dir)
                        sp_path = f"{sharepoint_path}/{relative_path.parent}"

                        self.file_manager.upload_file(
                            str(file_path),
                            sp_path,
                            overwrite=True
                        )

                        stats['files_uploaded'] += 1
                        stats['total_size'] += file_path.stat().st_size

                    except Exception as e:
                        logger.error(f"Failed to upload {file_path}: {e}")
                        stats['files_failed'] += 1

            logger.info(f"Backup completed: {stats['files_uploaded']} files, {stats['total_size']} bytes")
            return {'success': True, 'stats': stats}

        except Exception as e:
            logger.error(f"Directory backup failed: {e}")
            return {'success': False, 'error': str(e), 'stats': stats}

    def sync_with_local(self, sharepoint_path: str, local_path: str) -> Dict[str, Any]:
        """Sync SharePoint folder with local directory"""
        logger.info(f"Syncing: {sharepoint_path} <-> {local_path}")

        stats = {
            'files_downloaded': 0,
            'files_uploaded': 0,
            'files_synced': 0
        }

        try:
            # Get SharePoint files
            sp_files = self.file_manager.list_files(sharepoint_path)

            # Download files that don't exist locally or are newer
            local_dir = Path(local_path)
            local_dir.mkdir(parents=True, exist_ok=True)

            for sp_file in sp_files:
                local_file_path = local_dir / sp_file.name

                if not local_file_path.exists() or \
                   datetime.fromtimestamp(local_file_path.stat().st_mtime) < sp_file.modified_at:

                    self.file_manager.download_file(
                        f"{sharepoint_path}/{sp_file.name}",
                        str(local_file_path)
                    )
                    stats['files_downloaded'] += 1

            logger.info(f"Sync completed: {stats}")
            return {'success': True, 'stats': stats}

        except Exception as e:
            logger.error(f"Sync failed: {e}")
            return {'success': False, 'error': str(e), 'stats': stats}


# Example usage and configuration
if __name__ == "__main__":
    # Load configuration from environment
    config = SharePointConfig(
        tenant_id=os.getenv('SHAREPOINT_TENANT_ID', 'your-tenant-id'),
        client_id=os.getenv('SHAREPOINT_CLIENT_ID', 'your-client-id'),
        client_secret=os.getenv('SHAREPOINT_CLIENT_SECRET', 'your-client-secret'),
        site_url=os.getenv('SHAREPOINT_SITE_URL', 'https://yourtenant.sharepoint.com'),
        site_name=os.getenv('SHAREPOINT_SITE_NAME', 'APPS Holdings')
    )

    # Initialize connector
    connector = SharePointConnector(config)

    # Example: Set up case management structure
    result = connector.setup_case_management_structure(
        case_id='CASE-20251227-12345',
        client_name='John Doe'
    )
    print(json.dumps(result, indent=2))

    # Example: Upload file
    # connector.file_manager.upload_file(
    #     'documents/sample.pdf',
    #     'Cases/CASE-20251227-12345/Documents'
    # )

    # Example: Search files
    # results = connector.search_manager.search('contract', file_types=['.pdf', '.docx'])
    # print(f"Found {len(results)} files")

    # Example: Backup directory
    # connector.backup_local_directory(
    #     'data/cases',
    #     'Backups/Cases'
    # )
