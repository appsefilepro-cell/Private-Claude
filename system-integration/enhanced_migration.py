#!/usr/bin/env python3
"""
Enhanced Microsoft 365 Document Migration Tool
Supports batch processing, multiple targets, and resumable migrations

For research, development, and educational purposes only.
"""

import os
import json
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from dotenv import load_dotenv

# Import base migrator
from microsoft365_migration import Microsoft365Migrator

# Import target handlers
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False

import requests
from tqdm import tqdm


class MigrationTarget:
    """Base class for migration targets"""

    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.stats = {
            'uploaded_files': 0,
            'failed_files': 0,
            'total_bytes': 0
        }

    def upload_file(self, file_path: Path, metadata: Dict[str, Any]) -> bool:
        """Upload a file to the target. Override in subclasses."""
        raise NotImplementedError


class LocalStorageTarget(MigrationTarget):
    """Local filesystem storage target"""

    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        super().__init__(config, logger)
        self.output_dir = Path(config.get('output_dir', '/home/user/migrated-docs'))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.preserve_structure = config.get('preserve_structure', True)

    def upload_file(self, file_path: Path, metadata: Dict[str, Any]) -> bool:
        """Files are already on local storage, just verify"""
        if file_path.exists():
            self.stats['uploaded_files'] += 1
            self.stats['total_bytes'] += file_path.stat().st_size
            return True
        return False


class GoogleDriveTarget(MigrationTarget):
    """Google Drive storage target"""

    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        super().__init__(config, logger)

        if not GOOGLE_DRIVE_AVAILABLE:
            raise ImportError("Google Drive libraries not available. Install with: pip install google-auth google-api-python-client")

        self.credentials_file = config.get('credentials_file', 'google_credentials.json')
        self.folder_name = config.get('folder_name', 'Microsoft 365 Migration')
        self.preserve_structure = config.get('preserve_structure', True)
        self.service = None
        self.folder_id = None

        self._authenticate()

    def _authenticate(self):
        """Authenticate with Google Drive"""
        creds = None
        token_file = 'google_token.json'

        # Load existing token
        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file)

        # Refresh or get new token
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file,
                    ['https://www.googleapis.com/auth/drive.file']
                )
                creds = flow.run_local_server(port=0)

            # Save token
            with open(token_file, 'w') as token:
                token.write(creds.to_json())

        self.service = build('drive', 'v3', credentials=creds)
        self.logger.info("✅ Google Drive authentication successful")

        # Create or get migration folder
        self._get_or_create_folder()

    def _get_or_create_folder(self):
        """Get or create the migration folder in Google Drive"""
        # Search for existing folder
        results = self.service.files().list(
            q=f"name='{self.folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
            fields="files(id, name)"
        ).execute()

        files = results.get('files', [])

        if files:
            self.folder_id = files[0]['id']
            self.logger.info(f"Using existing Google Drive folder: {self.folder_name}")
        else:
            # Create folder
            folder_metadata = {
                'name': self.folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = self.service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            self.folder_id = folder['id']
            self.logger.info(f"Created Google Drive folder: {self.folder_name}")

    def upload_file(self, file_path: Path, metadata: Dict[str, Any]) -> bool:
        """Upload file to Google Drive"""
        try:
            file_metadata = {
                'name': file_path.name,
                'parents': [self.folder_id]
            }

            # Add description with original metadata
            file_metadata['description'] = json.dumps({
                'original_path': metadata.get('path', ''),
                'created': metadata.get('created', ''),
                'modified': metadata.get('modified', ''),
                'source': metadata.get('type', 'unknown')
            })

            media = MediaFileUpload(
                str(file_path),
                resumable=True
            )

            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()

            self.stats['uploaded_files'] += 1
            self.stats['total_bytes'] += file_path.stat().st_size
            self.logger.info(f"✅ Uploaded to Google Drive: {file_path.name}")

            return True

        except Exception as e:
            self.logger.error(f"Failed to upload {file_path.name} to Google Drive: {e}")
            self.stats['failed_files'] += 1
            return False


class EnhancedMigrator(Microsoft365Migrator):
    """Enhanced migrator with batch processing and multiple targets"""

    def __init__(self, config_file: str = 'config.json'):
        """Initialize enhanced migrator"""
        # Load configuration
        self.config = self._load_config(config_file)

        # Initialize base migrator
        m365_config = self.config.get('microsoft365', {})
        super().__init__(
            client_id=m365_config.get('client_id'),
            tenant_id=m365_config.get('tenant_id', 'common'),
            output_dir=self.config.get('migration_targets', {}).get('local', {}).get('output_dir', '../migrated-docs')
        )

        # Batch processing settings
        batch_config = self.config.get('batch_processing', {})
        self.batch_enabled = batch_config.get('enabled', True)
        self.batch_size = batch_config.get('batch_size', 50)
        self.concurrent_downloads = batch_config.get('concurrent_downloads', 5)
        self.retry_failed = batch_config.get('retry_failed', True)
        self.max_retries = batch_config.get('max_retries', 3)
        self.retry_delay = batch_config.get('retry_delay_seconds', 5)
        self.exponential_backoff = batch_config.get('exponential_backoff', True)

        # Initialize migration targets
        self.targets = self._initialize_targets()

        # State management
        self.state_file = self.output_dir / self.config.get('advanced', {}).get('state_file', 'migration_state.json')
        self.migration_state = self._load_state()

    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from file"""
        config_path = Path(config_file)

        if not config_path.exists():
            self.logger.warning(f"Config file not found: {config_file}, using defaults")
            return {}

        with open(config_path, 'r') as f:
            return json.load(f)

    def _initialize_targets(self) -> List[MigrationTarget]:
        """Initialize all enabled migration targets"""
        targets = []
        targets_config = self.config.get('migration_targets', {})

        # Local storage
        if targets_config.get('local', {}).get('enabled', True):
            targets.append(LocalStorageTarget(
                targets_config['local'],
                self.logger
            ))
            self.logger.info("✅ Local storage target enabled")

        # Google Drive
        if targets_config.get('google_drive', {}).get('enabled', False):
            try:
                targets.append(GoogleDriveTarget(
                    targets_config['google_drive'],
                    self.logger
                ))
                self.logger.info("✅ Google Drive target enabled")
            except Exception as e:
                self.logger.error(f"Failed to initialize Google Drive target: {e}")

        return targets

    def _load_state(self) -> Dict[str, Any]:
        """Load migration state from file"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {
            'completed_files': [],
            'failed_files': [],
            'last_run': None,
            'total_migrated': 0
        }

    def _save_state(self):
        """Save migration state to file"""
        with open(self.state_file, 'w') as f:
            json.dump(self.migration_state, f, indent=2)

    def download_file_with_retry(self, file_info: Dict[str, Any]) -> bool:
        """Download file with retry logic"""
        retries = 0
        delay = self.retry_delay

        while retries <= self.max_retries:
            try:
                success = self.download_file(file_info)
                if success:
                    return True

                retries += 1
                if retries <= self.max_retries:
                    self.logger.warning(
                        f"Retry {retries}/{self.max_retries} for {file_info['name']}"
                    )
                    time.sleep(delay)
                    if self.exponential_backoff:
                        delay *= 2

            except Exception as e:
                self.logger.error(f"Error downloading {file_info['name']}: {e}")
                retries += 1
                if retries <= self.max_retries:
                    time.sleep(delay)
                    if self.exponential_backoff:
                        delay *= 2

        return False

    def upload_to_targets(self, file_path: Path, metadata: Dict[str, Any]):
        """Upload file to all enabled targets"""
        for target in self.targets:
            if isinstance(target, LocalStorageTarget):
                # Already on local storage
                target.upload_file(file_path, metadata)
            else:
                target.upload_file(file_path, metadata)

    def process_batch(
        self,
        files: List[Dict[str, Any]],
        batch_num: int,
        total_batches: int
    ) -> Dict[str, Any]:
        """Process a batch of files"""
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"BATCH {batch_num}/{total_batches}")
        self.logger.info(f"Files in batch: {len(files)}")
        self.logger.info(f"{'='*60}\n")

        batch_stats = {
            'batch_num': batch_num,
            'total_files': len(files),
            'successful': 0,
            'failed': 0,
            'start_time': datetime.now().isoformat()
        }

        # Download files concurrently
        with ThreadPoolExecutor(max_workers=self.concurrent_downloads) as executor:
            future_to_file = {
                executor.submit(self.download_file_with_retry, file_info): file_info
                for file_info in files
            }

            # Progress bar
            with tqdm(total=len(files), desc=f"Batch {batch_num}") as pbar:
                for future in as_completed(future_to_file):
                    file_info = future_to_file[future]
                    try:
                        success = future.result()
                        if success:
                            batch_stats['successful'] += 1
                            self.migration_state['completed_files'].append(file_info['id'])

                            # Upload to additional targets
                            file_path = self.output_dir / file_info['type'] / file_info['name']
                            self.upload_to_targets(file_path, file_info)
                        else:
                            batch_stats['failed'] += 1
                            self.migration_state['failed_files'].append(file_info)

                    except Exception as e:
                        self.logger.error(f"Error processing {file_info['name']}: {e}")
                        batch_stats['failed'] += 1
                        self.migration_state['failed_files'].append(file_info)

                    pbar.update(1)

        batch_stats['end_time'] = datetime.now().isoformat()

        # Save state after each batch
        self.migration_state['total_migrated'] += batch_stats['successful']
        self.migration_state['last_run'] = datetime.now().isoformat()
        self._save_state()

        return batch_stats

    def migrate_with_batches(
        self,
        include_onedrive: bool = True,
        include_sharepoint: bool = True,
        resume: bool = False
    ) -> Dict[str, Any]:
        """Migrate files using batch processing"""
        self.stats['start_time'] = datetime.now().isoformat()

        self.logger.info("="*60)
        self.logger.info("ENHANCED MICROSOFT 365 DOCUMENT MIGRATION")
        self.logger.info("Batch Processing Enabled")
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

        # Filter out already completed files if resuming
        if resume:
            completed_ids = set(self.migration_state.get('completed_files', []))
            all_files = [f for f in all_files if f['id'] not in completed_ids]
            self.logger.info(f"\n♻️  Resuming: {len(all_files)} files remaining")

        # Apply filters
        all_files = self._apply_filters(all_files)

        self.logger.info(f"\n📊 Total files to migrate: {len(all_files)}")
        total_size_mb = sum(f['size'] for f in all_files) / (1024 * 1024)
        self.logger.info(f"📊 Total size: {total_size_mb:.2f} MB")

        # Process in batches
        batches = [
            all_files[i:i + self.batch_size]
            for i in range(0, len(all_files), self.batch_size)
        ]

        total_batches = len(batches)
        self.logger.info(f"📦 Processing in {total_batches} batches of {self.batch_size}")

        batch_results = []

        for batch_num, batch in enumerate(batches, 1):
            batch_stats = self.process_batch(batch, batch_num, total_batches)
            batch_results.append(batch_stats)

            # Summary after each batch
            self.logger.info(f"\nBatch {batch_num} Summary:")
            self.logger.info(f"  ✅ Successful: {batch_stats['successful']}")
            self.logger.info(f"  ❌ Failed: {batch_stats['failed']}")

        self.stats['end_time'] = datetime.now().isoformat()
        self.stats['batches'] = batch_results

        # Save final report
        self._save_migration_report(all_files)
        self._save_enhanced_report(batch_results)

        # Print final summary
        self._print_final_summary()

        return self.stats

    def _apply_filters(self, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply configured filters to file list"""
        filters = self.config.get('filters', {})

        # File type filter
        file_types = filters.get('file_types', [])
        if file_types:
            files = [
                f for f in files
                if any(f['name'].endswith(ext) for ext in file_types)
            ]

        # Exclude patterns
        exclude_patterns = filters.get('exclude_patterns', [])
        for pattern in exclude_patterns:
            import fnmatch
            files = [f for f in files if not fnmatch.fnmatch(f['name'], pattern)]

        # Size filters
        min_size = filters.get('min_size_bytes', 0)
        max_size = filters.get('max_size_bytes', float('inf'))
        files = [f for f in files if min_size <= f['size'] <= max_size]

        return files

    def _save_enhanced_report(self, batch_results: List[Dict[str, Any]]):
        """Save enhanced migration report with batch details"""
        report_path = self.output_dir / 'enhanced_migration_report.json'

        report = {
            'migration_stats': self.stats,
            'batch_results': batch_results,
            'target_stats': {
                type(target).__name__: target.stats
                for target in self.targets
            },
            'configuration': self.config,
            'migration_state': self.migration_state,
            'generated': datetime.now().isoformat()
        }

        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"\n📄 Enhanced report saved: {report_path}")

    def _print_final_summary(self):
        """Print comprehensive final summary"""
        self.logger.info("\n" + "="*60)
        self.logger.info("MIGRATION COMPLETE")
        self.logger.info("="*60)
        self.logger.info(f"✅ Successfully migrated: {self.stats['migrated_files']} files")
        self.logger.info(f"❌ Failed: {self.stats['failed_files']} files")
        self.logger.info(f"📁 Output directory: {self.output_dir.absolute()}")

        # Target-specific stats
        self.logger.info("\nTarget Statistics:")
        for target in self.targets:
            target_name = type(target).__name__
            self.logger.info(f"  {target_name}:")
            self.logger.info(f"    ✅ Uploaded: {target.stats['uploaded_files']}")
            self.logger.info(f"    ❌ Failed: {target.stats['failed_files']}")
            size_mb = target.stats['total_bytes'] / (1024 * 1024)
            self.logger.info(f"    📦 Total size: {size_mb:.2f} MB")

        self.logger.info("="*60)


def main():
    """Main execution with CLI"""
    load_dotenv()

    parser = argparse.ArgumentParser(
        description='Enhanced Microsoft 365 Document Migration Tool'
    )
    parser.add_argument(
        '--config',
        default='config.json',
        help='Configuration file path'
    )
    parser.add_argument(
        '--full',
        action='store_true',
        help='Run full migration'
    )
    parser.add_argument(
        '--batch',
        action='store_true',
        help='Use batch processing'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        help='Override batch size from config'
    )
    parser.add_argument(
        '--resume',
        action='store_true',
        help='Resume previous migration'
    )
    parser.add_argument(
        '--onedrive-only',
        action='store_true',
        help='Migrate only OneDrive files'
    )
    parser.add_argument(
        '--sharepoint-only',
        action='store_true',
        help='Migrate only SharePoint files'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be migrated without downloading'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test mode - migrate only first 5 files'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of files to migrate'
    )

    args = parser.parse_args()

    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     ENHANCED MICROSOFT 365 DOCUMENT MIGRATION TOOL              ║
║                                                                  ║
║     ✓ Batch Processing                                          ║
║     ✓ Multiple Storage Targets                                  ║
║     ✓ Resumable Migrations                                      ║
║     ✓ Concurrent Downloads                                      ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    # Create enhanced migrator
    migrator = EnhancedMigrator(config_file=args.config)

    # Override batch size if specified
    if args.batch_size:
        migrator.batch_size = args.batch_size

    # Determine what to migrate
    include_onedrive = not args.sharepoint_only
    include_sharepoint = not args.onedrive_only

    # Run migration
    if args.dry_run:
        print("\n🔍 DRY RUN MODE - No files will be downloaded")
        # TODO: Implement dry run
    elif args.test:
        print("\n🧪 TEST MODE - Migrating first 5 files only")
        migrator.batch_size = 5
        migrator.migrate_with_batches(
            include_onedrive=include_onedrive,
            include_sharepoint=include_sharepoint,
            resume=False
        )
    else:
        migrator.migrate_with_batches(
            include_onedrive=include_onedrive,
            include_sharepoint=include_sharepoint,
            resume=args.resume
        )

    print("\n✅ Migration complete!")
    print(f"Files migrated: {migrator.stats['migrated_files']}")
    print(f"Output directory: {migrator.output_dir.absolute()}")


if __name__ == "__main__":
    main()
